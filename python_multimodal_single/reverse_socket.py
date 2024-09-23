import socket

# 定义服务器地址和端口
HOST = '0.0.0.0'  # 监听所有网络接口
PORT = 18888

# 创建 socket 对象
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 绑定地址和端口
server_socket.bind((HOST, PORT))

# 开始监听连接
server_socket.listen(1)
print('服务器启动，等待连接...')

try:
    # 接受客户端连接
    client_socket, addr = server_socket.accept()
    print('连接成功：', addr)

    while True:
        # 接收数据
        data = client_socket.recv(1024)
        if not data:
            print('客户端断开连接')
            break
        print('收到数据：', data.decode())

except Exception as e:
    print('发生异常：', e)

finally:
    # 关闭连接
    client_socket.close()
