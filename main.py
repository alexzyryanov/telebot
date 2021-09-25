import telebot
import sqlite3
import datetime


bot = telebot.TeleBot("token")
date_now = datetime.datetime.now().strftime("%d.%m.%y")
all_commands = ["start", "add", "add_new", "show", "help"]


@bot.message_handler(commands=all_commands)
def hear_command(message):
    if message.text == "/start":
        start_page = f"Hello {message.from_user.first_name}\n" \
                     "\n" \
                     "/add - Add reps and weight\n" \
                     "/add_new - Add a new exercise\n" \
                     "/show - Show history\n" \
                     "/help - All commands"
        bot.send_message(message.chat.id, start_page)

    elif message.text == "/add":
        bot.send_message(message.chat.id, "Chose exercise", reply_markup=save_add(message))

    elif message.text == "/add_new":
        bot.send_message(message.chat.id, "Enter a name for the new exercise\n"
                                          "\n"
                                          "/cancel - Cancel enter")
        bot.register_next_step_handler(message, add_new_exercise)

    elif message.text == "/show":
        bot.send_message(message.chat.id, "Exercises", reply_markup=show_diary(message))

    elif message.text == "/help":
        help_page = "All commands\n" \
                    "\n" \
                    "/add - Add reps and weight\n" \
                    "/add_new - Add a new exercise\n" \
                    "/show - Show history\n" \
                    "/help - All commands"
        bot.send_message(message.chat.id, help_page)


@bot.message_handler(content_types=["text"])
def hear_text(message):
    connect_db = sqlite3.connect("bot_db.sqlite3")
    cursor = connect_db.cursor()
    param = f""" SELECT exercise FROM bot_users WHERE id_user = {message.from_user.id} """
    check = [i[0] for i in cursor.execute(param)]
    cursor.close()
    connect_db.close()

    if message.text in check:
        exercise = message.text
        bot.send_message(message.chat.id, "Add your reps", reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, save_add_r, exercise)


@bot.callback_query_handler(func=lambda call: True)
def hear_callback(call):
    if "show_diary_" in call.data:
        exercise = call.data[11::]
        show_about = f"{exercise}\n" \
                     "\n"

        connect_db = sqlite3.connect("bot_db.sqlite3")
        cursor = connect_db.cursor()
        param = f""" SELECT date, repeat, weight FROM bot_users 
                     WHERE (id_user = {call.from_user.id} AND exercise = '{exercise}') 
                     AND (repeat NOT null AND weight NOT null) """
        for i in cursor.execute(param):
            show_about += f"Date - {i[0]}\n" \
                          f"Reps - {i[1]}\n" \
                          f"Weight - {i[2]}\n" \
                          "\n"
        cursor.close()
        connect_db.close()

        bot.send_message(call.message.chat.id, show_about)
        bot.send_message(call.message.chat.id, "/help - All commands")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="History", reply_markup=None)


def save_add(message):
    connect_db = sqlite3.connect("bot_db.sqlite3")
    cursor = connect_db.cursor()
    item_from_db = []
    for i in cursor.execute(f""" SELECT exercise FROM bot_users 
                                 WHERE id_user = {message.from_user.id} AND date NOT null """):
        if i[0] not in item_from_db:
            item_from_db.append(i[0])
    cursor.close()
    connect_db.close()

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    all_button = [telebot.types.InlineKeyboardButton(text=i) for i in item_from_db]
    keyboard.add(*all_button)
    return keyboard


def save_add_r(message, exercise):
    reps = message.text
    bot.send_message(message.chat.id, "Add your weights")
    bot.register_next_step_handler(message, save_add_w, exercise, reps)


def save_add_w(message, exercise, reps):
    weight = message.text

    connect_db = sqlite3.connect("bot_db.sqlite3")
    cursor = connect_db.cursor()
    cursor.execute("""INSERT INTO bot_users VALUES (?, ?, ?, ?, ?)""",
                   (message.from_user.id, exercise, date_now, reps, weight))
    connect_db.commit()
    cursor.close()
    connect_db.close()

    bot.send_message(message.chat.id, "Your\n"
                                      "\n"
                                      f"exercise - {exercise}\n"
                                      f"reps - {reps}\n"
                                      f"weights - {weight}\n"
                                      "save\n"
                                      "\n"
                                      "/help - All commands")


def add_new_exercise(message):
    if message.text == "/cancel":
        bot.disable_save_next_step_handlers()
        cancel_page = "Enter canceled\n" \
                      "\n" \
                      "/add - Add reps and weight\n" \
                      "/add_new - Add a new exercise\n" \
                      "/show - Show history\n" \
                      "/help - All commands"
        bot.send_message(message.chat.id, cancel_page)
    else:
        connect_db = sqlite3.connect("bot_db.sqlite3")
        cursor = connect_db.cursor()
        cursor.execute("""INSERT INTO bot_users VALUES (?, ?, ?, ?, ?)""",
                       (message.from_user.id, message.text, date_now, None, None))
        connect_db.commit()
        cursor.close()
        connect_db.close()

        add_exercise_page = f"Exercise {message.text} added\n" \
                            "\n" \
                            "/add - Add reps and weight\n" \
                            "/add_new - Add a new exercise\n" \
                            "/show - Show history\n" \
                            "/help - All commands"
        bot.send_message(message.chat.id, add_exercise_page)


def show_diary(message):
    connect_db = sqlite3.connect("bot_db.sqlite3")
    cursor = connect_db.cursor()
    item_from_db = []
    for i in cursor.execute(f""" SELECT exercise FROM bot_users 
                                 WHERE id_user = {message.from_user.id} 
                                 AND (repeat NOT null AND weight NOT null) """):
        if i[0] not in item_from_db:
            item_from_db.append(i[0])
    cursor.close()
    connect_db.close()

    keyboard = telebot.types.InlineKeyboardMarkup()
    all_button = [telebot.types.InlineKeyboardButton(text=i, callback_data=f"show_diary_{i}") for i in item_from_db]
    keyboard.add(*all_button)
    return keyboard


def main():
    connect_db = sqlite3.connect("bot_db.sqlite3")
    cursor = connect_db.cursor()
    cursor.execute(""" CREATE TABLE IF NOT EXISTS bot_users 
        (id_user INT, exercise TEXT, date TEXT, repeat TEXT, weight TEXT) """)
    connect_db.commit()
    cursor.close()
    connect_db.close()

    bot.polling()


if __name__ == "__main__":
    main()
