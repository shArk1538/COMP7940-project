import os
from telegram import Update
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import configparser
import logging
import redis

from ChatGPT_HKBU import HKBU_ChatGPT
from Speech_to_text import speech2text


global redis1
def main():
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher

    global redis1
    redis1 = redis.Redis(host=(config['REDIS']['HOST']), password=(config['REDIS']['PASSWORD']), port=(config['REDIS']['REDISPORT']))
   
    # You can set this logging module, so you will know when and why things do not work as expected Meanwhile, update your config.ini as:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


    # dispatcher for chatgpt
    global chatgpt
    chatgpt = HKBU_ChatGPT(config)
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

    # 语音识别
    global speech_enabled
    speech_enabled = False

    dispatcher.add_handler(CommandHandler("speaking", enable_speech))
    dispatcher.add_handler(CommandHandler("type_only", disable_speech))
    dispatcher.add_handler(MessageHandler(Filters.voice, handle_text))


    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("hello", hello))

    # To start the bot:
    updater.start_polling()
    updater.idle()


def equiped_chatgpt(update, context): 
    global chatgpt
    message = update.effective_message
    reply_message = chatgpt.submit(message.text)
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))

    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        bot_username = context.bot.username
        if f'@{bot_username}' in message.text:
            context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


def enable_speech(update, context):
    global speech_enabled
    speech_enabled = True
    context.bot.send_message(chat_id=update.effective_chat.id, text="Speak-mode enable!")

# 处理 /stop 命令
def disable_speech(update, context):
    global speech_enabled
    speech_enabled = False
    context.bot.send_message(chat_id=update.effective_chat.id, text="Speak-mode closed!")

# 处理文本消息
def handle_text(update, context):
    message = update.effective_message
    if speech_enabled and message.voice:
        process_voice_message(update, context)
    else:
        pass

# 处理语音消息
def process_voice_message(update, context):
    message = update.effective_message
    file_id = message.voice.file_id
    file = context.bot.get_file(file_id)
    file.download('voice_message.ogg')

    # 'zh-CN' 简体中文
    # 'zh-HK' 粤语
    # 'en-US' 英语(美国)
    language_list = ['zh-CN','zh-HK','en-US']
    language = language_list[0]

    processer = speech2text()
    response = processer.process(language)

    if len(response.results)>0:
        transcript = response.results[0].alternatives[0].transcript
        reply_message = chatgpt.submit(transcript)
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I couldn't recognize your voice.")

    os.remove('voice_message.ogg')


# 基本功能
def start(update: Update, context: CallbackContext):
    message = update.message
    keyboard = [[KeyboardButton('/speaking'), KeyboardButton('/type_only')]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        message.reply_text('Hello！Please @ me if you need help.', reply_markup=reply_markup)
    else:
        message.reply_text('Hello！You can talk to me directly.', reply_markup=reply_markup)


def help(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')


def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]   # /add keyword <-- this should store the keyword
        redis1.incr(msg)
        update.message.reply_text('You have said ' + msg +  ' for ' + redis1.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')


def hello(update: Update, context: CallbackContext) -> None:
    global redis1
    logging.info(context.args[0])
    msg = context.args[0]  # /hello keyword <-- this should store the keyword
    redis1.incr(msg)
    update.message.reply_text('Good day, ' + msg +'!')

if __name__ == '__main__':
    main()
