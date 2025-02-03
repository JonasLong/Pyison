from http.server import BaseHTTPRequestHandler
from functools import cached_property
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qsl, urlparse
from config import Config
import wrapper
import textwrap


class Handler(BaseHTTPRequestHandler):
    cfg = None

    @classmethod
    def getCfg(cls):
        if cls.cfg is None:
            print("making cfg")
            cls.cfg = Config()
        return cls.cfg

    @cached_property
    def url(self):
        return urlparse(self.path)

    @cached_property
    def query_data(self):
        return dict(parse_qsl(self.url.query))

    @cached_property
    def post_data(self):
        content_length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(content_length)

    @cached_property
    def form_data(self):
        return dict(parse_qsl(self.post_data.decode("utf-8")))

    @cached_property
    def cookies(self):
        return SimpleCookie(self.headers.get("Cookie"))

    def do_POST(self):
        self.send_response(404)

    def do_DELETE(self):
        self.send_response(404)

    def do_PUT(self):
        self.send_response(404)

    def do_GET(self):
        url = self.url.geturl()
        # print('GET request for url "{}"'.format(textwrap.shorten(url, width=50)), end="- ")

        stripped = url.strip("/")

        if stripped == "" or stripped == self.cfg.doc_root:
            # Request to the homepage, so print info about this client
            self.getCatch()

        elif url.strip("/") == "robots.txt":
            if self.cfg.robots_txt != "":
                self.send_response(200)
                self.send_header("Content-Type", "gzip")
                self.wfile.write(self.load_binary(self.cfg.robots_txt))
                return
            else:
                self.send_response(404)

        if len(url) > 4 and url[-4] == ("."):
            # return a file
            if url.endswith(".ico"):
                cnt = "image/vnd.microsoft.icon"
                ext = "ico"
            elif url.endswith(".jpg"):
                cnt = "image/jpeg"
                ext = "jpg"
            elif url.endswith(".png"):
                cnt = "image/png"
                ext = "png"
            elif url.endswith(".css"):
                cnt = "text/css"
                ext = "css"
            else:
                self.send_response(404)
                print("served 404")
                return

            self.send_response(200)
            self.send_header("Content-Type", cnt)
            self.end_headers()
            file_options = Handler.getCfg().name_by_ext(ext)  # Get possible files to send from the config
            # print("options:", file_options)
            chosen_file = wrapper.chooseItem(url, file_options, Handler.getCfg())  # Choose one at random
            print("served {}".format(chosen_file))
            self.wfile.write(self.load_binary(chosen_file))  # Send to client
        else:
            self.send_response(200)
            # serve plain HTML
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(self.get_html(url).encode("utf-8"))

    def getCatch(self):
        print("Caught something in document root!")
        print("User-Agent:", self.headers.get("User-Agent"))
        print("IP: {}:{}".format(self.client_address[0], self.client_address[1]))
        # Can print more client specs here, or print all of headers.items()

    def get_html(self, url):
        # return "<html><head></head><body>hi</body></html>"
        x = wrapper.get_html(url, Handler.getCfg())
        print("served html with {} chars".format(len(x)))
        return x

    def load_binary(self, filename):
        with open(filename, 'rb') as file_handle:
            return file_handle.read()
