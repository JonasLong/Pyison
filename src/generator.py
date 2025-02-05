import random

import nltk
from nltk.corpus import words, stopwords
import random as _global_rand
from config import Config
from urllib.parse import ParseResult
import posixpath as path


class Generator:
    word_list = words.words()
    stop_list = None

    def __init__(self, url: ParseResult, cfg: Config):
        # The random seed is a combination of the url hash and the global seed (salt) specified in the config
        # Using the URL means that a crawler doing a "sanity check" by re-requesting a page
        # will be given the exact same data, as if it were a static resource
        self.rnd = _global_rand.Random(hash(url.path) + int(cfg.random_seed))
        self.stop_list = Generator.get_stopwords(cfg)
        self.doc_root = cfg.doc_root
        self.spacings = cfg.spacing
        self.unsafeChars = cfg.unsafe_chars
        self.url = url

    @classmethod
    def get_stopwords(cls, cfg: Config):
        # Trim a bunch of words from the list of stop words ("wouldn", "ll", single letters)
        # as determined by the config. Otherwise, these could be a giveaway that the content is auto-generated
        if cls.stop_list is None:
            cls.stop_list = stopwords.words("english")
            for i in cfg.non_stop_wrds:
                if i in cls.stop_list:
                    cls.stop_list.remove(i)
            print("Prepared stop words list")
            # print(cls.stop_list)
        return cls.stop_list

    def debug(self):
        print(len(self.word_list))
        print(len(self.stop_list))
        print(self.rnd.choice(self.word_list))
        print(self.rnd.choice(self.stop_list))
        print(self.getHeader() + "\n" + self.getPara())

    def getBool(self):
        return self.rnd.choice([True, False])

    def getWord(self):
        # The heart of the random word generation
        # Chooses a random word from either the english dictionary or a list of english "stop words"
        # This could be replaced by something like a Markov Chain for more believable sentence structure
        return self.rnd.choice(self.word_list if self.getBool() else self.stop_list)

    def getSentence(self):
        sentence = " ".join(self.getWord() for _ in range(self.rnd.randint(3, 20)))
        return sentence.capitalize() + "."

    def getTitle(self):
        return " ".join(self.getWord() for _ in range(self.rnd.randint(1, 7)))

    def getPara(self):
        return " ".join(self.getSentence() for _ in range(self.rnd.randint(15, 20)))

    def getHeader(self):
        return " ".join(self.getWord().capitalize() for _ in range(self.rnd.randint(1, 3)))

    def getName(self):
        return (self.getWord() + " " + self.getWord()).title()

    def addLinksToText(self, url, txt: str):
        words = txt.split(" ")
        for i in range(self.rnd.randint(0, 3)):
            start = self.rnd.randint(0, len(words) - 1)
            end = min(start + self.rnd.randint(0, 4), len(words) - 1)
            words[start] = '<a href="{}">{}'.format(self.getLink(), words[start])
            words[end] = words[end] + "</a>"
        return " ".join(words)

    def getMainHTML(self):
        level = 1
        content = ""
        for i in range(self.rnd.randint(3, 25)):
            if self.getBool():
                if self.getBool():
                    level += 1
                else:
                    level -= 1
                level = (level % 4) + 1
            content += "<h{0}>{1}</h{0}>\n<p>{2}</p>\n".format(
                str(level), self.getHeader(), self.addLinksToText(self.url, self.getPara()))

        # print("done content")
        return content

    def escapePageName(self, title):
        """Converts a Title into a page name to go into a URL
        ex: 'Once Upon A Time' -> 'once-upon-a-time'"""
        spacer = self.rnd.choice(self.spacings)
        return self.removeUnsafeChars(title.replace(" ", spacer)).lower()

    def unescapePageName(self):
        """Turns a URL back into a title
        ex: '/blog/about/once-upon-a-time' -> 'Once Upon A Time'"""

        url_path = self.url.path

        dirs = path.dirname(url_path)
        file = path.basename(url_path)

        if self._isDocRoot():
            # This is the Home directory
            return "Home"
        else:
            return self._reintroduceSpacingToPage(file).title()

    def _reintroduceSpacingToPage(self, url_page: str):
        title = url_page
        for i in self.spacings:
            title = title.replace(i, " ")
        return title

    def removeUnsafeChars(self, txt: str):
        for i in self.unsafeChars:
            txt = txt.replace(i, "")
        return txt

    def getParentPageName(self):
        # Returns the unescaped name of the parent url in the heiarchy

        url_path = self.url.path

        dirs = path.dirname(url_path)
        parent_file = path.basename(dirs)

        return self._reintroduceSpacingToPage(parent_file)

    def getPathForTitle(self, title):
        return path.join(self.getPath(), self.escapePageName(title))

    def getPage(self):
        return self.escapePageName(self.removeUnsafeChars(self.getTitle()))

    def getPath(self):
        return self._genUrl(self.doc_root.path)  # need doc root to provide sub-paths correctly

    def _genUrl(self, parent):
        new_url = parent
        for i in range(self.rnd.randint(1, 4)):
            new_url = path.join(new_url, self.getWord())
            # use getPage() instead of getWord() for multi-word paths
        return self.removeUnsafeChars(new_url)

    def getLink(self):
        return path.join(self.getPath(), self.getPage())

    def getSubpath(self, new_dir: str | None):
        if new_dir is None:
            return self._genUrl(self.doc_root.path)
        return self._genUrl(path.join(self.doc_root.path, new_dir))

    def getLinkForTitle(self, title: str):
        return path.join(self.getPath(), self.escapePageName(title))

    def _isDocRoot(self):
        return self.url == self.doc_root

    def getSiblingLink(self):
        parent = self.getParentLink()
        return path.join(parent, self.getPage())

    def getSiblingForTitle(self, title: str):
        return path.join(self.getParentLink(), self.escapePageName(title))

    def getParentLink(self):
        if self._isDocRoot():
            return self.url.path
        else:
            return path.dirname(self.url.path)

    def chooseItem(self, items: list | str):
        if items is None:
            return None
        elif type(items) == str:
            if len(items) == 0:
                return None
            else:
                return str
        elif len(items) == 0:
            return None
        elif len(items) == 1:
            return items[0]
        else:
            return random.choice(items)


def main():
    cfg = Config()
    g = Generator(cfg.doc_root, cfg)
    g.debug()


if __name__ == '__main__':
    # Runs a testing script
    print("start")
    nltk.download("words")
    main()
