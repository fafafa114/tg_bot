import telegram
from telegram import Update
from telegram.bot import Bot, BotCommand
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler
from query_script import kline, search_symbol

token = open('TOKEN.txt', 'r').read()
bot = Bot(token=token)
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher


def kline_command(update: Update, context: CallbackContext, command: str, interval: str):
    name = update.message.text[len(command)+2:]
    name = name.replace(' ', '')
    if name == '':
        return
    msg = kline.get_kline(name, interval)
    if msg == "Symbol not found":
        msg = 'Symbol not found, please try command /s <symbol>'
        bot.sendMessage(chat_id=update.effective_chat.id, text=msg)
    else:
        bot.sendPhoto(chat_id=update.effective_chat.id,
                      photo=open('kl.jpg', 'rb'), caption=msg)


def kq_command(update: Update, context: CallbackContext):
    kline_command(update, context, 'kq', '15m')


def km_command(update: Update, context: CallbackContext):
    kline_command(update, context, 'kk', '1m')


def kh_command(update: Update, context: CallbackContext):
    kline_command(update, context, 'kh', '1h')


def kd_command(update: Update, context: CallbackContext):
    kline_command(update, context, 'kd', '1d')


def s_command(update: Update, context: CallbackContext):
    name = update.message.text[3:]
    name = name.replace(' ', '')
    if name == '':
        return
    symbols = search_symbol.search(name)
    symbols = '`Symbols found:\n\t' + '\n\t'.join(symbols) + "`"
    bot.sendMessage(chat_id=update.effective_chat.id, text=symbols,
                    parse_mode=telegram.ParseMode.MARKDOWN_V2)


kq_handler = CommandHandler('kq', kq_command)
km_handler = CommandHandler('km', km_command)
kh_handler = CommandHandler('kh', kh_command)
kd_handler = CommandHandler('kd', kd_command)
s_handler = CommandHandler('s', s_command)

dispatcher.add_handler(kq_handler)
dispatcher.add_handler(km_handler)
dispatcher.add_handler(kh_handler)
dispatcher.add_handler(kd_handler)
dispatcher.add_handler(s_handler)
bot.set_my_commands([
    BotCommand('kq', '<symbol> 15min kline'),
    BotCommand('km', '<symbol> 1min kline'),
    BotCommand('kh', '<symbol> 1hour Kline'),
    BotCommand('kd', '<symbol> 1day kline'),
    BotCommand('s', 'Search symbol <symbol>')]
)
updater.start_polling()
