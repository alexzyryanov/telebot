from tok import token
import telebot
import sqlite3
import datetime


bot = telebot.TeleBot(token)

date_now = datetime.datetime.now().strftime("%d.%m.%y")
all_commands = ["start", "home", "diary", "add", "add_new", "show", "help"]


@bot.message_handler(commands=all_commands)
def hear_command(message):
    if message.text == "/start":
        connect_db = sqlite3.connect("tele_bot.db")
        cursor = connect_db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS bot_users
                                (id_user INT, exercise TEXT, date TEXT, rep TEXT, weight TEXT)""")
        connect_db.commit()
        cursor.execute("""INSERT INTO bot_users VALUES (?, ?, ?, ?, ?)""",
                       (message.from_user.id, None, date_now, None, None))
        connect_db.commit()
        cursor.close()
        connect_db.close()

        start_page = f"Hello {message.from_user.first_name}\n" \
                     "/home - Home\n" \
                     "/help - All commands"

        bot.send_message(message.chat.id, start_page)

    elif message.text == "/home":
        home_page = "Home\n" \
                    "/diary - Diary"
        bot.send_message(message.chat.id, home_page)

    elif message.text == "/diary":
        diary_page = "Diary\n" \
                     "/add - \n" \
                     "/add_new - Add a new exercise\n" \
                     "/show - Show exercises"
        bot.send_message(message.chat.id, diary_page)

    elif message.text == "/add":
        pass

    elif message.text == "/add_new":
        bot.send_message(message.chat.id, "Enter a name for the new exercise\n"
                                          "/cancel - Cancel enter")
        bot.register_next_step_handler(message, save_add_new)

    elif message.text == "/show":
        bot.send_message(message.chat.id, "Exercises", reply_markup=show_diary(message))

    elif message.text == "/help":
        help_page = "All commands\n" \
                    "/home - Home\n" \
                    "/diary - Diary\n" \
                    "/add - \n" \
                    "/add_new - Add a new exercise\n" \
                    "/show - Show exercises\n" \
                    "/help - All commands"
        bot.send_message(message.chat.id, help_page)


def save_add_new(message):
    if message.text == "/cancel":
        bot.disable_save_next_step_handlers()
        bot.send_message(message.chat.id, "Enter canceled")
    else:
        connect_db = sqlite3.connect("tele_bot.db")
        cursor = connect_db.cursor()
        cursor.execute("""INSERT INTO bot_users VALUES (?, ?, ?, ?, ?)""",
                       (message.from_user.id, message.text, date_now, None, None))
        connect_db.commit()
        cursor.close()
        connect_db.close()
        bot.send_message(message.chat.id, f"Exercise {message.text} added\n"
                                          "/diary - Diary\n"
                                          "/help - All commands")


def show_diary(message):
    connect_db = sqlite3.connect("tele_bot.db")
    cursor = connect_db.cursor()
    item_from_bd = []
    param = f"""SELECT exercise FROM bot_users WHERE id_user = {message.from_user.id}"""
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
                show_about += f"Date - {i[2]}\n" \
                              f"Reps - {i[3]}\n" \
                              f"Weight - {i[4]}\n" \
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
