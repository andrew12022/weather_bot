import datetime
import logging
import os
import sys
from http import HTTPStatus

import requests

from telegram.ext import CommandHandler, Updater

from dotenv import load_dotenv

load_dotenv()


WEATHER_TOKEN = os.getenv('WEATHER_TOKEN')
BOT_TOKEN = os.getenv('BOT_TOKEN')

CITY = 'Тольятти'
ENDPOINT = 'https://api.openweathermap.org/data/2.5/weather'
CODE_TO_SMILE = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
}


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')
handler.setFormatter(formatter)


def check_tokens():
    """."""
    logger.debug('Проверка наличия всех токенов')
    return all([WEATHER_TOKEN, BOT_TOKEN])


def get_new_weather():
    """."""
    params = {
        'q': CITY,
        'appid': WEATHER_TOKEN,
        'units': 'metric',
        'lang': 'ru',
    }
    logger.debug(f'Начало отправления запроса к API: {ENDPOINT}')
    try:
        response = requests.get(
            ENDPOINT,
            params=params,
        )
    except Exception as error:
        error_message = (
            f'Произошел сбой при запросе: {error}.'
            f'Запрос выглядел таким образом: {ENDPOINT}, {params}.'
        )
        logger.error(error_message)
    else:
        logger.debug('Ответ на запрос успешно отправлен')
    if response.status_code == HTTPStatus.OK:
        logger.debug('Успешный ответ от API')
    else:
        logger.error(
            'Неуспешный ответ от API. '
            f'Код ответа: {response.status_code}'
        )
    response = response.json()
    main = response.get('main')
    wind = response.get('wind')
    sys = response.get('sys')
    temp = main.get('temp')
    feels_like = main.get('feels_like')
    humidity = main.get('humidity')
    pressure = main.get('pressure')
    speed = wind.get('speed')
    format = "%H:%M"
    now = datetime.datetime.now().strftime(format)
    sunrise = datetime.datetime.fromtimestamp(sys.get('sunrise'))
    sunset = datetime.datetime.fromtimestamp(sys.get('sunset'))
    length = sunset - sunrise
    hours = length.seconds // 3600
    minutes = (length.seconds % 3600) // 60
    wd = CODE_TO_SMILE[response['weather'][0]['main']]
    text = (
        f'Погода в городе Тольятти:\n'
        f'Время: {now}\n'
        f'Температура воздуха: {int(temp)}°C {wd}\n'
        f'Ощущается как: {int(feels_like)}°C\n'
        f'Влажность: {humidity}%\n'
        f'Ветер: {int(speed)} м/с\n'
        f'Давление: {pressure} мм рт. ст.\n'
        f'Восход солнца: {sunrise.strftime(format)}\n'
        f'Закат солнца: {sunset.strftime(format)}\n'
        f'Продолжительность дня: {hours} часов {minutes} минут'
    )
    return text


def new_weather(update, context):
    """."""
    username = update.effective_user.username
    logger.info(f'Получена команда /weather от пользователя: {username}')
    chat = update.effective_chat
    try:
        context.bot.send_message(chat.id, get_new_weather())
    except Exception as error:
        logger.error(f'Ошибка при отправке сообщения в Telegram: {error}')
    else:
        logger.info(f'Сообщение успешно отправлено пользователю: {username}')


def start_up(update, context):
    """."""
    username = update.effective_user.username
    logger.info(f'Получена команда /start от пользователя: {username}')
    chat = update.effective_chat
    try:
        context.bot.send_message(
            chat_id=chat.id,
            text=(f'Привет, {username}.\n'
                  'Я WeatherBot и могу сказать какая погода на улице сейчас.\n'
                  'Она будет выведена после этого сообщения.\n'
                  'Чтобы заново запросить информацию о погоде '
                  'нужно всего лишь написать команду: /weather'),
        )
        context.bot.send_message(chat.id, get_new_weather())
    except Exception as error:
        logger.error(f'Ошибка при отправке сообщения в Telegram: {error}')
    else:
        logger.info(f'Сообщение успешно отправлено пользователю: {username}')


def main():
    """."""
    if not check_tokens():
        error_message = 'Программа была остановлена из за отсутствия токенов'
        logger.critical(error_message)
        sys.exit()
    logger.info('WeatherBot начал работать')
    updater = Updater(token=BOT_TOKEN)
    updater.dispatcher.add_handler(CommandHandler('start', start_up))
    updater.dispatcher.add_handler(CommandHandler('weather', new_weather))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - [%(levelname)s] - %(message)s',
    )
    main()
    logger.info('WeatherBot закончил работать')
