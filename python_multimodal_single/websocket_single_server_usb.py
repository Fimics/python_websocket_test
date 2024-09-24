import asyncio
import websockets
import cv2
import numpy as np
from datetime import datetime

# unknown
SERVICE_ID_UNKNOWN = -1
# stream
SERVICE_ID_STREAM = 10001
# audio
SERVICE_ID_AUDIO = 10002
# video
SERVICE_ID_VIDEO = 10003
# info
SERVICE_ID_INFO = 10004

# 全局变量来存储最新的图像
latest_image = None
# 用于计数的全局变量和锁
frame_count = 0
frame_count_lock = asyncio.Lock()
# 全局变量，用于存储音频数据
latest_audio = None

# 控制是否显示图像
is_show_images = True
is_show_video_log = True
is_show_audio_log = True

image_event = asyncio.Event()

# 定义服务器地址和端口
HOST = 'localhost'  # 监听所有网络接口
PORT = 39999

async def display_images():
    global latest_image
    while True:
        await image_event.wait()
        if is_show_images and latest_image is not None:
            cv2.imshow('Preview', latest_image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            latest_image = None  # 重置图像
            image_event.clear()  # 重置事件状态
        await asyncio.sleep(0.01)  # 短暂休眠以允许其他协程运行


async def count_frames_per_second():
    global frame_count
    while True:
        async with frame_count_lock:
            # print(f"{datetime.now()}: 收到 {frame_count} 帧")
            frame_count = 0
        await asyncio.sleep(1)


async def echo(websocket, path):
    global latest_image, frame_count, latest_audio
    try:
        async for message in websocket:
            if isinstance(message,bytes):
                service_id = int.from_bytes(message[0:4], byteorder='big')
                if service_id == SERVICE_ID_VIDEO:
                    await process_video(message)
                elif service_id == SERVICE_ID_AUDIO:
                    await process_audio(message)
            elif isinstance(message,str):
                await process_stream(message)
            else:
                print("未知服务ID")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"连接关闭: {e}")
    except Exception as e:
        print(f"意外错误: {e}")


async def process_video(message: bytes):
    global latest_image, frame_count

    index = int.from_bytes(message[4:12], 'big', signed=True)
    data_len = int.from_bytes(message[12:16], 'big', signed=True)
    img_width = int.from_bytes(message[16:20], 'big', signed=True)
    img_height = int.from_bytes(message[20:24], 'big', signed=True)
    hasFace = bool(int.from_bytes(message[24:28], 'big'))
    faceNum = int.from_bytes(message[28:32], 'big', signed=True)
    faceIndex = int.from_bytes(message[32:40], 'big', signed=True)
    w = int.from_bytes(message[40:44], 'big', signed=True)
    h = int.from_bytes(message[44:48], 'big', signed=True)
    x = int.from_bytes(message[48:52], 'big', signed=True)
    y = int.from_bytes(message[52:56], 'big', signed=True)
    mouthW = int.from_bytes(message[56:60], 'big', signed=True)
    mouthH = int.from_bytes(message[60:64], 'big', signed=True)
    mouthX = int.from_bytes(message[64:68], 'big', signed=True)
    mouthY = int.from_bytes(message[68:72], 'big', signed=True)

    if is_show_video_log:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f""" {current_time} video ----------------->Frame Index: {index} Data Length: {data_len}""")
        print(f"""
        video ----------------->Frame Index: {index}
        Data Length: {data_len}
        Image Width: {img_width}
        Image Height: {img_height}
        Has Face: {hasFace}
        Face Number: {faceNum}
        Face Index: {faceIndex}
        W: {w}
        H: {h}
        X: {x}
        Y: {y}
        Mouth W: {mouthW}
        Mouth H: {mouthH}
        Mouth X: {mouthX}
        Mouth Y: {mouthY}
        """)

    video_data = message[72:72 + data_len]
    img_np = np.frombuffer(video_data, dtype=np.uint8).reshape((img_height, img_width, 3)).copy()

    # 如果检测到人脸，绘制边框
    # 如果检测到人脸，绘制边框
    if hasFace & faceNum>=1:
        # 人脸边框的右下角坐标
        x2 = x + w
        y2 = y + h
        # 绘制矩形
        cv2.rectangle(img_np, (x, y), (x2, y2), (0, 255, 0), 2)

    latest_image = img_np
    image_event.set()  # 触发事件，通知display_images更新图像

    async with frame_count_lock:
        frame_count += 1


async def process_audio(message: bytes):
    global latest_audio
    data_len = int.from_bytes(message[4:8], byteorder='big')
    vad_status = int.from_bytes(message[8:12], byteorder='big')
    audio_data = message[12:12 + data_len]
    latest_audio = audio_data
    # 这里可以添加音频的处理代码，例如保存到文件，或者播放等

    if is_show_audio_log:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"""{current_time} audio Frame data_len ------------------>: {data_len} audio_data_len: {len(audio_data)} """)
        print(f"""
                audio Frame data_len ------------------>: {data_len}
                vad_status: {vad_status}
                audio_data_len: {len(audio_data)}
                """)


async def process_info(message: bytes):
    data_len = int.from_bytes(message[4:8], byteorder='big')
    vad_status = int.from_bytes(message[8:12], byteorder='big')
    audio_data = message[12:12 + data_len]
    latest_audio = audio_data
    # 这里可以添加音频的处理代码，例如保存到文件，或者播放等

    if is_show_audio_log:
        print(f"""
                audio Frame data_len: {data_len}
                vad_status: {vad_status}
                audio_data_len: {len(audio_data)}
                """)


async def process_stream(message: str):
    print(message)


async def start_server():
    max_message_size = None
    server = await websockets.serve(
        echo, HOST, PORT, max_size=max_message_size)
    print(f"服务器已启动，正在监听 {HOST}:{PORT}")
    await server.wait_closed()


async def main():
    # 启动图像显示协程
    image_display_task = asyncio.create_task(display_images())
    # 启动WebSocket服务器
    server_task = asyncio.create_task(start_server())
    # 启动每秒计数器
    counter_task = asyncio.create_task(count_frames_per_second())

    await asyncio.gather(image_display_task, server_task, counter_task)

    cv2.destroyAllWindows()


asyncio.run(main())

if __name__ == "__main__":
    asyncio.run(main())
