# -*- coding: utf-8 -*-

import simple_hid
import ctypes
import sys
import time
import random

k1 = "`1234567890-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./ "
k2 = "~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:\"ZXCVBNM<>?"


def CanInput(c):
    if c in k1:
        return True
    if c in k2:
        return True
    return False


def needShift(c):
    return c in k2


def getUnShiftKey(c):
    for i in range(0, 48):
        if k2[i] == c:
            return k1[i]
    return 0


class i_KM:
    def __init__(self):
        self.dev = None
        self.version = 0
        self.model = 0
        self.vid = 0
        self.pid = 0
        self.wait_respon = False
        if sys.platform == "win32":
            user32 = ctypes.windll.user32
            self.screenX = user32.GetSystemMetrics(78)
            self.screenY = user32.GetSystemMetrics(79)
        else:
            import tkinter
            root = tkinter.Tk()
            self.screenX = root.winfo_vrootwidth()
            self.screenY = root.winfo_vrootheight()
            root.quit()

    # print(self.screenX,self.screenY)

    def __del__(self):
        self.Close()

    def Close(self):
        if self.dev:
            self.dev.close()
            self.dev = None
        self.version = 0
        self.model = 0
        self.vid = 0
        self.pid = 0
        self.wait_respon = False

    def DelayRandom(self, min, max):
        delay = 0;
        if max >= min and max > 0 and min >= 0:
            delay = random.randint(min, max)
        elif max == 0 and min > 0:
            delay = min;
        if delay > 0:
            time.sleep(delay / 1000)

    def OpenDevice(self):
        return self.OpenDeviceByID(0x1c1f, 0xc18a)

    def OpenDeviceByID(self, vid, pid):
        dev = simple_hid.HID()
        devices = dev.enum_device()
        vidpid_str = "#vid_{:04x}&pid_{:04x}&".format(vid, pid)
        for device in devices:
            if device.find(vidpid_str) == -1:
                continue
            print("open", device)
            ret = dev.open(device)
            if not ret:
                dev.close()
            else:
                self.dev = dev
                ret = self._getVersion()
                if not ret:
                    continue
                self.version = ret[1]
                self.model = ret[0]
                return True
        return False

    def IsOpen(self):
        return self.dev != None

    def write_cmd(self, cmd, dat=None):
        if not self.dev:
            return -1
        if dat and len(dat) > 61:
            return -2
        buf = [32, 1, cmd]
        if dat:
            buf[1] = len(dat) + 1
            buf.extend(dat)
        buf.extend([0xff] * (64 - len(buf)))
        ret = self.dev.write(buf)
        # print(ret)
        if ret < 0:
            self.Close()
        return ret

    def read_data_timeout(self, timeout=None):
        if not self.dev:
            return None
        try:
            ret = self.dev.read(64, timeout)
            if ret and ret[0] == 31:
                return ret[2], ret[3:ret[1] + 2]
            else:
                return None
        except OSError:
            self.Close()
            return None

    def read_data_timeout_promise(self, cmd, timeout=None):
        if not self.dev:
            return None
        for i in range(0, 10):
            ret = self.read_data_timeout(timeout)
            if ret and ret[0] == cmd:
                return ret[1]
        return None

    def _getVersion(self):
        self.write_cmd(1)
        return self.read_data_timeout_promise(1, 10)

    def GetVID(self):
        return self.vid

    def GetPID(self):
        return self.pid

    def GetVersion(self):
        return self.version

    def GetModel(self):
        return self.model

    def GetChipID(self):
        self.write_cmd(12)
        ret = self.read_data_timeout_promise(9, 10)
        if not ret:
            return -1
        result = int.from_bytes(ret, byteorder='little', signed=True)
        result += 113666
        return ctypes.c_int32(result).value

    def GetStorageSize(self):
        self.write_cmd(2)
        ret = self.read_data_timeout_promise(2, 10)
        if not ret:
            return -1
        result = int.from_bytes(ret, byteorder='little', signed=True)
        return result

    def SetWaitRespon(self, wait):
        self.wait_respon = wait
        self.write_cmd(34)
        self.read_data_timeout_promise(39, 10)

    def Reboot(self):
        self.write_cmd(20)
        ret = self.read_data_timeout_promise(39, 10)
        if not ret:
            return 1
        else:
            self.Close()
            return 0

    def SetVidPid(self, vid, pid):
        cmd = [0, 0, 0, 4, vid & 0xff, (vid >> 8) & 0xff, pid & 0xff, (pid >> 8) & 0xff]
        if self.write_cmd(7, cmd) == -1:
            return 1
        ret = self.read_data_timeout_promise(7, 10)
        return 0 if ret else 1

    def SetConfigData(self, index, data):
        if index < 0 or index >= 252:
            return 2
        cmd = [0xff] * 6
        addr = index * 2 + 8

        cmd[0] = (addr >> 24) & 0xff
        cmd[1] = (addr >> 16) & 0xff
        cmd[2] = (addr >> 8) & 0xff
        cmd[3] = (addr >> 0) & 0xff
        cmd[4] = (data & 0xff00) >> 8
        cmd[5] = data & 0xff
        if self.write_cmd(7, cmd) == -1:
            return 1
        ret = self.read_data_timeout_promise(7, 100)
        return 0 if ret else 1

    def GetConfigData(self, index):
        if index < 0 or index >= 252:
            return -2
        cmd = [0xff] * 5
        addr = index * 2 + 8

        cmd[0] = (addr >> 24) & 0xff
        cmd[1] = (addr >> 16) & 0xff
        cmd[2] = (addr >> 8) & 0xff
        cmd[3] = (addr >> 0) & 0xff
        cmd[4] = 2

        if self.write_cmd(6, cmd) == -1:
            return -1
        ret = self.read_data_timeout_promise(6, 20)
        if not ret:
            return -1
        return ret[0] * 256 + ret[1]

    def SetLed(self, on):
        self.write_cmd(24, [1 if on else 0])
        ret = self.read_data_timeout_promise(39, 10)
        return 0 if ret else 1

    def RunScript(self, mode, index):
        self.write_cmd(5, [mode, index])

    def mouse_event(self, e, x=0, y=0, extra1=0, extra2=0):
        cmd = [0xff] * 12
        cmd[0] = e
        if e >= 1 and e <= 7:
            pass
        elif e == 8:
            if x < 0:
                x = 0
            if y < 0:
                y = 0

            screenx = self.screenX
            screeny = self.screenY
            if x >= screenx:
                x = screenx - 1
            if y >= screeny:
                y = screeny - 1

            x = int((x << 15) / screenx)
            y = int((y << 15) / screeny)
            cmd[1] = (x >> 8) & 0xff
            cmd[2] = x & 0xff
            cmd[3] = (y >> 8) & 0xff
            cmd[4] = y & 0xff
        elif e == 9:
            if x < -128 or x > 127 or y < -128 or y > 127:
                return
            cmd[1] = x;
            cmd[2] = y;
        elif e == 91:
            if x < -32768 or x > 32767 or y < -32768 or y > 32767:
                return
            cmd[1] = (x >> 8) & 0xff
            cmd[2] = x & 0xff
            cmd[3] = (y >> 8) & 0xff
            cmd[4] = y & 0xff;
        elif e == 10:
            if x < -128 or x > 127:
                return
            cmd[1] = x
        elif e == 11:
            if x < 0:
                x = 0
            if y < 0:
                y = 0

            cmd[1] = (x >> 8) & 0xff
            cmd[2] = x & 0xff
            cmd[3] = (y >> 8) & 0xff
            cmd[4] = y & 0xff
            screenx = self.screenX
            screeny = self.screenY
            cmd[5] = (screenx >> 8) & 0xff
            cmd[6] = screenx & 0xff
            cmd[7] = (screeny >> 8) & 0xff
            cmd[8] = screeny & 0xff
            cmd[9] = extra1
            cmd[10] = extra2
        elif e == 12:
            cmd[1] = (x >> 8) & 0xff
            cmd[2] = x & 0xff
            cmd[3] = (y >> 8) & 0xff
            cmd[4] = y & 0xff
            screenx = self.screenX
            screeny = self.screenY
            cmd[5] = (screenx >> 8) & 0xff
            cmd[6] = screenx & 0xff
            cmd[7] = (screeny >> 8) & 0xff
            cmd[8] = screeny & 0xff
            cmd[9] = extra1
            cmd[10] = extra2
        elif e == 13 or e == 14:
            cmd[1] = x
        self.write_cmd(16, cmd);
        if self.wait_respon:
            self.read_data_timeout_promise(20, 10)

    def LeftDown(self):
        self.mouse_event(1)

    def LeftUp(self):
        self.mouse_event(2)

    def LeftClick(self, min=0, max=0):
        self.LeftDown()
        self.DelayRandom(min, max)
        self.LeftUp()

    def LeftDoubleClick(self, min=0, max=0):
        self.LeftDown()
        self.DelayRandom(min, max)
        self.LeftUp()
        self.DelayRandom(min, max)
        self.LeftDown()
        self.DelayRandom(min, max)
        self.LeftUp()

    def RightDown(self):
        self.mouse_event(3)

    def RightUp(self):
        self.mouse_event(4)

    def RightClick(self, min=0, max=0):
        self.RightDown()
        self.DelayRandom(min, max)
        self.RightUp()

    def MiddleDown(self):
        self.mouse_event(5)

    def MiddleUp(self):
        self.mouse_event(6)

    def MiddleClick(self, min=0, max=0):
        self.MiddleDown()
        self.DelayRandom(min, max)
        self.MiddleUp()

    def MouseWheel(self, delta):
        self.mouse_event(10, delta)

    def MouseButtonDown(self, index):
        if index < 1 or index > 8:
            return
        index -= 1
        self.mouse_event(13, index)

    def MouseButtonUp(self, index):
        if index < 1 or index > 8:
            return
        index -= 1
        self.mouse_event(14, index)

    def MouseButtonClick(self, index, min=0, max=0):
        self.MouseButtonDown(index)
        self.DelayRandom(min, max)
        self.MouseButtonUp(index)

    def MouseAllUp(self):
        self.mouse_event(7)

    def MoveTo(self, x, y):
        self.mouse_event(8, x, y)

    def MoveR(self, x, y):
        self.mouse_event(91, x, y)

    def MoveD(self, x, y, delay=8, delta=10):
        self.mouse_event(11, x, y, delay, delta)

    def MoveRD(self, dx, dy, delay=8, delta=10):
        self.mouse_event(12, dx, dy, delay, delta)

    @staticmethod
    def GetScanCodeFromVirtualCode(vcode):
        keymap = {
            "65": 4, "66": 5, "67": 6, "68": 7, "69": 8, "70": 9, "71": 10, "72": 11, "73": 12, "74": 13, "75": 14,
            "76": 15, "77": 16, "78": 17, "79": 18,
            "80": 19, "81": 20, "82": 21, "83": 22, "84": 23, "85": 24, "86": 25, "87": 26, "88": 27, "89": 28,
            "90": 29, "49": 30, "50": 31, "51": 32, "52": 33,
            "53": 34, "54": 35, "55": 36, "56": 37, "57": 38, "48": 39, "13": 40, "27": 41, "8": 42, "9": 43, "32": 44,
            "189": 45, "187": 46, "219": 47, "221": 48,
            "220": 49, "186": 51, "222": 52, "192": 53, "188": 54, "190": 55, "191": 56, "20": 57, "112": 58, "113": 59,
            "114": 60, "115": 61, "116": 62, "117": 63,
            "118": 64, "119": 65, "120": 66, "121": 67, "122": 68, "123": 69, "44": 70, "145": 71, "19": 72, "19": 72,
            "45": 73, "36": 74, "33": 75, "46": 76, "35": 77,
            "34": 78, "39": 79, "37": 80, "40": 81, "38": 82, "144": 83, "111": 84, "96": 85, "109": 86, "107": 87,
            "108": 88, "97": 89, "98": 90, "99": 91, "100": 92,
            "101": 93, "102": 94, "103": 95, "104": 96, "105": 97, "96": 98, "110": 99, "93": 101, "146": 103,
            "173": 127, "175": 128, "174": 129, "162": 224, "160": 225,
            "164": 226, "91": 227, "163": 228, "161": 229, "165": 230, "92": 231, "17": 224, "16": 225, "18": 226
        }
        vcode = str(vcode)
        if vcode in keymap:
            return keymap[vcode]
        else:
            return 0

    @staticmethod
    def GetScanCodeFromKeyName(keyname):
        keymap = {
            "a": 4, "b": 5, "c": 6, "d": 7, "e": 8, "f": 9, "g": 10, "h": 11, "i": 12, "j": 13, "k": 14, "l": 15,
            "m": 16, "n": 17, "o": 18, "p": 19, "q": 20,
            "r": 21, "s": 22, "t": 23, "u": 24, "v": 25, "w": 26, "x": 27, "y": 28, "z": 29, "1": 30, "2": 31, "3": 32,
            "4": 33, "5": 34, "6": 35, "7": 36,
            "8": 37, "9": 38, "0": 39, "enter": 40, "esc": 41, "backspace": 42, "tab": 43, "space": 44, " ": 44,
            "空格键": 44, "-": 45, "=": 46, "[": 47, "]": 48,
            "\\": 49, ";": 51, "'": 52, "`": 53, ",": 54, ".": 55, "/": 56, "capslock": 57, "f1": 58, "f2": 59,
            "f3": 60, "f4": 61, "f5": 62, "f6": 63, "f7": 64,
            "f8": 65, "f9": 66, "f10": 67, "f11": 68, "f12": 69, "printscreen": 70, "scrolllock": 71, "pause": 72,
            "break": 72, "insert": 73, "home": 74,
            "pageup": 75, "delete": 76, "end": 77, "pagedown": 78, "right": 79, "left": 80, "down": 81, "up": 82,
            "numlock": 83, "小键盘/": 84, "小键盘*": 85,
            "小键盘-": 86, "小键盘+": 87, "小键盘enter": 88, "小键盘1": 89, "小键盘2": 90, "小键盘3": 91, "小键盘4": 92,
            "小键盘5": 93, "小键盘6": 94,
            "小键盘7": 95, "小键盘8": 96, "小键盘9": 97, "小键盘0": 98, "小键盘.": 99, "menu": 101, "小键盘=": 103,
            "静音": 127, "音量加": 128, "音量减": 129,
            "lctrl": 224, "lshift": 225, "lalt": 226, "lwin": 227, "rctrl": 228, "rshift": 229, "ralt": 230,
            "rwin": 231,
            "ctrl": 224, "shift": 225, "alt": 226, "win": 227
        }
        keyname = keyname.lower()
        if keyname in keymap:
            return keymap[keyname]
        else:
            return 0

    def key_event(self, e, key):
        cmd = [e, 0xff]
        if isinstance(key, str):
            key = self.GetScanCodeFromKeyName(key)
        cmd[1] = key
        self.write_cmd(17, cmd);
        if self.wait_respon:
            self.read_data_timeout_promise(20, 10)

    def KeyDownName(self, keyname):
        self.key_event(1, keyname)

    def KeyUpName(self, keyname):
        self.key_event(2, keyname)

    def KeyPressName(self, keyname, min=0, max=0):
        self.key_event(1, keyname)
        self.DelayRandom(min, max)
        self.key_event(2, keyname)

    def KeyDownCode(self, keycode):
        self.key_event(1, keycode)

    def KeyUpCode(self, keycode):
        self.key_event(2, keycode)

    def KeyPressCode(self, keycode, min=0, max=0):
        self.key_event(1, keycode)
        self.DelayRandom(min, max)
        self.key_event(2, keycode)

    def KeyDownVirtualCode(self, keycode):
        keycode = self.GetScanCodeFromVirtualCode(keycode)
        self.KeyDownCode(keycode)

    def KeyUpVirtualCode(self, keycode):
        keycode = self.GetScanCodeFromVirtualCode(keycode)
        self.KeyUpCode(keycode)

    def KeyPressVirtualCode(self, keycode, min=0, max=0):
        keycode = self.GetScanCodeFromVirtualCode(keycode)
        self.KeyPressCode(keycode)

    def SayString(self, s, min=0, max=0):
        len_s = len(s)
        shift = False;
        for i in range(0, len_s):
            c = s[i]
            need_shift = needShift(c)
            keyname = c
            if need_shift:
                keyname = getUnShiftKey(c)
            if need_shift and not shift:
                self.KeyDownCode(0xE1)
                self.DelayRandom(min, max)
                shift = True
            self.KeyPressName(keyname, min, max)
            self.DelayRandom(min, max)
            if i == len_s - 1:
                need_shift = False
            else:
                need_shift = needShift(s[i + 1])

            if not need_shift and shift:
                self.KeyUpCode(0xE1)
                self.DelayRandom(min, max)
                shift = False

    def SayStringAnsi(self, s, min=0, max=0):
        s = s.encode("gbk")
        len_s = len(s)
        i = 0
        while i < len_s:
            c = s[i]
            code = 0
            if c < 128:
                code = c
                i += 1
            elif i < len_s - 1:
                code = c * 256 + s[i + 1]
                i += 2
            temp = str(code)
            self.KeyDownCode(0xe2)
            self.DelayRandom(min, max)
            for j in range(0, len(temp)):
                c2 = ord(temp[j]) - 48
                if c2 == 0:
                    c2 = 10
                keycode = 0x58 + c2
                self.KeyDownCode(keycode)
                self.DelayRandom(min, max)
                self.KeyUpCode(keycode)
                self.DelayRandom(min, max)
            self.KeyUpCode(0xe2)

    def SayStringUnicode(self, s, min=0, max=0):
        len_s = len(s)
        for c in s:
            temp = str(ord(c))
            self.KeyDownCode(0xe2)
            self.DelayRandom(min, max)
            for j in range(0, len(temp)):
                c2 = ord(temp[j]) - 48
                if c2 == 0:
                    c2 = 10
                keycode = 0x58 + c2
                self.KeyDownCode(keycode)
                self.DelayRandom(min, max)
                self.KeyUpCode(keycode)
                self.DelayRandom(min, max)
            self.KeyUpCode(0xe2)

    def Lock_Mouse(self, option):
        self.write_cmd(25, [option])
        ret = self.read_data_timeout_promise(39, 10)
        return 1 if ret else 0

    def Notify_Mouse(self, option):
        self.write_cmd(26, [option])
        ret = self.read_data_timeout_promise(39, 10)
        return 1 if ret else 0

    def Lock_KeyBoard(self, option):
        self.write_cmd(31, [option])
        ret = self.read_data_timeout_promise(39, 10)
        return 1 if ret else 0

    def Notify_KeyBoard(self, option):
        self.write_cmd(31, [option])
        ret = self.read_data_timeout_promise(39, 10)
        return 1 if ret else 0

    def Read_Notify(self, timeout):
        return self.read_data_timeout_promise(43, timeout)

    def GetKeyState(self, keycode):
        self.write_cmd(33, [keycode])
        ret = self.read_data_timeout_promise(49, 10)
        print(ret)
        return ret

    def Set_Freq(self, time):
        self.write_cmd(28, [time])
        return self.read_data_timeout_promise(39, 100)

    def Get_Freq(self):
        self.write_cmd(29)
        ret = self.read_data_timeout_promise(44, 100)
        return ret[0]
