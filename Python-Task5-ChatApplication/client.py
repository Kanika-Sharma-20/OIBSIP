import socket
import threading

HOST = "127.0.0.1"
PORT = 5000


def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()

            if not message:
                print("\nDisconnected from server.")
                break

            print("\n" + message)
            print("You: ", end="", flush=True)

        except:
            break


def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((HOST, PORT))

        print("=" * 45)
        print("          OASIS CHAT APPLICATION")
        print("=" * 45)

        name = input("Enter your name: ").strip()

        if not name:
            name = "User"

        client_socket.send(name.encode())

        print("\nConnected to the chat!")
        print("Type your message and press Enter.")
        print("Type /quit to leave the chat.\n")

        receive_thread = threading.Thread(
            target=receive_messages,
            args=(client_socket,),
            daemon=True
        )
        receive_thread.start()

        while True:
            message = input("You: ")

            if message.lower() == "/quit":
                client_socket.send("/quit".encode())
                print("You left the chat.")
                break

            if message.strip():
                client_socket.send(message.encode())

    except ConnectionRefusedError:
        print("\nCould not connect to the server.")
        print("Make sure server.py is running first.")

    except Exception as error:
        print(f"\nError: {error}")

    finally:
        client_socket.close()


if __name__ == "__main__":
    start_client()