from generator import Generator
from config import Config


def chooseItem(url, lst, config: Config):
    if type(lst) is not list:
        return lst
    textSource = Generator(url, config)
    return textSource.chooseItem(lst)


def get_html(url, config: Config):
    text_source = Generator(url, config)  # Create new generator instance with random seed based on current url
    res = template
    title = text_source.unescapePageName(url)
    # Replace static text
    # every occurrence of {TITLE} will be replaced with the same text
    res = res.replace("{TITLE}", title)
    res = res.replace("{UPTITLE}", text_source.getParentPageName(url))
    res = res.replace("{MAIN}", text_source.getMainHTML(url))
    res = res.replace("{UP}", text_source.getParentLink(url))
    res = res.replace("{CSSLINK}", text_source.chooseItem(config.css_dir) + text_source.getLink())

    # Slightly hacky code for giving
    # `<div><a href="{LINK}">{NEWTITLE}</a></div>`
    # elements a url to match their title text
    while "{NEWTITLE}" in res:
        #segment = res[:res.index("{NEWTITLE}")]
        title_pos = res.index("{NEWTITLE}")
        title = text_source.getTitle()

        segment=res

        link_pos = segment.rfind("{LINK}", 0, title_pos)
        over_pos = segment.rfind("{OVER}", 0, title_pos)

        if link_pos != -1 or over_pos != -1:  # Give the closest {LINK} or {OVER} tag a title
            if link_pos > over_pos:
                # Substituting a {LINK} tag
                link = text_source.getLinkForTitle(title)
                segment = segment[link_pos:title_pos].replace("{LINK}", link, 1)
            else:
                # Substituting an {OVER} tag
                over_link = text_source.getSiblingForTitle(url, title)
                segment = segment[over_pos:title_pos].replace("{OVER}", over_link, 1)

            #res = segment + res[res.index("{NEWTITLE}"):]
            tag_pos=max(link_pos, over_pos)
            #print("seg=",segment)
            res = res[0:tag_pos] + segment + res[title_pos:]
            #print("res=",res)
            res = res.replace("{NEWTITLE}", title, 1)
            #print(res)


    # Dynamic text substitution
    # each occurrence of {WORD} will be replaced with its own random words
    for i in ["{WORD}", "{NEWTITLE}", "{PIC}", "{SENTENCE}", "{LINK}", "{OVER}", "{NAME}"]:
        while i in res:
            # print("replacing",i)
            res = res.replace("{WORD}", text_source.getWord(), 1)
            res = res.replace("{NEWTITLE}", text_source.getTitle(), 1)
            res = res.replace("{PIC}", text_source.chooseItem(config.image_dir) + text_source.getLink(), 1)
            res = res.replace("{SENTENCE}", text_source.getSentence(), 1)
            res = res.replace("{LINK}", text_source.getLink(), 1)
            res = res.replace("{OVER}", text_source.getSiblingLink(url), 1)
            res = res.replace("{NAME}", text_source.getName(), 1)

    return res


with open("template.html") as tmp:
    template: str = tmp.read()
