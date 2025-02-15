from .enums import InputType, TaskType

TASK_PARAMETERS = {
    TaskType.CHECK_OBSTACLES: ["location", "floor", "description"],
    TaskType.CHECK_CAMERA: ["camera_id", "location", "time_period"],
    TaskType.CHECK_SNOW: ["location", "area", "priority"],
    TaskType.CALL_ELEVATOR: ["floor", "direction", "priority"],
    TaskType.CREATE_TICKET: ["category", "description", "priority", "location"],
    TaskType.SUBMIT_READINGS: ["meter_type", "value", "apartment", "period"],
    TaskType.PAY_UTILITIES: ["amount", "service_type", "period", "account_number"]
}

TASK_INPUT_SUPPORT = {
    TaskType.CHECK_OBSTACLES: {InputType.IMAGE, InputType.TEXT},
    TaskType.CHECK_CAMERA: {InputType.TEXT},
    TaskType.CHECK_SNOW: {InputType.IMAGE, InputType.TEXT},
    TaskType.CALL_ELEVATOR: {InputType.TEXT, InputType.VOICE},
    TaskType.CREATE_TICKET: {InputType.TEXT, InputType.VOICE},
    TaskType.SUBMIT_READINGS: {InputType.TEXT, InputType.IMAGE},
    TaskType.PAY_UTILITIES: {InputType.TEXT}
}

FEW_SHOT_EXAMPLES = """
Запрос: "Посмотри, есть ли препятствия в подъезде"
Рассуждение: Пользователь хочет проверить наличие препятствий, это связано с безопасностью передвижения.
Выбранная задача: check_obstacles
Параметры: {"location": "подъезд", "floor": "1", "description": "проверка препятствий"}

Запрос: "Вызови лифт на 5 этаж"
Рассуждение: Пользователь хочет воспользоваться лифтом, нужно отправить лифт на указанный этаж.
Выбранная задача: call_elevator
Параметры: {"floor": 5, "direction": "up", "priority": "normal"}

Запрос: "Проверь сугробы возле дома"
Рассуждение: Пользователь интересуется состоянием территории, нужно проверить уровень снега.
Выбранная задача: check_snow
Параметры: {"location": "возле дома", "area": "придомовая территория", "priority": "high"}

Запрос: "Создай заявку на ремонт трубы в ванной, течет сильно"
Рассуждение: Пользователь сообщает об аварийной ситуации, требуется создание срочной заявки.
Выбранная задача: create_ticket
Параметры: {"category": "сантехника", "description": "течь трубы в ванной", "priority": "high", "location": "ванная"}

Запрос: "Хочу подать показания за воду, счетчик показывает 12345"
Рассуждение: Пользователь хочет передать показания счетчика воды.
Выбранная задача: submit_readings
Параметры: {"meter_type": "вода", "value": "12345", "period": "текущий месяц"}

Запрос: "Нужно оплатить счет за отопление на 5000 рублей"
Рассуждение: Пользователь хочет произвести оплату коммунальных услуг.
Выбранная задача: pay_utilities
Параметры: {"amount": 5000, "service_type": "отопление", "period": "текущий месяц"}

Запрос: "Проверь камеру у второго подъезда"
Рассуждение: Пользователь запрашивает просмотр камеры видеонаблюдения.
Выбранная задача: check_camera
Параметры: {"camera_id": "2", "location": "второй подъезд", "time_period": "текущее время"}
""" 