import socket
import threading

# Predefined users and their passwords
users = {"user1": "password1", "user2": "password2"}

# Dictionary to track online users (username: socket)
online_users = {}

def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                # Client disconnected
                for username, sock in list(online_users.items()):
                    if sock == client_socket:
                        del online_users[username]
                        print(f"{username} disconnected")
                        break
                client_socket.close()
                break

            parts = message.split()
            command = parts[0]

            if command == "LOGIN":
                username = parts[1]
                password = parts[2]
                if username in users and users[username] == password:
                    online_users[username] = client_socket
                    client_socket.send("LOGIN_SUCCESS".encode())
                    print(f"{username} logged in")
                else:
                    client_socket.send("LOGIN_FAILED".encode())
            elif command == "MESSAGE":
                target_username = parts[1]
                message_content = " ".join(parts[2:])
                if target_username in online_users:
                    sender_username = [k for k, v in online_users.items() if v == client_socket][0]
                    online_users[target_username].send(f"MESSAGE_FROM {sender_username} {message_content}".encode())
                else:
                    client_socket.send("ERROR target user not online".encode())
            elif command == "LOGOUT":
                for username, sock in list(online_users.items()):
                    if sock == client_socket:
                        del online_users[username]
                        print(f"{username} logged out")
                        break
                client_socket.close()
                break
        except Exception as e:
            print(f"Error: {e}")
            break

# Server setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 5000))
server_socket.listen(5)
print("Server listening on port 5000")

while True:
    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr}")
    threading.Thread(target=handle_client, args=(client_socket,)).start()