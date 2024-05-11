import mimetypes
import socket
import logging
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, unquote_plus
from http.server import HTTPServer, BaseHTTPRequestHandler
from multiprocessing import Process
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

URI_DB = "mongodb://mongodb:27017"
BASE_DIR = Path(__file__).parent
CHUNK_SIZE = 1024
HTTP_PORT = 3000
SOCKET_PORT = 5000
HTTP_HOST = "0.0.0.0"
SOCKET_HOST = "127.0.0.1"


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        size = int(self.headers["Content-Length"])
        data = self.rfile.read(size)

        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.sendto(data, (SOCKET_HOST, SOCKET_PORT))
            client_socket.close()
        except socket.error:
            logging.error("Failed to send data")

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def do_GET(self):
        router = urlparse(self.path).path
        match router:
            case "/":
                self.send_html_file("index.html")
            case "/message":
                self.send_html_file("message.html")
            case _:
                file = BASE_DIR.joinpath(router[1:])
                if file.exists():
                    self.send_static()
                else:
                    self.send_html_file("error.html", 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mimetype = mimetypes.guess_type(self.path)[0] or "text/plain"
        self.send_header("Content-type", mimetype)
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


def run_http_server(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = (HTTP_HOST, HTTP_PORT)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
        logging.info(f"Server started: http://{HTTP_HOST}:{HTTP_PORT}")
    except Exception as e:
        logging.error(e)
    finally:
        logging.info("Server stopped")
        http.server_close()


def save_to_db(data):
    client = MongoClient(URI_DB, server_api=ServerApi('1'))
    db = client.python_courses
    try:
        data = unquote_plus(data)
        parse_data = dict([i.split("=") for i in data.split("&")])
        parse_data["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.messages.insert_one(parse_data)
    except Exception as e:
        logging.error(e)
    finally:
        client.close()


def run_socket_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((SOCKET_HOST, SOCKET_PORT))
    logging.info(f"Server started: socket://{SOCKET_HOST}:{SOCKET_PORT}")
    try:
        while True:
            data, addr = s.recvfrom(CHUNK_SIZE)
            logging.info(f"Received from {addr}: {data.decode()}")
            save_to_db(data.decode())
    except Exception as e:
        logging.error(e)
    finally:
        logging.info("Server socket stopped")
        s.close()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(processName)s - %(message)s"
    )
    http_server_process = Process(
        target=run_http_server,
        name="HTTP_Server"
    )
    socket_server_process = Process(
        target=run_socket_server,
        name="SOCKET_Server"
    )

    http_server_process.start()
    socket_server_process.start()

    http_server_process.join()
    socket_server_process.join()
