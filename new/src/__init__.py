from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.websockets import WebSocket, WebSocketDisconnect
from src.websockets.manager import WebSocketManager

app = FastAPI()

templates = Jinja2Templates(
    directory="templates"
)

app.mount('/static',StaticFiles(directory="static"), name="static")

manager = WebSocketManager()

@app.get('/presenter_ui')
async def root(request: Request):
    return templates.TemplateResponse(
        request,
        'presenter.html',
        {}
    )
@app.get('/')
async def root(request: Request):
    return templates.TemplateResponse(
        request,
        'audience.html',
        {}
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    while True:
        try:
            message = await websocket.receive_json()

            
            for client in manager.connected_clients:
                await manager.send_message(client, message)


        except WebSocketDisconnect:
            await manager.disconnect(websocket)
        

