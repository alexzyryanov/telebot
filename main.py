import telebot
import sqlite3
import datetime
from tok import *


bot = telebot.TeleBot(token)

date_now = datetime.datetime.now().strftime("%d.%m.%y")
all_commands = ["start", "home", "diary", "add", "add_new", "show", "help"]


@bot.message_handler(commands=all_commands)
def hear_command(message):
    if message.text == "/start":
        connect_db = sqlite3.connect("tele_bot.db")
        cursor = connect_db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS bot_users
                    (id_user INT, workouts TEXT, date TEXT, reps TEXT, weights TEXT)""")
        connect_db.commit()
        cursor.execute("""INSERT INTO bot_users VALUES (?, ?, ?, ?, ?)""",
                       (message.from_user.id, None, date_now, None, None))
        connect_db.commit()
        cursor.close()
        connect_db.close()

        start_page = f"Привет {message.from_user.first_name}\n" \
                     "/home - Домашняя страница\n" \
                     "/help - Все команды бота"

        bot.send_message(message.chat.id, start_page)

    elif message.text == "hello":
        bot.send_message(message.chat.id, "hailo")

    elif message.text == "/home":
        home_page = "Домашняя страница\n" \
                    "/diary - Дневник тренировок"
        bot.send_message(message.chat.id, home_page)

    elif message.text == "/diary":
        diary_page = "Дневник тренировок\n" \
                     "/add - Добавить повторения и вес\n" \
                     "/add_new - Добавить новое упражнение\n" \
                     "/show - Показать упражнения в дневнике"
        bot.send_message(message.chat.id, diary_page)

    elif message.text == "/add":
        pass

    elif message.text == "/add_new":
        bot.send_message(message.chat.id, "Введите название нового упражнения\n"
                                          "/cancel - отменить ввод")
        bot.register_next_step_handler(message, save_add_new)

    elif message.text == "/show":
        bot.send_message(message.chat.id, "Упражнения", reply_markup=show_diary(message))

    elif message.text == "/help":
        help_page = "Все команды бота\n" \
                    "/home - Домашняя страница\n" \
                    "/diary - Дневник тренировок\n" \
                    "/add - Добавить повторения и вес\n" \
                    "/add_new - Добавить новое упражнение\n" \
                    "/show - Показать упражнения в дневнике\n" \
                    "/help - Все команды бота"
        bot.send_message(message.chat.id, help_page)


def save_add_new(message):
    if message.text == "/cancel":
        bot.disable_save_next_step_handlers()
        bot.send_message(message.chat.id, "Ввод отменен")
    else:
        connect_db = sqlite3.connect("tele_bot.db")
        cursor = connect_db.cursor()
        cursor.execute("""INSERT INTO bot_users VALUES (?, ?, ?, ?, ?)""",
                       (message.from_user.id, message.text, date_now, None, None))
        connect_db.commit()
        cursor.close()
        connect_db.close()
        bot.send_message(message.chat.id, f"Упражнение {message.text} добавлено\n"
                                          "/diary - Дневник тренировок\n"
                                          "/help - Все команды бота")


def show_diary(message):
    connect_db = sqlite3.connect("tele_bot.db")
    cursor = connect_db.cursor()
    item_from_bd = []
    param = f"""SELECT workouts FROM bot_users WHERE id_user = {message.from_user.id}"""
    for i in cursor.execute(param):
        if type(i[0]) == str:
            item_from_bd.append(i[0])
        else:
            pass
    cursor.close()
    connect_db.close()
    keyboard = telebot.types.InlineKeyboardMarkup()
    all_button = [telebot.types.InlineKeyboardButton(text=i, callback_data=f"show_diary_{i}") for i in item_from_bd]
    keyboard.add(*all_button)
    return keyboard


@bot.message_handler(content_types=["text"])
def asdasd(message):
    if message.text == "hello":
        bot.send_message(message.chat.id, "hailo")


@bot.callback_query_handler(func=lambda call: True)
def hear_callback(call):
    if "show_diary_" in call.data:
        call_data = call.data[11::]
        show_about = f"{call_data}\n" \
                     "\n"

        connect_db = sqlite3.connect("tele_bot.db")
        cursor = connect_db.cursor()
        param = f"""SELECT * FROM bot_users WHERE id_user = {call.from_user.id}"""
        for i in cursor.execute(param):
            if i[1] == call_data:
                show_about += f"Дата - {i[2]}\n" \
                              f"Повторения - {i[3]}\n" \
                              f"Вес - {i[4]}\n" \
                              "\n"
        cursor.close()
        connect_db.close()
        bot.send_message(call.message.chat.id, show_about)

    else:
        pass


def main():
    bot.polling()


if __name__ == "__main__":
    main()
