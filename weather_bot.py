import datetime
import logging
import os
import sys
from http import HTTPStatus
from urllib.error import HTTPError

import pytz
import requests
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler

from exceptions import TelegramAPIError, WeatherAPIError

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
    """Проверка наличия всех токенов."""
    logger.debug('Проверка наличия всех токенов')
    return all([WEATHER_TOKEN, BOT_TOKEN])


def fetch_weather_data():
    """Запрос данных о погоде."""
    params = {
        'q': CITY,
        'appid': WEATHER_TOKEN,
        'units': 'metric',
        'lang': 'ru',
    }
    logger.debug(f'Начало отправления запроса к API: {ENDPOINT}')

    try:
        response = requests.get(ENDPOINT, params=params)
        response.raise_for_status()
    except (requests.exceptions.RequestException, HTTPError) as error:
        raise WeatherAPIError(f'Ошибка при запросе к API погоды: {error}')
    except Exception as error:
        error_message = (
            f'Произошел сбой при запросе: {error}.'
            f'Запрос выглядел таким образом: {ENDPOINT}, {params}.'
        )
        logger.error(error_message)
    else:
        logger.debug('Запрос успешно отправлен')

    if response.status_code == HTTPStatus.OK:
        logger.debug('Успешный ответ от API')
    else:
        logger.error(
            'Неуспешный ответ от API. '
            f'Код ответа: {response.status_code}'
        )

    return response.json()


def process_weather_data(response):
    """Обработка данных о погоде."""
    main = response.get('main')
    wind = response.get('wind')
    sys_info = response.get('sys')

    temp = main.get('temp')
    feels_like = main.get('feels_like')
    humidity = main.get('humidity')
    pressure = main.get('pressure')
    speed = wind.get('speed')

    current_timezone = pytz.timezone('Europe/Samara')
    format = "%H:%M"
    now = datetime.datetime.now(current_timezone).strftime(format)
    sunrise = datetime.datetime.fromtimestamp(
        sys_info.get('sunrise'),
        tz=pytz.UTC,
    )
    sunset = datetime.datetime.fromtimestamp(
        sys_info.get('sunset'),
        tz=pytz.UTC,
    )
    sunrise_current = sunrise.astimezone(current_timezone).strftime(format)
    sunset_current = sunset.astimezone(current_timezone).strftime(format)
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
        f'Восход солнца: {sunrise_current}\n'
        f'Закат солнца: {sunset_current}\n'
        f'Продолжительность дня: {hours} часов {minutes} минут'
    )

    return text


def get_new_weather():
    """Получение и обработка данных о погоде."""
    try:
        weather_data = fetch_weather_data()
        return process_weather_data(weather_data)
    except WeatherAPIError as error:
        error_message = (
            f'Произошла ошибка при получении данных о погоде: {error}.'
        )
        logger.error(error_message)


async def new_weather(update, context):
    """Обработка команды /weather."""
    username = update.effective_user.username
    logger.info(f'Получена команда /weather от пользователя: {username}')
    chat = update.effective_chat
    weather_message = get_new_weather()

    try:
        await context.bot.send_message(chat.id, weather_message)
    except Exception as error:
        logger.error(f'Ошибка при отправке сообщения в Telegram: {error}')
    else:
        logger.info(f'Сообщение успешно отправлено пользователю: {username}')


async def start_up(update, context):
    """Обработка команды /start."""
    username = update.effective_user.username
    logger.info(f'Получена команда /start от пользователя: {username}')
    chat = update.effective_chat

    try:
        await context.bot.send_message(
            chat_id=chat.id,
            text=(f'Привет, {username}.\n'
                  'Я WeatherBot и могу сказать какая погода на улице сейчас.\n'
                  'Она будет выведена после этого сообщения.\n'
                  'Чтобы заново запросить информацию о погоде '
                  'нужно всего лишь написать команду: /weather'),
        )
        weather_message = get_new_weather()
        await context.bot.send_message(chat.id, weather_message)
    except Exception as error:
        logger.error(f'Ошибка при отправке сообщения в Telegram: {error}')
    else:
        logger.info(f'Сообщение успешно отправлено пользователю: {username}')


def main():
    """Основная функция бота."""
    if not check_tokens():
        error_message = 'Программа была остановлена из-за отсутствия токенов'
        logger.critical(error_message)
        sys.exit()
    logger.info('WeatherBot начал работать')
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start_up))
    application.add_handler(CommandHandler('weather', new_weather))
    application.run_polling()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - [%(levelname)s] - %(message)s',
    )
    try:
        main()
    except (WeatherAPIError, TelegramAPIError) as error:
        logger.error(f'Произошла ошибка: {error}')
    logger.info('WeatherBot закончил работать')
