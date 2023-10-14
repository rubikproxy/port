import paramiko
import threading
import os
import hashlib
import getpass

host = 'localhost'
port = 2222

server = paramiko.Transport((host, port))

private_key_path = 'C:/Users/admin/.ssh/my_ssh_key'

try:
    private_key = paramiko.RSAKey(filename=private_key_path)
except FileNotFoundError:
    print(f"Private key file not found at '{private_key_path}'")
    exit(1)

users = {
    'rubikproxy': 'admin',
    'admin': 'admin',
    # Add more username/password hashes as needed
}

home_directories = {
    'rubikproxy': 'C:/Users/rubik proxy',
    'admin': 'C:/Users/admin',
    # Add more home directories as needed
}


active_sessions = {}


recorded_sessions = {}


last_command = {}

allowed_commands = ['ls', 'pwd', 'cd', 'mkdir', 'touch', 'rm', 'mv']

def hash_password(password):

    return hashlib.sha256(password.encode()).hexdigest()

def create_user():
    username = input("Enter the new username: ")
    if username in users:
        print("User already exists.")
        return
    password = getpass.getpass("Enter the password: ")
    users[username] = hash_password(password)
    print(f"User {username} created.")

def handle_client(client):
    session = server.accept(20)
    if session is None:
        return
    channel = session.accept(20)
    username = session.get_username()
    home_dir = home_directories.get(username, '/tmp')

    while channel.active:
        try:
            command = input(f"{username}@ssh-server:{home_dir}$ ")

            if command.startswith('record'):
                session_id = command.split(' ')[-1]
                if session_id in recorded_sessions:
                    print(f"Playback session {session_id}:")
                    playback_session(client, recorded_sessions[session_id])
                else:
                    print(f"Session {session_id} not found.")
            elif command.startswith('createuser'):
                create_user()
            elif command in allowed_commands:
                channel.send(command + '\n')
                response = channel.recv(4096).decode('utf-8')
                print(response.strip())
                last_command[username] = command
            else:
                print("Command not allowed.")
        except KeyboardInterrupt:
            channel.close()
            session.close()
            if recorded_sessions.get(username) is not None:
                recorded_sessions[username].close()
            return

def playback_session(client, recorded_session):
    client_transport = paramiko.Transport(client)
    recorded_session_transport = recorded_session.accept(event=threading.Event())
    recorded_channel = recorded_session_transport.accept(event=threading.Event())

    while recorded_channel.active:
        recorded_output = recorded_channel.recv(4096).decode('utf-8')
        print(recorded_output, end='')

def record_session(client):
    session = server.accept(20)
    username = session.get_username()
    recorded_sessions[username] = paramiko.Transport(None)
    recorded_session_transport = recorded_sessions[username]
    recorded_session_transport.add_server_key(private_key)
    recorded_session_transport.start_server(event=threading.Event())
    recorded_channel = recorded_session_transport.accept(event=threading.Event())
    active_sessions[username] = session

    while active_sessions[username].is_active():
        recorded_input = channel.recv(4096).decode('utf-8')
        recorded_channel.send(recorded_input)
        active_sessions[username].recv(4096)

    recorded_channel.close()
    recorded_session_transport.close()
    del recorded_sessions[username]
    del active_sessions[username]


try:
    server.add_server_key(private_key)
    server.start_server()
    print(f"SSH server is running on {host}:{port}")

    while True:
        client, addr = server.accept(20)
        if client is not None:
            threading.Thread(target=handle_client, args=(client,)).start()
            threading.Thread(target=record_session, args=(client,)).start()

except KeyboardInterrupt:
    print("\nSSH server stopped.")

finally:
    server.close()
