from googletrans import Translator

def check_and_translate_to_russian(text: str) -> str:
    """
    Проверяет первые символы текста на русский язык и при необходимости переводит весь текст
    """
    # Проверяем первые символы на принадлежность к русскому алфавиту
    russian_chars = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')
    first_chars = set(text[:3].replace(' ', ''))  # Берем первые 3 символа, исключая пробелы
    
    # Если нет пересечения с русскими символами, переводим текст
    if not first_chars.intersection(russian_chars):
        try:
            translator = Translator()
            translated = translator.translate(text, dest='ru')
            return translated.text
        except Exception as e:
            print(f"Ошибка при переводе: {str(e)}")
            return text
    return text

#в начало классификации или в основной респонс хз как по вайбу 
# Проверяем и при необходимости переводим запрос на русский
    user_input = check_and_translate_to_russian(user_input)
