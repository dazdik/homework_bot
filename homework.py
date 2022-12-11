import logging
import os
import time
from http import HTTPStatus
from json.decoder import JSONDecodeError
from sys import stdout

import requests
import telegram
from dotenv import load_dotenv
from telegram import TelegramError

from exceptions import ErrorHomeWork, RequestApiError, TelegramMessageError

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_tokens() -> bool:
    """Функция check_tokens.
    Проверяет доступность переменных окружения,
    которые необходимы для работы программы.
    """
    env_tokens = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
    }
    for k, v in env_tokens.items():
        if v is None:
            logger.critical(f'{k} токен отсутствует')
            return False
    return True


def send_message(bot: telegram.Bot, message: str) -> bool:
    """Функция send_message отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug('Сообщение успешно отправлено')

    except TelegramError as e:
        logger.error(e)
        raise TelegramMessageError('при отправке сообщения из'
                                   'бота возникает ошибка')


def get_api_answer(timestamp: int) -> dict:
    """
    Функция get_api_answer делает запрос к эндпоинту API-сервиса.

    В качестве параметра в функцию передается временная метка.
    """
    payload = {'from_date': timestamp}
    arguments = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': payload,
    }
    try:
        response = requests.get(**arguments)
        if response.status_code != HTTPStatus.OK:
            logger.error('Эндопоинт недоступен!')
            message = (
                f'Получен {response.status_code} код ответа сервера: '
                f'{response.reason}'
            )
            raise requests.HTTPError(message)
        logger.debug('Запрос прошел успешно: код ответа 200')
        return response.json()

    except JSONDecodeError as e:
        raise e(
            'Ошибка преобразования типа данных')

    except requests.RequestException as e:
        raise RequestApiError(f'Ошибка при запросе к API: {e}')


def check_response(response: dict) -> list:
    """
    Функция check_response.
    Проверяет ответ API на соответствие документации.
    """
    if not isinstance(response, dict):
        logger.error('В ответе должен быть словарь!')
        raise TypeError('Требуемый тип данных — словарь.')

    try:
        homeworks = response['homeworks']
    except KeyError as e:
        raise e('Ключ homeworks отсутствует')

    if 'current_date' not in response:
        logger.error('Ключ current_date отсутствует')
        raise KeyError('Ключ current_date отсутствует')

    if not isinstance(homeworks, list):
        logger.error('homeworks должен быть представлен в виде списка')
        raise TypeError('Список ДЗ должен быть представлен в виде списка')

    current_date = response['current_date']

    if not isinstance(current_date, int):
        logger.error('Данные current_date получены не в виде целого числа')
        raise TypeError('Данные current_date получены не в виде целого числа')

    return homeworks


def parse_status(homework: dict) -> str:
    """
    Функция parse_status.
    Извлекает из информации о конкретной домашней работе статус этой работы.
    """
    keys = ('homework_name', 'status',)
    for k in keys:
        if k not in homework:
            raise KeyError(f'{homework} не содержит {k}')

    homework_name = homework['homework_name']
    homework_status = homework['status']

    if homework_status not in HOMEWORK_VERDICTS:
        logger.error('Неверный ключ для статуса ДЗ')
        raise ErrorHomeWork('Неверный ключ для статуса ДЗ')

    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        raise SystemExit('Работа бота бессмысленна')

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    old_message = ''

    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            if homework:
                message = parse_status(homework[0])
            else:
                logger.debug('Статус домашней работы не поменялся')
                message = 'Нет обновлений'
            if message != old_message:
                send_message(bot, message)
                old_message = message
                timestamp = response.get('current_date')

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if message != old_message:
                send_message(bot, message)
                old_message = message

        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
