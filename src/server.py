from http.server import HTTPServer
from handler import Handler
from config import Config

def run(config:Config):
    print("Listening on port {}".format(config.port))
    server_address = ('', config.port)
    httpd = HTTPServer(server_address, Handler)
    Handler.cfg = config
    httpd.serve_forever()


def main():
    config = Config()
    if config.random_seed == 0:
        print("Please update the random seed value in the config file!")
    run(config)


if __name__ == "__main__":
    main()
