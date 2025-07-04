import socket
import threading
import queue

# Queue for incoming messages
message_queue = queue.Queue()

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                print("Connection closed by server")
                break
            message_queue.put(message)
        except Exception as e:
            print(f"Error: {e}")
            break

# Client setup
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 5000))

# Login
username = input("Enter username: ")
password = input("Enter password: ")
client_socket.send(f"LOGIN {username} {password}".encode())

# Start receiving messages
threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

# Wait for login response
while True:
    if not message_queue.empty():
        message = message_queue.get()
        parts = message.split()
        if parts[0] == "LOGIN_SUCCESS":
            print("Login successful")
            break
        elif parts[0] == "LOGIN_FAILED":
            print("Login failed")
            client_socket.close()
            exit()

# Message sending loop
while True:
    command = input("Enter command (send/exit): ")
    if command == "send":
        target_username = input("Enter target username: ")
        message_content = input("Enter message: ")
        client_socket.send(f"MESSAGE {target_username} {message_content}".encode())
    elif command == "exit":
        client_socket.send("LOGOUT".encode())
        client_socket.close()
        break

    # Check for incoming messages
    while not message_queue.empty():
        message = message_queue.get()
        parts = message.split()
        if parts[0] == "MESSAGE_FROM":
            sender_username = parts[1]
            message_content = " ".join(parts[2:])
            print(f"{sender_username}: {message_content}")
        elif parts[0] == "ERROR":
            error_message = " ".join(parts[1:])
            print(f"Error: {error_message}")