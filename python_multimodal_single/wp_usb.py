import usb.core
import usb.util

# 通过 vendor_id 和 product_id 来过滤设备，如果不需要过滤可以设为 None
vendor_id = 0x2207
product_id = 0x0017
iProduct = "0x2 LubanCat 4"
targetDevice = None
interface = None  # 将 interface 定义在 try 块之外

# 查找所有 USB 设备
devices = usb.core.find(find_all=True)

# 遍历所有设备并打印设备索引和信息
for index, device in enumerate(devices):
    # 如果指定了 vendor_id 和 product_id，就进行过滤
    if vendor_id is not None and product_id is not None:
        if device.idVendor == vendor_id:
            targetDevice = device
            print("Found matching targetDevice at index", index)
            print(device)

            # 尝试连接到目标设备
            try:
                # 设置配置
                targetDevice.set_configuration()

                # 获取第一个接口
                interface = targetDevice[0][(0, 0)]

                # Claim interface
                usb.util.claim_interface(targetDevice, interface)

                # 在一个无限循环中持续与设备通信
                while True:
                    try:
                        # 在这里可以执行与设备通信的操作
                        # 例如，可以使用 control_transfer, bulk_transfer, interrupt_transfer 等方法进行数据传输等操作
                        # 例如，可以使用 targetDevice 对象进行数据传输等操作
                        print("Communicating with the device...")

                        # 这里可以添加数据传输的逻辑

                    except usb.core.USBError as e:
                        print("USB communication error:", e)
                        break

            except usb.core.USBError as e:
                print("Error connecting to the target device:", e)

            finally:
                # 释放接口
                if interface is not None:
                    usb.util.release_interface(device, interface)

    else:
        print(device)
