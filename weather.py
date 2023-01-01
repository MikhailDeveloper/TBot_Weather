import os
import requests
import telebot
from telebot import types
from geopy.geocoders import Nominatim

bot = telebot.TeleBot(os.environ.get('TELEGRAM_KEY'))

def make_url(city):
    # в URL задаём город, в котором узнаем погоду
    return f'http://wttr.in/{city}'

def make_parameters():
    params = {
        'format': 2,  # погода одной строкой
        'M': ''  # скорость ветра в "м/с"
    }
    return params

def what_weather(city):
    try:
        response = requests.get(make_url(city), make_parameters())
    except requests.ConnectionError:
        return '<сетевая ошибка>'
    if(response.status_code == 200):
        return response.text
    else:
        return '<ошибка в названии города>'

# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(m, res=False):
        # Добавляем две кнопки
        markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1=types.KeyboardButton("Геолокация", request_location=True)
        item2=types.KeyboardButton("Город")
        markup.add(item1)
        markup.add(item2)
        bot.send_message(m.chat.id, 'Нажми: \nГеолокация — для получения информации о погоде по текущему местуположению \nГород — для получения информации о погоде по выбранному городу ',  reply_markup=markup)

#Получаю локацию
geolocator = Nominatim(user_agent = "WhatWeatherLocBot")
@bot.message_handler(content_types=['location'])
def location (message):
    if message.location is not None:
        location = geolocator.reverse('{} {}'.format(message.location.latitude, message.location.longitude))
        handle_text(message, location.raw['address']['city'])

# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(message, town=''):
    if (town != ''):
        msg=town
    else:
        msg=message.text.strip()
    weather=what_weather(msg)
    if msg == 'Город' :
        bot.send_message(message.chat.id,'Введите название города')
    elif weather == '<сетевая ошибка>' :
        bot.send_message(message.chat.id,'Ошибка подключения к срверу, попробуйте еще раз')
    elif weather == '<ошибка в названии города>' :
         bot.send_message(message.chat.id,'Запрашиваемый город не найден')
    else:
        bot.send_message(message.chat.id, f'Погода в городе {msg}: {weather}')

# Запускаем бота
bot.polling(none_stop=True, interval=0)

