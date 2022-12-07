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
def fafa(update: Update, context: CallbackContext):
    bot.sendMessage(chat_id=update.effective_chat.id, text=f'started')
    print('fafa')
    global flag
    flag = 1

def ping(update: Update, context: CallbackContext):
    name = update.message.text[6:]
    query.query(name)
    bot.sendPhoto(chat_id=update.effective_chat.id, photo=open('kl.jpg', 'rb'))

ping_handler = CommandHandler('ping', ping)
fafa_handler = CommandHandler('fafa',fafa)
dispatcher.add_handler(fafa_handler)
dispatcher.add_handler(ping_handler)

updater.start_polling()
