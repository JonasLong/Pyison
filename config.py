import json


class Config:

    @property
    def port(self):
        return self.opts["port"]

    @property
    def random_seed(self):
        return self.opts["random-seed"]

    @property
    def spacing(self):
        return self.opts["spacing-characters"]

    @property
    def unsafe_chars(self):
        return self.opts["unsafe-characters"]

    @property
    def robots_txt(self):
        return self.opts["robots-txt"]

    @property
    def doc_root(self):
        return self.opts["document-root"]

    @property
    def non_stop_wrds(self):
        return self.opts["remove-from-stop-words"]

    @property
    def html_templates(self):
        return self.opts["html-templates"]

    @property
    def css(self):
        return self.opts["css-files"]

    @property
    def image_dir(self):
        return self.opts["fake-image-dir"]

    @property
    def css_dir(self):
        return self.opts["fake-css-dir"]

    @property
    def ico(self):
        return self.opts["images"]["ico"]

    @property
    def jpg(self):
        return self.opts["images"]["jpg"]

    @property
    def png(self):
        return self.opts["images"]["png"]

    def name_by_ext(self, ext: str):
        """Returns the value for the config value given by the string
        ex: `config_inst.name_by_ext("png")` will return the same value as `config_inst.png`"""
        return getattr(self, ext)

    def __init__(self):
        with open("config.json") as cfg:
            self.opts = json.load(cfg)
