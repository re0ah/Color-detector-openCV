import telebot
import json
from threading import Thread

def save_user_id(user_id):
    with open("telegram_user_list.json", "w") as write_file:
        data = {
                 "id": user_id
               }
        json.dump(data, write_file)

def load_user_id() -> dict:
    try:
        with open("telegram_user_list.json", "r") as read_file:
            return json.load(read_file)
    except FileNotFoundError:
        return 0

class Telegram_th(Thread):
    def __init__(self):
        super().__init__()
        """-1 - ожидание начала подсчета
           0..150 - подсчет
           150 - отправка и обнуление"""
        self.mailing = -1
        self.id = load_user_id()["id"]
        self.bot = telebot.TeleBot("TELEGRAM_TOKEN")
        self.bot.remove_webhook()
        @self.bot.message_handler(commands=["start"])
        def registration_command(message):
            self.bot.send_message(message.chat.id, "Вы добавлены в список рассылки!")
            save_user_id(message.chat.id)

    def run(self):
        self.bot.polling(none_stop=True)

    def send_message(self, message: str):
        self.bot.send_message(self.id, message)


bot = Telegram_th()
bot.start()
