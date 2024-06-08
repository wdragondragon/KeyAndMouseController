import time

from IntentManager import IntentManager
from log import LogFactory
from controller import ControllerFactory
from controller.KeyMouseController import KeyMouseController

controller_params = {
    "win32api": {},
    "km_box": {
        "VID/PID": "66882021"
    },
    "wu_ya": {
        "VID/PID": "046DC539"
    },
    "km_box_net": {
        "ip": "192.168.2.188",
        "port": "35368",
        "uuid": "8A6E5C53"
    },
    "fei_yi_lai": {
        "VID/PID": "C2160102"
    },
    "fei_yi_lai_single": {
        "VID/PID": "C2160301"
    },
    "logitech": {},
    "pan_ni": {
        "VID/PID": "1C1FC18A"
    }
}

if __name__ == '__main__':
    LogFactory.init_logger('console')

    key_mouse_controller: KeyMouseController = ControllerFactory.get_controller(controller_params=controller_params,
                                                                                mouse_model='pan_ni')
    intent_manager: IntentManager = IntentManager(key_mouse_controller=key_mouse_controller, move_step=(1, 1),
                                                  move_step_max=(3, 2), move_frequency=500)
    intent_manager.start()
    # intent_manager.set_intention(200, 100)
    # key_mouse_controller.move(1000, 1000)
    # intent_manager.testMouseRate()
    intent_manager.stop()
