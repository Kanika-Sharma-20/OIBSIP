import socket
import threading
from datetime import datetime

HOST = "127.0.0.1"
PORT = 5000

clients = {}
lock = threading.Lock()


def get_time():
    return datetime.now().strftime("%H:%M")


def broadcast(message, sender=None):
    with lock:
        for client in list(clients.keys()):
            if client != sender:
                try:
                    client.send(message.encode())
                except:
                    clients.pop(client, None)


def handle_client(client_socket, address):
    try:
        name = client_socket.recv(1024).decode().strip()

        if not name:
            name = f"User-{address[1]}"

        with lock:
            clients[client_socket] = name

        join_message = f"[{get_time()}] {name} joined the chat."
        print(join_message)
        broadcast(join_message, client_socket)

        while True:
            message = client_socket.recv(1024).decode()

            if not message:
                break

            if message.lower() == "/quit":
                break

            formatted_message = f"[{get_time()}] {name}: {message}"
            print(formatted_message)
            broadcast(formatted_message, client_socket)

    except ConnectionResetError:
        pass

    finally:
        with lock:
            name = clients.pop(client_socket, "Unknown User")

        leave_message = f"[{get_time()}] {name} left the chat."
        print(leave_message)
        broadcast(leave_message)

        client_socket.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((HOST, PORT))
    server.listen()

    print("=" * 45)
    print("       OASIS CHAT APPLICATION SERVER")
    print("=" * 45)
    print(f"Server running on {HOST}:{PORT}")
    print("Waiting for clients...")
    print("Press Ctrl+C to stop the server.\n")

    try:
        while True:
            client_socket, address = server.accept()

            print(f"New connection from {address}")

            thread = threading.Thread(
                target=handle_client,
                args=(client_socket, address),
                daemon=True
            )
            thread.start()

    except KeyboardInterrupt:
        print("\nServer stopped.")

    finally:
        server.close()


if __name__ == "__main__":
    start_server()