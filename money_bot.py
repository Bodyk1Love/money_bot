from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
from pprint import pprint as pp
from sqlite3 import Error
import os
import sqlite3


PORT = int(os.environ.get('PORT', 5000))
bot = telegram.Bot(token=open("secret.cnf").read())


def post_sql_query(sql_query):
    print(sql_query)
    with sqlite3.connect('db.db') as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(sql_query)
            connection.commit()
        except Error:
            pass
        result = cursor.fetchall()
        return result


def get_amount(update):
    data = update.to_dict()['message']['text'].split()
    try:
        amount = float(data[1])
        comment = ""
        if len(data) > 2:
            comment = " ".join(data[2:])
        return [amount, comment]
    except Exception as error:
        update.message.reply_text(error)


def balance(update, context):
    b = post_sql_query("SELECT SUM(amount) FROM logs")
    update.message.reply_text(b[0][0])


def get_minus(update, context):
    data = post_sql_query(
        f"SELECT amount, date, comment FROM logs WHERE amount < 0")
    res = "\n".join([f"{i[1]}) {i[0]} {i[2]}" for i in data])
    update.message.reply_text(res)


def get_plus(update, context):
    data = post_sql_query(
        f"SELECT amount, date, comment FROM logs WHERE amount > 0")
    res = "\n".join([f"{i[1]}) {i[0]} {i[2]}" for i in data])
    update.message.reply_text(res)


def minus(update, context):
    amount, comment = get_amount(update)
    post_sql_query(
        f"INSERT INTO logs (amount, comment) VALUES ('-{abs(amount)}', '{comment}')")
    update.message.reply_text("Записав")


def plus(update, context):
    amount, comment = get_amount(update)
    post_sql_query(
        f"INSERT INTO logs (amount, comment) VALUES ({amount}, '{comment}')")
    update.message.reply_text("Записав")


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
    dp.add_handler(CommandHandler("get_minus", get_minus))
    dp.add_handler(CommandHandler("get_plus", get_plus))

    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=token)
    updater.bot.setWebhook('https://serene-taiga-53897.herokuapp.com/' + token)

    updater.idle()


if __name__ == '__main__':
    main()
