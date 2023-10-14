import socket
import subprocess
import logging
import getpass
import telnetlib
from datetime import datetime
import threading


host = '0.0.0.0'  
port = 23  

log_filename = "telnet.log"
logging.basicConfig(filename=log_filename, level=logging.INFO,
                    format='%(asctime)s - %(message)s')


users = {
    'admin': 'hashed_password1',
    'user2': 'hashed_password2',
    # Add more user credentials as needed
}


user_access = {}


def log_session(username, action):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"{timestamp} - User '{username}' - {action}")


def handle_connection(client_socket):
    try:
        client_socket.send(b"Welcome to My Secure Telnet Server\nUsername: ")
        username = client_socket.recv(1024).strip()


        username = username.decode('utf-8', errors='ignore').strip()


        log_session(username, "Login attempt")

        if username in users:
            client_socket.send(b"Password: ")
            password = client_socket.recv(1024).strip()

            # Decode the received password
            password = password.decode('utf-8', errors='ignore').strip()


            if password == users[username]:
                client_socket.send(f"Welcome, {username}!\n".encode('utf-8'))


                log_session(username, "Login successful")

                # Record the user's access time
                user_access[username] = datetime.now()


                tn = telnetlib.Telnet()
                tn.sock = client_socket

                def keep_alive():
                    while True:
                        now = datetime.now()
                        last_access = user_access.get(username, now)
                        if (now - last_access).total_seconds() > 1800:  # 30 minutes in seconds
                            tn.close()
                            log_session(username, "Session closed due to inactivity")
                            return

                # Start a thread to monitor session activity
                monitor_thread = threading.Thread(target=keep_alive)
                monitor_thread.daemon = True
                monitor_thread.start()

                tn.interact()
            else:
                client_socket.send(b"Authentication failed. Closing the connection.\n")
                log_session(username, "Authentication failed")
        else:
            client_socket.send(b"Invalid username. Closing the connection.\n")
            log_session(username, "Invalid username")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

    client_socket.close()


try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)  # Listen for up to 5 incoming connections
    print(f"Telnet server is running on {host}:{port}")

    while True:
        client, addr = server.accept()
        print(f"Accepted connection from {addr[0]}:{addr[1]}")
        handle_connection(client)

except KeyboardInterrupt:
    print("\nTelnet server stopped.")

finally:
    server.close()
