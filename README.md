# WeatherBot

WeatherBot - это бот для Telegram, написанный на Python, который предоставляет информацию о погоде для города Тольятти. Он использует API OpenWeatherMap для получения данных о погоде и отправки их пользователям по запросу.

## Функции
- Запрашивает данные о погоде в реальном времени для Тольятти.
- Предоставляет информацию, такую как температура, влажность, скорость ветра, давление, восход и закат солнца и многое другое.
- Поддерживает две команды Telegram: `/start` для начала взаимодействия и `/weather` для получения последнего обновления погоды.

## Предварительные требования
Перед запуском WeatherBot убедитесь, что у вас есть следующее:
- Установлен Python 3.x на вашем компьютере.
- Токен API OpenWeatherMap. Вы можете получить его, зарегистрировавшись на [OpenWeatherMap](https://openweathermap.org/).
- Токен бота Telegram. Создайте бота в Telegram и получите токен у [BotFather](https://core.telegram.org/bots#botfather).

## Установка:

Клонируйте репозиторий и перейдите в него в командной строке:

```
git clone git@github.com:andrew12022/weather_bot.git
```

```
cd weather_bot
```

Cоздайте и активируйте виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

Установите зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Создайте файл `.env` в той же директории, что и `weather_bot.py`, и добавьте свои токены API:

```.env
WEATHER_TOKEN=ваш_токен_openweathermap_api
BOT_TOKEN=ваш_токен_telegram_bot
```

Измените переменную `CITY` в файле `weather_bot.py`, чтобы указать желаемое местоположение:

```python
CITY = 'ваш_город'
```

Также не забудьте изменить строчку № 92 в файле `weather_bot.py`, чтобы данные о времени отображались правильно:

```python
current_timezone = pytz.timezone('Europe/ваш_регион_или_город')
```

Запустите бота с помощью следующей команды:

```
python weather_bot.py
```

## Использование
- Начните чат с вашим ботом в Telegram.
- Отправьте команду `/start`, чтобы начать взаимодействие и получить приветственное сообщение.
- Чтобы получить последнее обновление погоды, отправьте команду `/weather`.

## Обработка ошибок
WeatherBot включает обработку ошибок для потенциальных проблем, таких как отсутствие токенов API или неудачные запросы к API. Сообщения об ошибках будут зарегистрированы в консоли для устранения неполадок.

## Зависимости
- [requests](https://pypi.org/project/requests/): используется для выполнения HTTP-запросов к API OpenWeatherMap.
- [python-dotenv](https://pypi.org/project/python-dotenv/): помогает загружать переменные окружения из файла `.env`.
- [python-telegram-bot](https://pypi.org/project/python-telegram-bot/): обертка на Python для Telegram Bot API.

## Автор
- [andrew12022](https://github.com/andrew12022)
