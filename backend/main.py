import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List, Dict

app = FastAPI()
rooms: Dict[str, List[WebSocket]] = {}

async def broadcast_message(room_name: str, message: str, exclude=None):
    for connection in rooms[room_name]:
        if exclude and exclude == connection:
            continue
        try:
            await connection.send_text(message)
        except WebSocketDisconnect:
            rooms[room_name].remove(connection)

async def handle_offer(data, websocket):
    await broadcast_message(data["room"], json.dumps({"type":"offer","data":data}), exclude=websocket)

async def handle_answer(data, websocket):
    await broadcast_message(data["room"], json.dumps({"type":"answer","data":data}), exclude=websocket)

async def handle_icecandidate(data, websocket):
    await broadcast_message(data["room"], json.dumps({"type":"ice","data":data}), exclude=websocket)

async def handle_join(data, websocket):
    await broadcast_message(data["room"], json.dumps({"type":"join","data":data}), exclude=websocket)

@app.websocket("/ws/{room_name}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_name: str):
    await websocket.accept()
    if room_name not in rooms:
        rooms[room_name] = []
    rooms[room_name].append(websocket)

    try:
        while True:
            try:
                data = await websocket.receive_text()
                if type(data) != str or "type" not in data or "data" not in data:
                    await websocket.close()
                    break
                data = json.loads(data)
                match data["type"]:
                    case "join":
                        data["data"]["room"] = room_name
                        await handle_join(data["data"], websocket=websocket)
                    case "offer":
                        await handle_offer(data["data"], websocket=websocket)
                    case "answer":
                        await handle_answer(data["data"], websocket=websocket)
                    case "ice":
                        await handle_icecandidate(data["data"], websocket=websocket)
            except WebSocketDisconnect:
                break
    finally:
        rooms[room_name].remove(websocket)
        await websocket.close()