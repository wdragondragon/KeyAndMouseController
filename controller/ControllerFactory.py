from controller.PanNiController import PanNiController
from log import LogFactory
from controller.FeiController import FeiControllerKey
from controller.KmBoxController import KmBoxControllerKey
from controller.KmBoxNetController import KmBoxNetControllerKey
from controller.Win32ApiController import Win32ApiControllerKey
from controller.WuYaController import WuYaControllerKey


def get_controller(controller_params, mouse_model):
    """
        获取键鼠模拟器
    :param logger:
    :param controller_params:
    :param mouse_model:
    :return:
    """
    controller_params = controller_params[mouse_model]
    if controller_params is None:
        LogFactory.logger().print_log(f"鼠标模式:[{mouse_model}]不可用")
        return None
    else:
        LogFactory.logger().print_log(f"初始化鼠标模式：[{mouse_model}]")
    if mouse_model == 'win32api':
        return Win32ApiControllerKey(controller_params)
    elif mouse_model == "km_box":
        return KmBoxControllerKey(controller_params)
    elif mouse_model == "wu_ya":
        return WuYaControllerKey(controller_params)
    elif mouse_model == "fei_yi_lai":
        return FeiControllerKey(controller_params)
    elif mouse_model == "km_box_net":
        return KmBoxNetControllerKey(controller_params)
    elif mouse_model == "pan_ni":
        return PanNiController(controller_params)
