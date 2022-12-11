# Telegram-бот для API сервиса Практикум.Домашка
## Описание
Telegram-бота, который обращатся к API сервиса Практикум.Домашка и узнаёт статус домашней работы: взята ли домашка в ревью, проверена ли она, а если проверена — то принял её ревьюер или вернул на доработку.
## Функционал
* раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы;
* при обновлении статуса анализирует ответ API и отправляет соответствующее уведомление в Telegram;
* логирует свою работу и сообщает о важных проблемах сообщением в Telegram.
## Использованные технологии/пакеты
* Python 3.7
* python-dotenv 0.19.0
* python-telegram-bot 13.7
* requests 2.26.0
## Установка
* Клонировать проект
```
git clone https://github.com/GritsenkoSerge/homework_bot.git
```
* Перейти в директорию homework_bot
```
cd homework_bot
```
* Создать окружение
```
python -m venv venv
```
* Активировать окружение
```
. venv/Scripts/activate
```
* Установить зависимости
```
pip install -r requirements.txt
```
* Создать файл .env с переменными окружения (при необходимости изменить)
```
PRACTICUM_TOKEN = practicum_token > .env
TELEGRAM_TOKEN = tg_token >> .env
TELEGRAM_CHAT_ID = chat_id >> .env
```
Здесь  
practicum_token - токен [API сервиса Практикум.Домашка](https://code.s3.yandex.net/backend-developer/%D0%9F%D1%80%D0%B0%D0%BA%D1%82%D0%B8%D0%BA%D1%83%D0%BC.%D0%94%D0%BE%D0%BC%D0%B0%D1%88%D0%BA%D0%B0%20%D0%A8%D0%BF%D0%B0%D1%80%D0%B3%D0%B0%D0%BB%D0%BA%D0%B0.pdf);  
tg_token - токен [Telegram-бота](https://core.telegram.org/bots#how-do-i-create-a-bot), от чьего имени будут отправляться сообщения;  
chat_id - [идентификатор Telegam-чата](https://t.me/getmyid_bot), в который будут отправляться сообщения.
* Запустить проект
```
python homework_bot.py
```

