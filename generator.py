import random
import nltk
from nltk.corpus import words, stopwords
import random as _global_rand
from config import Config


class Generator:
    word_list = words.words()
    stop_list = None

    def __init__(self, url, cfg: Config):
        # The random seed is a combination of the url hash and the global seed (salt) specified in the config
        # Using the URL means that a crawler doing a "sanity check" by re-requesting a page
        # will be given the exact same data, as if it were a static resource
        self.rnd = _global_rand.Random(hash(url) + int(cfg.random_seed))
        self.stop_list = Generator.get_stopwords(cfg)
        self.doc_root = cfg.doc_root
        self.spacings = cfg.spacing
        self.unsafeChars = cfg.unsafe_chars

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
            #print(cls.stop_list)
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
        sentence = " ".join(self.getWord() for i in range(self.rnd.randint(3, 20)))
        return sentence.capitalize() + "."

    def getTitle(self):
        return " ".join(self.getWord() for i in range(self.rnd.randint(1, 7)))

    def getPara(self):
        return " ".join(self.getSentence() for i in range(self.rnd.randint(15, 20)))

    def getHeader(self):
        return " ".join(self.getWord().capitalize() for i in range(self.rnd.randint(1, 3)))

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

    def getMainHTML(self, url):
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
                str(level), self.getHeader(), self.addLinksToText(url, self.getPara()))

        # print("done content")
        return content

    def escapePageName(self, title):
        """Converts a Title into a page name to go into a URL
        ex: 'Once Upon A Time' -> 'once-upon-a-time'"""
        spacer = self.rnd.choice(self.spacings)
        return self.removeUnsafeChars(title.replace(" ", spacer)).lower()

    def unescapePageName(self, url: str):
        """Turns a URL back into a title
        ex: '/blog/about/once-upon-a-time' -> 'Once Upon A Time'"""
        url = url.strip("/")
        if url == "": #or url == self.doc_root: # don't use doc root- sub-path isn't Home
            return "Home"
        if "/" in url:
            url = url[url.rfind("/") + 1:]
        return self.revertURLSpacing(url.title())

    def revertURLSpacing(self, url:str):
        for i in self.spacings:
            url = url.replace(i, " ")
        return url

    def removeUnsafeChars(self, txt: str):
        for i in self.unsafeChars:
            txt = txt.replace(i, "")
        return txt

    def getParentPageName(self, url):
        return self.unescapePageName(self.getParentLink(url))

    def getPathForTitle(self, title):
        return self.getPath() + "/" + self.escapePageName(title)

    def getPage(self):
        return self.escapePageName(self.removeUnsafeChars(self.getTitle()))

    def getPath(self):
        new_url = ""
        for i in range(self.rnd.randint(1, 4)):
            new_url += self.doc_root + self.getWord() # need doc root to provide sub-paths correctly
            # new_url += self.doc_root + self.getPage() # for multi-word paths
        # new_url = new_url[:-1]
        return self.removeUnsafeChars(new_url)

    def getLink(self):
        return self.getPath() + "/" + self.getPage()

    def getLinkForTitle(self, title: str):
        return self.getPath() + "/" + self.escapePageName(title)

    def getSiblingLink(self, url: str):
        return self.getPage()

    def getParentLink(self, url: str):
        # return ".."
        url = url.strip("/")
        if "/" in url:
            # shouldn't need to reference doc root. Parent will still be a valid path,
            # just not controlled by this webserver
            page = url[:url.rfind("/")]
            return "/" + page
        else:
            return "/"

    def chooseItem(self, lst: list):
        if len(lst) == 1:
            return lst[0]
        return random.choice(lst)


def main():
    g = Generator(None, Config())
    g.debug()


if __name__ == '__main__':
    print("start")
    nltk.download("words")
    main()
