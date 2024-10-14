from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

# Create a new FastAPI app
app = FastAPI()

# Allow CORS for development purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

socket_app = socketio.ASGIApp(sio)

# In-memory storage for squares
squares = []


@app.post("/spawn_square")
async def spawn_square():
    square = {"id": len(squares), "position": "bottom-left"}
    squares.append(square)
    await sio.emit("new_square", [square])
    return {"message": "Square spawned"}


@sio.event
async def connect(sid, environ):
    print("Client connected:", sid)
    # await sio.emit("new_square", squares, room=sid)


@sio.event
async def disconnect(sid):
    print("Client disconnected:", sid)


# Mount the Socket.IO app on the FastAPI app
app.mount("/", socket_app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
