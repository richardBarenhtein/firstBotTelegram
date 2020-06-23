from random import randint

from telebot import types
import telebot

import config
import schedule
import time

bot = telebot.TeleBot(config.TOKEN)
times = {"Утром": ["06:00", "07:00", "08:00", "09:00", "10:00", "11:00"], "Днем": ["12:00", "13:00", "14:00",
                                                                                   "15:00", "16:00", "17:00"],
         "Вечером": ["18:00", "19:00", "20:00", "21:00", "22:00", "23:00"]}

saved_times = []


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.first_name is not None:
        hello_message = "%s, %s, %s" % ('Приветствую', message.from_user.first_name, 'я бот,который будет отправлять '
                                                                                     'вам рандомные цитаты мудрецов. '
                                                                                     'Напишите /random для '
                                                                                     'продолжения')
    else:
        hello_message = "%s, %s, %s" % ('Приветствую', message.from_user.username, 'я бот,который будет отправлять '
                                                                                   'вам рандомные цитаты мудрецов. '
                                                                                   'Напишите /help, чтобы увидеть '
                                                                                   'все команды')

    bot.send_message(message.chat.id, hello_message)


@bot.message_handler(commands='help')
def send_all_commands(message):
    bot.send_message(message.chat.id, '*Команды:* \n/random - получить рандомную цитату\n/set - установить время для '
                                      'отправки пожелания\n/check - проверить установленное время для пожелания\n'
                                      '/reset - переустановить время для отправки пожелания\n/time - установить время для '
                                      'отправки пожелания вручную', parse_mode='markdown')


@bot.message_handler(commands=['random'])
def send_random_quote(message):
    Quotes = [
        "Иногда момент, который ты так долго ждал, приходит в самое неподходящее время...\nЦитата из фильма \"Клиника\"",
        'Ничто так не выдает человека, как то, над чем он смеётся.\nИоганн Вольфганг фон Гёте',
        'Каждый живет, как хочет, и расплачивается за это сам.\nОскар Уайльд\nhttps://ru.wikipedia.org/wiki/Уайльд,_Оскар',
        'Иногда хватает мгновения, чтобы забыть жизнь, а иногда не хватает жизни, чтобы забыть мгновение.\nДжим Моррисон',
        'Самой большой ошибкой, которую вы можете совершить в своей жизни, является постоянная боязнь ошибаться.\nЭлберт Грин Хаббард',
        'Если вы хотите иметь то, что никогда не имели, вам придётся делать то, что никогда не делали.\nКоко Шанель',
        'Такой вот парадокс: мы совершаем подвиги для тех, кому до нас нет никакого дела, а любят нас те, кому мы нужны и без всяких подвигов...\nПроисхождение неизвестно',
        'Самое худшее, когда нужно ждать и не можешь ничего сделать. От этого можно сойти с ума.\nЭрих Мария Ремарк']
    random_quote = randint(0, len(Quotes) - 1)
    bot.send_message(message.chat.id, Quotes[random_quote])


def send_specific_message(message):
    msg = 'Ричард тебя любит и желает тебе удачного дня!'
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['set', 'reset'])
def time_manager(message):
    if message.text == "/reset":
        saved_times.clear()
    if not saved_times:
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        for keys in times.keys():
            if keys == "Утром":
                callback_button1 = types.InlineKeyboardButton(text=keys, callback_data="clicked_morning")
            elif keys == "Днем":
                callback_button1 = types.InlineKeyboardButton(text=keys, callback_data="clicked_afternoon")
            else:
                callback_button1 = types.InlineKeyboardButton(text=keys, callback_data="clicked_evening")
            keyboard.row(callback_button1)

        bot.send_message(message.chat.id, "<b>Выберите время суток..</b>", parse_mode="HTML", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Вы можете добавить только одно время для отсылки сообщения. Используйте "
                                          "команду /reset, чтобы переустановить время")


@bot.message_handler(commands=['check'])
def get_list_of_saved_times(message):
    index = 0

    if saved_times:
        string_of_all_set_times = "Установленное время для отправки сообщения: " + saved_times[0]

        bot.send_message(message.chat.id, string_of_all_set_times)

    else:
        bot.send_message(message.chat.id, "Вы еще не добавили время для отправки сообщения! Вы можете добавить "
                                          "использую команду /set")


@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    cid = call.message.chat.id
    flag = True
    key_in_dict = ""

    bot.edit_message_reply_markup(cid, call.message.message_id, reply_markup=None)

    if call.data == "clicked_morning":
        key_in_dict = "Утром"
    elif call.data == "clicked_afternoon":
        key_in_dict = "Днем"
    elif call.data == "clicked_evening":
        key_in_dict = "Вечером"
    else:
        scheduled_time = call.data
        saved_times.append(scheduled_time)
        schedule.every().day.at(scheduled_time).do(send_specific_message, call.message)
        bot.send_message(cid, "%s *%s*" % ("Устанавлено время на", scheduled_time), parse_mode="markdown")

        while flag:
            schedule.run_pending()
            time.sleep(1)

            if not saved_times:
                flag = False

    if key_in_dict != "":
        bot.send_message(cid, "Вы выбрали " + "*" + key_in_dict+ "*", parse_mode="markdown")
        keyboard = types.InlineKeyboardMarkup()

        for value in times[key_in_dict]:
            callback_button = types.InlineKeyboardButton(text=value, callback_data=value)
            keyboard.row(callback_button)

        bot.send_message(cid, "<b>Теперь выберите час, когда вы хотите получить сообщение..</b>", parse_mode="HTML",
                         reply_markup=keyboard)


@bot.message_handler(commands=['time'])
def set_time(message):
    bot.send_message(message.chat.id, "Введите время в формате HH:MM(пример 00:00)")


@bot.message_handler(content_types=['text'])
def change_time(message):
    scheduled_time = message.text
    schedule.every().day.at(scheduled_time).do(send_specific_message, message)
    bot.send_message(message.chat.id, "%s %s" % ("Устанавлено время на", scheduled_time))

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    bot.infinity_polling()
