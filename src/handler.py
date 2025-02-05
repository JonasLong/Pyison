from functools import cached_property
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qsl
from config import Config
import wrapper
from urllib.parse import urlparse, urljoin


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
        url = urlparse(self.path)
        return url

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

        if not (self.url.path.startswith(self.cfg.doc_root.path) or self.url.geturl().startswith(
                self.cfg.doc_root.path)):
            # initial URL validation checks
            print("Invalid request! Not in document root")
            self.send_response(500)
            return

        else:
            url = urlparse(self.url.geturl())
            # print('GET request for url "{}"'.format(textwrap.shorten(url, width=50)), end="- ")

            doc_root = self.cfg.doc_root

            if url == doc_root:
                # Request to the homepage, so print info about this client
                self.logCatch()
                # Continue to serve content

            url_path = url.path
            if len(url_path) > 4 and url_path[-4] == ".":
                # Handle file extensions (.txt, .jpg, etc)
                if url == urljoin(doc_root.path, "robots.txt"):
                    return self.getRobots()
                else:
                    self.getFile(url_path)
            else:
                # serve plain HTML
                self.get_html(url)

    def logCatch(self):
        print("Caught something in document root!")
        print("User-Agent:", self.headers.get("User-Agent"))
        print("IP: {}:{}".format(self.client_address[0], self.client_address[1]))
        # Can print more client specs here, or print all of headers.items()

    def getFile(self, url_path):
        # return a file
        if url_path.endswith(".ico"):
            cnt = "image/vnd.microsoft.icon"
            ext = "ico"
        elif url_path.endswith(".jpg"):
            cnt = "image/jpeg"
            ext = "jpg"
        elif url_path.endswith(".png"):
            cnt = "image/png"
            ext = "png"
        elif url_path.endswith(".css"):
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
        chosen_file = wrapper.chooseItem(self.url, file_options, Handler.getCfg())  # Choose one at random
        if chosen_file is None:
            print("Client requested a .{} file, but none was provided! Served 404".format(ext))
            self.send_response(404)
        else:
            print("served {}".format(chosen_file))
            self.wfile.write(self.load_binary(chosen_file))  # Send to client

    def getRobots(self):
        if self.cfg.robots_txt != "":
            self.send_response(200)
            self.send_header("Content-Type", "gzip")
            self.wfile.write(self.load_binary(self.cfg.robots_txt))
            return
        else:
            self.send_response(404)

    def get_html(self, url):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        # generate HTML
        # page = "<html><head></head><body>hi</body></html>"
        page = wrapper.getHtml(url, Handler.getCfg())
        print("served html with {} chars".format(len(page)))
        self.wfile.write(page.encode("utf-8"))

    def load_binary(self, filename):
        with open(filename, 'rb') as file_handle:
            return file_handle.read()
