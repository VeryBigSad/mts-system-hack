import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import re
import logging

from .enums import InputType, TaskType
from .constants import TASK_PARAMETERS, TASK_INPUT_SUPPORT, FEW_SHOT_EXAMPLES
from .llm import llm_generate

logger = logging.getLogger(__name__)


async def speech_to_text(audio_path: str) -> str:
    """Заглушка для конвертации речи в текст"""
    logger.info(f"Конвертация аудио {audio_path} в текст")
    # TODO: Implement actual async speech-to-text conversion
    return "преобразованный текст из аудио"


async def text_to_speech(text: str, output_path: str) -> str:
    """Заглушка для конвертации текста в речь"""
    logger.info(f"Конвертация текста '{text}' в аудио {output_path}")
    # TODO: Implement actual async text-to-speech conversion
    return output_path


async def classify_request(user_input: str, available_input_types: List[InputType]) -> Dict[str, Any]:
    """Классификация запроса пользователя с учетом доступных входных типов"""
    try:
        available_tasks = [
            task for task in TaskType 
            if any(input_type in TASK_INPUT_SUPPORT[task] for input_type in available_input_types)
        ]
        task_descriptions = "\n".join([f"- {task.value}: {task.name}" for task in available_tasks])
        prompt = f"""{FEW_SHOT_EXAMPLES}\n\nДоступные задачи:\n{task_descriptions}\n\nЗапрос пользователя: {user_input}\n\nРассуждение: Давайте проанализируем запрос пользователя шаг за шагом:\n1) Какую основную потребность выражает пользователь?\n2) Какая из доступных задач лучше всего подходит для решения этой потребности?\n3) Какие параметры нужны для выполнения задачи?\n\nНа основе анализа:"""
        
        reasoning = await llm_generate(prompt)
        logger.info(f"Reasoning: {reasoning}")
        
        task_match = re.search(r'(?:выбранная задача|selected task):\s*(\w+)', reasoning.lower())
        if not task_match:
            return {"status": "error", "message": "Не удалось определить задачу"}
        task_name = task_match.group(1)
        
        params_match = re.search(r'параметры:\s*({[^}]+})', reasoning.lower())
        parameters = {}
        if params_match:
            try:
                parameters = json.loads(params_match.group(1))
            except json.JSONDecodeError:
                logger.error("Failed to parse parameters JSON")
        
        try:
            task = TaskType(task_name)
        except ValueError:
            return {"status": "error", "message": f"Неизвестная задача: {task_name}"}
        
        request_data = {
            "task": task.value,
            "timestamp": datetime.now().isoformat(),
            "input": user_input,
            "parameters": parameters
        }
        
        return {"status": "success", "request": request_data, "reasoning": reasoning}
    except Exception as e:
        logger.error(f"Error in classify_request: {str(e)}", exc_info=True)
        raise


async def process_request(
    input_data: str, 
    input_type: InputType = InputType.TEXT,
    needs_voice_response: bool = False,
    output_audio_path: Optional[str] = None
) -> Dict[str, Any]:
    """Основная функция обработки запроса пользователя"""
    try:
        logger.info(f"Processing request: {input_data[:100]}... (type: {input_type})")
        available_input_types = [input_type]
        
        # Convert voice to text if needed
        user_input = await speech_to_text(input_data) if input_type == InputType.VOICE else input_data
        
        # Classify the request
        classification_result = await classify_request(user_input, available_input_types)
        if classification_result["status"] != "success":
            logger.error(f"Classification failed: {classification_result['message']}")
            return classification_result
        
        logger.info(f"Request classified as: {classification_result['request']['task']}")
        text_response = json.dumps(classification_result["request"], ensure_ascii=False, indent=2)
        result = {
            "status": "success",
            "classification": classification_result,
            "text_response": text_response
        }
        
        # Generate voice response if needed
        if needs_voice_response and output_audio_path:
            audio_path = await text_to_speech(text_response, output_audio_path)
            result["audio_response"] = audio_path
            logger.info(f"Generated voice response at: {audio_path}")
        
        return result
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return {"status": "error", "message": f"Ошибка при обработке запроса: {str(e)}"} 