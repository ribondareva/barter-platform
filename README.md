# Barter Platform

![Python](https://img.shields.io/badge/python-3.11-blue)
![Django](https://img.shields.io/badge/django-5.2-green)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-pytest-orange)
![Coverage](https://img.shields.io/badge/coverage-90%25-green)

Веб-приложение на Django для обмена вещами между пользователями.  
Пользователи могут размещать объявления, просматривать чужие, отправлять предложения на обмен и управлять своими активностями.

## 🚀 Возможности

- Регистрация и аутентификация пользователей
- Создание, редактирование и удаление объявлений
- Добавление описания, категории, состояния и изображения вещи
- Поиск и фильтрация объявлений по категории, состоянию и ключевым словам
- Просмотр всех доступных объявлений
- Отправка предложений на обмен между объявлениями
- Принятие или отклонение предложений
- Защита: нельзя обмениваться собственными объявлениями и одним и тем же

## 🛠️ Технологии

- Python 3.11
- Django 5.2
- Django Templates
- SQLite
- Pytest, pytest-django

## Установка и запуск

### 1. Клонируйте репозиторий:

```bash
git clone https://github.com/ribondareva/barter-platform.git
cd barter-platform
```
### 2. Создайте и активируйте виртуальное окружение:
```bash
python -m venv venv
```
```bash
# Windows
venv\Scripts\activate
```
```bash
# macOS / Linux
source venv/bin/activate
```
### 3. Установите зависимости:
```bash
pip install -r requirements.txt
```
### 4. Создайте .env файл:
```bash
cp .env-example .env
```
Содержимое .env:
```python
SECRET_KEY=your-secret-key
```
SECRET_KEY можно сгенерировать командой:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
### 5. Проведите миграции:
```bash
python manage.py migrate
```
### 6. Запустите сервер:
```bash
python manage.py runserver
```
Перейди в браузер:
```
http://127.0.0.1:8000/
```
## Тестирование
Для запуска всех тестов (модели, формы, представления):
```bash
pytest
```
Общее покрытие тестами 90%.
Чтобы посмотреть покрытие тестами (test coverage):
```bash
pytest --cov=ads --cov-report=term-missing
```
Покрыты тестами:
- базовые сценарии (GET/POST, login/logout)
- позитивные и негативные кейсы (валидность, доступность, права)
- пограничные случаи (несуществующие объявления, чужие объявления)
- проверка форм и результатов (redirects, status codes, содержимое ответа)

## Примечания
* В проекте используется встроенная система пользователей Django
* Обмен возможен только между объявлениями разных пользователей
* Валидация форм и авторизация доступа реализованы
* REST API пока не реализован, но может быть добавлен через Django REST Framework
