# Chat Application

A real-time command-line chat application developed in Python as part of the OASIS Infobyte Python Programming Internship.

## Features

* Real-time messaging between multiple clients
* Client-server communication using sockets
* Bidirectional message exchange
* Multiple clients can connect to the same server
* Threading for handling multiple clients
* Timestamped messages
* Join and leave notifications
* Graceful disconnection
* Runs locally using localhost

## Technologies Used

* Python
* Socket Programming
* Threading
* DateTime

## How It Works

The application uses a client-server architecture.

1. The server starts and listens for incoming connections.
2. Clients connect to the server using localhost.
3. Each client enters a username.
4. A separate thread handles each connected client.
5. Messages are sent through sockets.
6. The server broadcasts messages to other connected clients.
7. Timestamps are added to messages.
8. When a user leaves, other users receive a disconnection notification.

## How to Run

### Step 1: Start the Server

Open a terminal in the project folder and run:

```bash
python server.py
```

The server will start listening on:

```text
127.0.0.1:5000
```

### Step 2: Start Client 1

Open another terminal and run:

```bash
python client.py
```

Enter a username when asked.

### Step 3: Start Client 2

Open a third terminal and run:

```bash
python client.py
```

Enter another username.

Now both clients can communicate in real time.

### Leaving the Chat

Type:

```text
/quit
```

to disconnect from the chat.

## Example

```text
[14:35] Alice joined the chat.
[14:36] Bob joined the chat.
[14:36] Alice: Hello!
[14:36] Bob: Hi Alice!
[14:37] Alice left the chat.
```

## Project Structure

```text
Python-Task5-ChatApplication/
├── server.py
├── client.py
├── README.md
├── requirements.txt
└── .gitignore
```

## Internship Task

OASIS Infobyte Python Programming Internship

Task 5 - Chat Application
