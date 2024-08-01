import asyncio
import websockets


async def send_message():
    uri = "ws://192.168.2.173:8765"  # WebSocket 服务器的地址

    while True:
        try:
            async with websockets.connect(uri, ping_interval=5, ping_timeout=200) as websocket:
                print("Connected to the server.")
                while True:
                    message = input("Enter a message to send to the server: ")
                    await websocket.send(message)
                    response = await websocket.recv()
                    print(f"Received response from server: {response}")
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed unexpectedly: {e}")
        except websockets.exceptions.WebSocketException as e:
            print(f"WebSocket exception occurred: {e}")

        print("Reconnecting...")
        await asyncio.sleep(5)  # 重新连接前等待5秒


asyncio.get_event_loop().run_until_complete(send_message())
