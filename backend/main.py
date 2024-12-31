import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List, Dict

app = FastAPI()  # Create FastAPI app instance
rooms = {}  # Dictionary to store room information

async def broadcast_message(room_name: str, message: str, exclude=None):
    """
    Broadcast message to all participants in the room except the excluded one.
    """
    for participant in rooms[room_name]["participants"]:
        connection = participant["websocket"]
        if exclude and exclude == connection:
            continue
        try:
            await connection.send_text(message)
        except WebSocketDisconnect:
            rooms[room_name].remove(connection)

async def private_message(room_name: str, message: str, target):
    """
    Send private message to a specific participant in the room.
    """
    for participant in rooms[room_name]["participants"]:
        if participant["user_id"] == target:
            connection = participant["websocket"]
            try:
                await connection.send_text(message)
                return
            except WebSocketDisconnect:
                rooms[room_name].remove(connection)
                return

async def handle_offer(data, websocket):
    """
    Handle 'offer' messages by sending private message to target participant.
    """
    await private_message(data["room"], json.dumps({"type": "offer", "data": data}), data["target"])

async def handle_answer(data, websocket):
    """
    Handle 'answer' messages by sending private message to target participant.
    """
    await private_message(data["room"], json.dumps({"type": "answer", "data": data}), data["target"])
    

async def handle_icecandidate(data, websocket):
    """
    Handle 'candidate' messages by sending private message to target participant.
    """
    await private_message(data["room"], json.dumps({"type": "candidate", "data": data}), data["target"])

async def handle_join(data, websocket):
    """
    Broadcast 'join' messages to all participants in the room.
    """
    room = rooms[data["room"]]
    await broadcast_message(data["room"], json.dumps({"type": "join", "data": data}), exclude=websocket)

@app.websocket("/ws/{room_name}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_name: str, user_id: str):
    """
    WebSocket endpoint to handle client connections and messages.
    """
    await websocket.accept()
    if room_name not in rooms:
        rooms[room_name] = {"participants": []}
    rooms[room_name]["participants"].append({"user_id": user_id, "websocket": websocket})

    try:
        while True:
            try:
                data = await websocket.receive_text()
                if type(data) != str or "type" not in data or "data" not in data:
                    await websocket.close()
                    break
                data = json.loads(data)
                data["data"]["room"] = room_name
                data["data"]["user_id"] = user_id
                match data["type"]:
                    case "join":
                        await handle_join(data["data"], websocket=websocket)
                    case "offer":
                        await handle_offer(data["data"], websocket=websocket)
                    case "answer":
                        await handle_answer(data["data"], websocket=websocket)
                    case "candidate":
                        await handle_icecandidate(data["data"], websocket=websocket)
            except WebSocketDisconnect:
                break
    finally:
        room = rooms[room_name]
        for p in room["participants"]:
            if p["user_id"] == user_id:
                room["participants"].remove(p)
                await broadcast_message(room_name, json.dumps({"type": "left", "data": {"target": user_id}}))
