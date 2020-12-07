from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
from pprint import pprint as pp
import os
from datetime import datetime
import pymongo

month = {
    1: "Січень",
    2: "Лютий",
    3: "Березень",
    4: "Квітень",
    5: "Травень",
    6: "Червень",
    7: "Липень",
    8: "Серпень",
    9: "Вересень",
    10: "Жовтень",
    11: "Листопад",
    12: "Грудень"
}

PORT = int(os.environ.get('PORT', 5000))
bot = telegram.Bot(token=open("secret.cnf").read())


def get_collection():
    myclient = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0-gsskm.mongodb.net/money_bot?retryWrites=true&w=majority")
    mydb = myclient["money_bot"]
    mycol = mydb["logs"]
    return mycol

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
    col = get_collection()
    b = sum([float(i.get('amount') or 0) for i in col.find()])
    update.message.reply_text(b)


def get_minus(update, context):
    mon = update.to_dict()['message']['text'].split()
    col = get_collection()
    query = {'amount': {'$lt': 0}}
    if len(mon) > 1:
        query['date'] = { "$regex": f"^{mon[1]}" }
    res = "\n".join([f"{i['date']}) {i['amount']} {i['comment']}" for i in col.find(query)])
    update.message.reply_text(res or "Нема")


def get_plus(update, context):
    mon = update.to_dict()['message']['text'].split()
    col = get_collection()
    query = {'amount': {'$gt': 0}}
    if len(mon) > 1:
        query['date'] = { "$regex": f"^{mon[1]}" }
    res = "\n".join([f"{i['date']}) {i['amount']} {i['comment']}" for i in col.find(query)])
    update.message.reply_text(res or "Нема")


def minus(update, context):
    col = get_collection()
    amount, comment = get_amount(update)
    col.insert_one({
        'amount': -abs(amount), 
        'date': f"{month[datetime.now().month]} {datetime.now().day}",
        'comment': comment
    })
    update.message.reply_text("Записав")

def plus(update, context):
    col = get_collection()
    amount, comment = get_amount(update)
    col.insert_one({
        'amount': amount, 
        'date': f"{month[datetime.now().month]} {datetime.now().day}",
        'comment': comment
    })
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

if __name__ == '__main__':
    main()
