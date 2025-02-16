from enum import Enum

class InputType(Enum):
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    GESTURE = "gesture"  # Для будущего расширения


class TaskType(Enum):
    CHECK_OBSTACLES = "check_obstacles"  # Проверка препятствий
    CHECK_CAMERA = "check_camera"        # Просмотр камеры
    CHECK_SNOW = "check_snow"            # Проверка сугробов
    CALL_ELEVATOR = "call_elevator"      # Вызов лифта
    CREATE_TICKET = "create_ticket"      # Создание тикета
    SUBMIT_READINGS = "submit_readings"  # Подача показаний
    PAY_UTILITIES = "pay_utilities"      # Оплата счетов 
