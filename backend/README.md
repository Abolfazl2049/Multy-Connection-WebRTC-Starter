# Meet: WebRTC Socket Chat Application

This project is a WebRTC-based chat application using FastAPI and WebSockets. It supports room-based messaging with options for broadcasting messages to all participants or sending private messages.

## Features
- **Room-based messaging**: Users can join specific rooms to chat.
- **Broadcast messages**: Send messages to all participants in a room.
- **Private messages**: Send private messages to specific participants.
- **Join notifications**: Notify room participants when a new user joins.
- **Leave notifications**: Notify room participants when a user leaves.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/mohamad171/meet.git
    cd meet
    ```

2. Build the Docker image:
    ```
    docker build -t fastapi-app .
    ```

3. Run the container:
    ```
    docker run -d -p 8000:8000 --name fastapi-container fastapi-app
    ```
4. Open your browser and navigate to `http://localhost:8000` to start chatting!

## Code Explanation

### `app = FastAPI()`
Creates an instance of the FastAPI application.

### `rooms = {}`
A dictionary to store information about chat rooms and their participants.

### `broadcast_message(room_name: str, message: str, exclude=None)`
Broadcasts a message to all participants in a specified room, with an option to exclude a specific participant.

### `private_message(room_name: str, message: str, target)`
Sends a private message to a specific participant in a specified room.

### `handle_offer(data, websocket)`
Handles "offer" messages and sends them as private messages to the target participant.

### `handle_answer(data, websocket)`
Handles "answer" messages and sends them as private messages to the target participant.

### `handle_icecandidate(data, websocket)`
Handles "candidate" messages and sends them as private messages to the target participant.

### `handle_join(data, websocket)`
Broadcasts "join" messages to all participants in the specified room.

### `websocket_endpoint(websocket: WebSocket, room_name: str, user_id: str)`
The main WebSocket endpoint that handles client connections, messages, and disconnections.


## Contributing
Contributions are welcome! Please submit a pull request or open an issue to discuss any changes.

## Acknowledgements
Special thanks to the FastAPI, WebRTC, and WebSockets communities for their excellent libraries and documentation.

## Contact
For questions or comments, please reach out to [mohamadmohamadi249@gmail.com].

---

Enjoy your chatting experience with Meet!
