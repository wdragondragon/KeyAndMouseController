# -*- coding: utf-8 -*-

from ctypes import *
import platform


class GUID(Structure):
    _fields_ = [("Data1", c_ulong),
                ("Data2", c_ushort),
                ("Data3", c_ushort),
                ("Data4", c_ubyte * 8)]


class SP_DEVICE_INTERFACE_DATA(Structure):
    _fields_ = [("cbSize", c_ulong),
                ("InterfaceClassGuid", GUID),
                ("Flags", c_ulong),
                ("Reserved", c_ulong)]


def SP_DATA_A_factory(length):
    class SP_DEVICE_INTERFACE_DETAIL_DATA_A(Structure):
        _fields_ = [("cbSize", c_ulong), ("DevicePath", c_char * (length - 4))]

    return SP_DEVICE_INTERFACE_DETAIL_DATA_A


class HID():
    def __init__(self):
        self.setupapi_dll = WinDLL("setupapi.dll")
        info_value = [c_ulong(0x4d1e55b2), c_ushort(0xf16f), c_ushort(0x11cf),
                      (c_ubyte * 8)(0x88, 0xcb, 0x00, 0x11, 0x11, 0x00, 0x00, 0x30)]
        self.InterfaceClassGuid = GUID(*info_value)
        self.handle = None
        self.setupapi_dll.SetupDiGetClassDevsA.restype = c_void_p
        self.setupapi_dll.SetupDiEnumDeviceInterfaces.argtypes = (
        c_void_p, c_void_p, POINTER(GUID), c_ulong, POINTER(SP_DEVICE_INTERFACE_DATA))

    def __del__(self):
        self.close()

    def enum_device(self):
        result = []
        device_info_set = self.setupapi_dll.SetupDiGetClassDevsA(pointer(self.InterfaceClassGuid), None, None, 0x12)
        if device_info_set != -1:
            # print(device_info_set)
            device_index = 0
            while True:
                if platform.architecture()[0] == "64bit":
                    info_value = [c_ulong(32), self.InterfaceClassGuid, 0, 0]
                else:
                    info_value = [c_ulong(28), self.InterfaceClassGuid, 0, 0]
                device_interface_data = SP_DEVICE_INTERFACE_DATA(*info_value)
                ret = self.setupapi_dll.SetupDiEnumDeviceInterfaces(device_info_set, None,
                                                                    pointer(self.InterfaceClassGuid), device_index,
                                                                    byref(device_interface_data))
                if not ret:
                    err = GetLastError()
                    if err != 259:
                        print("SetupDiEnumDeviceInterfaces return:", err)
                    break
                required_size = c_ulong(0)
                SP_DATA_A = SP_DATA_A_factory(8)
                self.setupapi_dll.SetupDiGetDeviceInterfaceDetailA.argtypes = (
                c_void_p, POINTER(SP_DEVICE_INTERFACE_DATA), POINTER(SP_DATA_A), c_ulong, POINTER(c_ulong), c_void_p)
                ret = self.setupapi_dll.SetupDiGetDeviceInterfaceDetailA(device_info_set,
                                                                         pointer(device_interface_data), None, 0,
                                                                         byref(required_size), None)
                # print(required_size.value)
                SP_DATA_A = SP_DATA_A_factory(required_size.value)
                self.setupapi_dll.SetupDiGetDeviceInterfaceDetailA.argtypes = (
                c_void_p, POINTER(SP_DEVICE_INTERFACE_DATA), POINTER(SP_DATA_A), c_ulong, POINTER(c_ulong), c_void_p)
                if platform.architecture()[0] == "64bit":
                    device_interface_detail_data = SP_DATA_A(*[8, b''])
                else:
                    device_interface_detail_data = SP_DATA_A(*[5, b''])
                ret = self.setupapi_dll.SetupDiGetDeviceInterfaceDetailA(device_info_set,
                                                                         pointer(device_interface_data),
                                                                         byref(device_interface_detail_data),
                                                                         required_size, None, None)
                # print(ret)
                if ret:
                    # print(device_interface_detail_data.DevicePath)
                    device_path = device_interface_detail_data.DevicePath.decode("gbk")
                    # print(device_path)
                    if device_path.find("pid") != -1:
                        # print(device_path)
                        if device_path.find("&mi_00#") != -1:
                            result.append(device_path)
                else:
                    print("SetupDiGetDeviceInterfaceDetailA return:", GetLastError())
                device_index += 1
        return result

    def open(self, path):
        handle = windll.kernel32.CreateFileA(c_char_p(bytes(path, "gbk")), 0xc0000000, 3, None, 3, 0x00000080, 0)
        if handle == -1:
            return False
        self.handle = handle
        return True

    def close(self):
        if self.handle:
            windll.kernel32.CancelIo(self.handle)
            windll.kernel32.CloseHandle(self.handle)
            self.handle = None

    def write(self, data):
        if self.handle == -1:
            return -1
        length = len(data)
        buf = bytearray(data)
        ret = windll.kernel32.WriteFile(self.handle, c_char_p(bytes(buf)), length, None, None)
        return ret

    def read(self, len, timeout):
        if self.handle == -1:
            return -1
        buf = create_string_buffer(len)
        bytes_read = c_ulong(0)
        ret = windll.kernel32.ReadFile(self.handle, buf, len, byref(bytes_read), None)
        if ret:
            return bytes(buf)
        else:
            return None
