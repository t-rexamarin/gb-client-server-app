import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler
from common.variables import *

LOGGER_NAME = 'server'

# задаем форматирование сообщений
SERVER_FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

# выводим все в stderr
STREAM_HANDLER = logging.StreamHandler(sys.stderr)
# подключаем форматирование к обработчику
STREAM_HANDLER.setFormatter(SERVER_FORMATTER)
# события не ниже ошибок (ERROR, CRITICAL)
STREAM_HANDLER.setLevel(LOGGING_LEVEL)

# путь до папки исполняемого файла
LOG_PATH = os.path.dirname(os.path.abspath(__file__))
# путь до файла логов
LOG_PATH = os.path.join(LOG_PATH,
                        'server_logs',
                        'server_log.txt')
# задаем файловый обработчик логирования, с ротацией 1 день в полночь
LOG_FILE = logging.handlers.TimedRotatingFileHandler(LOG_PATH,
                                                     encoding='utf-8',
                                                     interval=1,
                                                     when='midnight')
LOG_FILE.setFormatter(SERVER_FORMATTER)

# создаем новый экземпляр, т.к. ранее такой логгер не определялся
LOGGER = logging.getLogger(LOGGER_NAME)
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LOGGING_LEVEL)


# отладка
if __name__ == '__main__':
    LOGGER.critical('Критическая ошибка')
    LOGGER.error('Ошибка')
    LOGGER.debug('Отладочная информация')
    LOGGER.info('Информационное сообщение')
