import query
import telegram
from telegram import Update
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler
# read token from TOKEN.txt

token = open('TOKEN.txt', 'r').read()
# print(list(token))

bot = telegram.Bot(token=token)
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher


def k_command(update: Update, context: CallbackContext):
    name = update.message.text[3:]
    query.query(name,'15m')
    bot.sendPhoto(chat_id=update.effective_chat.id, photo=open('kl.jpg', 'rb'))

def kk_command(update: Update, context: CallbackContext):
    name = update.message.text[4:]
    query.query(name,'1m')
    bot.sendPhoto(chat_id=update.effective_chat.id, photo=open('kl.jpg', 'rb'))

def kh_command(update: Update, context: CallbackContext):
    name = update.message.text[4:]
    query.query(name,'1h')
    bot.sendPhoto(chat_id=update.effective_chat.id, photo=open('kl.jpg', 'rb'))

def kd_command(update: Update, context: CallbackContext):
    name = update.message.text[4:]
    query.query(name,'1d')
    bot.sendPhoto(chat_id=update.effective_chat.id, photo=open('kl.jpg', 'rb'))

k_handler = CommandHandler('k', k_command)
kk_handler = CommandHandler('kk', kk_command)
kh_handler = CommandHandler('kh', kh_command)
dispatcher.add_handler(k_handler)
dispatcher.add_handler(kk_handler)
dispatcher.add_handler(kh_handler)
updater.start_polling()
