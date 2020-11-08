from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
from pprint import pprint as pp
import os
PORT = int(os.environ.get('PORT', 5000))

bot = telegram.Bot(token=open("secret.cnf").read())


def balance(update, context):
    with open("balance", "r") as file:
        update.message.reply_text(file.read())


def minus(update, context):
    data = update.to_dict()
    balance = float(open("balance").read() or 0)
    try:
        amount = float(data['message']['text'].split()[1])
    except:
        update.message.reply_text("Хуй соси")
    balance -= amount
    with open("balance", "w") as file:
        file.write(str(balance))
    update.message.reply_text(balance)


def plus(update, context):
    data = update.to_dict()
    balance = float(open("balance").read() or 0)
    try:
        amount = float(data['message']['text'].split()[1])
    except:
        update.message.reply_text("Хуй соси")
    balance += amount
    with open("balance", "w") as file:
        file.write(str(balance))
    update.message.reply_text(balance)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    token = open("secret.cnf").read()
    updater = Updater(token, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("balance", balance))
    dp.add_handler(CommandHandler("minus", minus))
    dp.add_handler(CommandHandler("plus", plus))

    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=token)
    updater.bot.setWebhook('https://serene-taiga-53897.herokuapp.com/' + token)

    updater.idle()


if __name__ == '__main__':
    main()
