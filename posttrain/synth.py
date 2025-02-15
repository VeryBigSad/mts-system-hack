def generate_synthetic_example(task: TaskType) -> str:
    """
    Генерация синтетического примера для конкретной задачи с использованием vLLM
    """
    # Получаем параметры задачи
    task_params = TASK_PARAMETERS[task]
    input_types = [t.value for t in TASK_INPUT_SUPPORT[task]]
    
    prompt = f"""
Ты - генератор обучающих данных для системы обработки запросов ЖКХ.
Сгенерируй реалистичный пример запроса и его классификации для следующей задачи:

Задача: {task.value} ({task.name})
Требуемые параметры: {', '.join(task_params)}
Поддерживаемые типы ввода: {', '.join(input_types)}

Вот примеры существующих запросов и их классификации:

Запрос: "Посмотри, есть ли препятствия в подъезде"
Рассуждение: Пользователь хочет проверить наличие препятствий, это связано с безопасностью передвижения.
Выбранная задача: check_obstacles
Параметры: {{"location": "подъезд", "floor": "1", "description": "проверка препятствий"}}

Запрос: "Вызови лифт на 5 этаж"
Рассуждение: Пользователь хочет воспользоваться лифтом, нужно отправить лифт на указанный этаж.
Выбранная задача: call_elevator
Параметры: {{"floor": 5, "direction": "up", "priority": "normal"}}

Запрос: "Проверь сугробы возле дома"
Рассуждение: Пользователь интересуется состоянием территории, нужно проверить уровень снега.
Выбранная задача: check_snow
Параметры: {{"location": "возле дома", "area": "придомовая территория", "priority": "high"}}

Запрос: "Создай заявку на ремонт трубы в ванной, течет сильно"
Рассуждение: Пользователь сообщает об аварийной ситуации, требуется создание срочной заявки.
Выбранная задача: create_ticket
Параметры: {{"category": "сантехника", "description": "течь трубы в ванной", "priority": "high", "location": "ванная"}}

Запрос: "Хочу подать показания за воду, счетчик показывает 12345"
Рассуждение: Пользователь хочет передать показания счетчика воды.
Выбранная задача: submit_readings
Параметры: {{"meter_type": "вода", "value": "12345", "period": "текущий месяц"}}

Запрос: "Нужно оплатить счет за отопление на 5000 рублей"
Рассуждение: Пользователь хочет произвести оплату коммунальных услуг.
Выбранная задача: pay_utilities
Параметры: {{"amount": 5000, "service_type": "отопление", "period": "текущий месяц"}}

Запрос: "Проверь камеру у второго подъезда"
Рассуждение: Пользователь запрашивает просмотр камеры видеонаблюдения.
Выбранная задача: check_camera
Параметры: {{"camera_id": "2", "location": "второй подъезд", "time_period": "текущее время"}}

Сгенерируй один новый пример в том же формате:
Запрос: [реалистичный пользовательский запрос]
Рассуждение: [подробное логическое обоснование выбора задачи]
Выбранная задача: {task.value}
Параметры: [JSON с требуемыми параметрами: {', '.join(task_params)}]

Используй следующие примеры как образец стиля:
{FEW_SHOT_EXAMPLES}

Сгенерируй один новый пример:
"""

    sampling_params = SamplingParams(
        temperature=0.8,
        max_tokens=500,
        top_p=0.95
    )
    
    return prompt

def generate_synthetic_dataset(examples_per_task: int = 10) -> List[str]:
    """
    Генерация набора синтетических данных для всех задач
    """
    # Подготавливаем промпты для всех задач
    prompts = []
    for task in TaskType:
        prompts.extend([generate_synthetic_example(task) for _ in range(examples_per_task)])
    
    # Генерируем ответы батчами
    all_examples = []
    batch_size = 8  # Размер батча для vLLM
    
    for i in range(0, len(prompts), batch_size):
        batch_prompts = prompts[i:i + batch_size]
        outputs = llm.generate(batch_prompts, sampling_params)
        
        for output in outputs:
            example = output.outputs[0].text.strip()
            all_examples.append(example)
    
    return all_examples

# Пример использования:
# examples = generate_synthetic_dataset(10)
# for example in examples:
#     print(example)
#     print("-" * 80)
