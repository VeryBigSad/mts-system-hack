# МТС Система Хакатон - Инклюзивный дом

Проект разработан для хакатона МТС Система, трек "Инклюзивный дом". Решение представляет собой систему умного помощника для людей с ограниченными возможностями, позволяющую взаимодействовать с системой ЖКХ через различные каналы коммуникации: голос, текст и язык жестов.

## Запуск проекта

1. Клонировать репозиторий
2. Запустить модуль backend
3. Запустить модуль ml_service
4. Запустить модуль frontend

См. инструкции по запуску в каждом модуле.

## Структура проекта

### Frontend (./frontend)
Клиентское веб-приложение, разработанное на React + TypeScript:
- Поддержка различных способов ввода (текст, голос, жесты)
- Интерактивный чат-интерфейс
- Распознавание языка жестов через веб-камеру
- Адаптивный дизайн

### Backend (./backend)
API-сервер на FastAPI для обработки запросов (бизнес-логика):
- Конвертация речи/видео в текст
- Маршрутизация запросов в ML-сервис
- Сохранение истории запросов
- Асинхронная обработка через Redis

### ML Service (./ml_service)
Сервис машинного обучения для обработки запросов:
- Классификация намерений пользователя
- Обработка естественного языка
- Поддержка мультиязычности
- Интеграция с LLM для генерации ответов

### Posttrain (./posttrain)
Скрипты и конфигурации для дообучения моделей:
- Генерация синтетических данных
- Файлы конфигурации для обучения
- Утилиты для подготовки данных
- Скрипты для fine-tuning моделей

## Основные функции системы
- Создание заявок в УК
- Вызов лифта
- Просмотр камер видеонаблюдения
- Проверка состояния территории
- Передача показаний счетчиков
- Оплата коммунальных услуг

## Технологии
- Frontend: React, Vite, TypeScript, TailwindCSS
- Backend: FastAPI, PostgreSQL, Redis, FFmpeg
- ML Service: vLLM, Pytorch, huggingface
- Infrastructure: Docker, Docker Compose, Nginx, Postgres, Redis
