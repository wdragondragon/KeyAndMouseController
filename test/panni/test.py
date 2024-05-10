# -*- coding: utf-8 -*-

'''
说明：该版本无依赖库，未经严格测试
2023/12/1 修复64位python无法连接的问题
2023/12/1 优化连接方法，方式卡住
'''
from pykm2 import i_KM
import time

km = i_KM()
ret = km.OpenDevice()
if not ret:
    print("设备未连接")
else:
    print("设备已连接")
    print("型号:", chr(km.GetModel() + 64))
    print("版本:", km.GetVersion())
    print("序列号:", km.GetChipID())
    print("空间大小:", km.GetStorageSize())
    km.SetWaitRespon(True)

    print("测试鼠标...")
    for y in range(300, 305):
        for x in range(300, 600):
            km.MoveTo(x, y)
    km.MoveD(100, 100)
    km.MoveD(500, 100)
    km.MoveD(500, 500)
    km.MoveD(100, 500)
    km.MoveD(100, 100)
    time.sleep(1)

    print("测试键盘...")
    km.KeyDownName("Win")
    km.KeyPressName("R", 10, 50)
    km.KeyUpName("Win")
    time.sleep(0.6)
    km.SayString("Cmd", 1, 10)
    km.KeyPressVirtualCode(13)
    time.sleep(0.6)
    km.SayString("ipconfig /flushdns", 1, 10)
    km.KeyPressCode(40)
    time.sleep(0.3)
    km.SayStringAnsi("echo 测试中文！")
    km.KeyPressCode(40)

    '''
    print("测试配置区读写...")
    km.SetConfigData(1,12345)
    print("SetConfigData 1=12345")
    ret=km.GetConfigData(1)
    print("GetConfigData 1="+ret)
    '''

    print("测试led灯...")
    for i in range(0, 9):
        km.SetLed(i % 2)
        time.sleep(0.5)

    print("测试锁定...")
    print("禁止鼠标横向移动...")
    km.Lock_Mouse(8)
    time.sleep(1)
    print("禁止鼠标纵向移动...")
    km.Lock_Mouse(16)
    time.sleep(1)
    print("取消鼠标锁定")
    km.Lock_Mouse(0)

    print("测试捕获...")
    print("捕获鼠标所有动作...")
    km.Notify_Mouse(63)
    begin_time = time.time()
    while time.time() < begin_time + 3:
        ret = km.Read_Notify(10)
        if ret:
            print(ret)
    print("取消鼠标捕获")
    km.Notify_Mouse(0)
