import threading
import logging
import os
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# Create a custom logger
logger = logging.getLogger("my_ftp_server")
logger.setLevel(logging.INFO)
log_format = '%(asctime)s [%(levelname)s] - %(message)s'
logging.basicConfig(filename='ftp_server.log', level=logging.INFO, format=log_format)


stop_event = threading.Event()


def start_ftp_server():

    authorizer = DummyAuthorizer()

    authorizer.add_user("rubikproxy", "admin", "D:/", perm="elradfmw")

    authorizer.add_anonymous("D:/", perm="elr")  # Anonymous users can read (elr) only


    class CustomFTPHandler(FTPHandler):
        def format_list(self, basedir, listing):

            lines = []
            for (perms, _, _, _, size, modify, name) in listing:
                line = self.format_line(perms, size, modify, name)
                lines.append(line)
            return lines

        def format_line(self, perms, size, modify, name):

            return "{} 1 ftp ftp {} {} {}\r\n".format(perms, size, modify, name)

        def on_login(self, username):

            super().on_login(username)
            logger.info(f"User {username} logged in.")

        def on_file_received(self, file):

            super().on_file_received(file)
            logger.info(f"File {file.uri} received by user: {file.user.username}")

        def on_file_sent(self, file):

            super().on_file_sent(file)
            logger.info(f"File {file.uri} sent by user: {file.user.username}")


    handler = CustomFTPHandler
    handler.authorizer = authorizer


    server = FTPServer(("0.0.0.0", 21), handler)
    server.max_cons = 256
    server.max_cons_per_ip = 5


    server.passive_ports = range(60000, 65535)


    server.banner = "Welcome to My FTP Server"


    handler.max_login_attempts = 3

    handler.permit = "0.0.0.0/0"

    handler.max_login_attempts = 3


    server.serve_forever()


server_thread = threading.Thread(target=start_ftp_server)
server_thread.start()


server_thread.join()
