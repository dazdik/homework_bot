class ErrorHomeWork(Exception):
    """Статус домашней работы отличается от ожидаемого."""

    pass


class TelegramMessageError(Exception):
    """Сбой при отправке сообщения в телеграм."""

    pass




class RequestApiError(Exception):
    """Ошибка при запросе к API."""

    pass
