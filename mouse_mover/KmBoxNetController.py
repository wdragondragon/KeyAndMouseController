from mouse_mover.KeyMouseController import KeyMouseController


class KmBoxNetControllerKey(KeyMouseController):

    def __init__(self, mouse_mover_param):
        import kmNet
        self.kmNet = kmNet
        # 初始化
        super().__init__(mouse_mover_param)
        ip = mouse_mover_param["ip"]
        port = mouse_mover_param["port"]
        uuid = mouse_mover_param["uuid"]
        self.kmNet.init(ip, port, uuid)  # 连接盒子
        self.listener = None
        self.toggle_key_listener = None

    def left_click(self):
        # 左键
        self.left(1)
        self.left(0)

    def left(self, vk_key: int):
        """
            鼠标左键控制 0松开 1按下
        """
        # 左键
        self.kmNet.left(1)
        self.kmNet.left(0)

    def move_rp(self, short_x: int, short_y: int, re_cut_size=0):
        self.kmNet.move(short_x, short_y)

    def move(self, short_x: int, short_y: int):
        """
        鼠标相对移动
        x		:鼠标X轴方向移动距离
        y		:鼠标Y轴方向移动距离
        返回值：
                -1：发送失败\n
                0：发送成功\n
        """

        self.kmNet.move_auto(short_x, short_y, int(max(5, short_x / 10, short_y / 10)))

    def destroy(self):
        """
            销毁
        """
        if self.listener is not None:
            self.listener.stop()
        if self.toggle_key_listener is not None:
            self.toggle_key_listener.destory()

    def click_key(self, value):
        self.kmNet.keydown(value)
        self.kmNet.keyup(value)

    def key_down(self, value):
        self.kmNet.keydown(value)

    def key_up(self, value):
        self.kmNet.keyup(value)

    def show_pic(self, pic_array):
        self.kmNet.lcd_picture_bottom(pic_array)
