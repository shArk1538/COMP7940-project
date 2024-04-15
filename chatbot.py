import os
from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import logging

from ChatGPT_HKBU import HKBU_ChatGPT
from Speech_to_text import speech2text
from Google_Map import google_map
from MongoDB import database


def main():
    # 日志信息
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    global updater
    global dispatcher
    updater = Updater(token=(os.environ['Bot_Token']), use_context=True)
    dispatcher = updater.dispatcher

    # MongoDB:NoSQL
    global db
    db = database()

    # chatgpt
    global chatgpt
    chatgpt = HKBU_ChatGPT()
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

    # 语音识别
    global speech_enabled
    speech_enabled = False
    dispatcher.add_handler(CommandHandler("speaking", enable_speech))
    dispatcher.add_handler(CommandHandler("type_only", disable_speech))
    dispatcher.add_handler(MessageHandler(Filters.voice, handle_voice))

    # 谷歌地图
    global map
    global map_enabled
    map = google_map()
    map_enabled = False
    dispatcher.add_handler(CommandHandler('map_assistant', map_assistant))  # 注册命令处理程序
    dispatcher.add_handler(CallbackQueryHandler(handle_inline_button))   # 注册 inline keyboard 按钮点击处理程序


    # 基本功能
    dispatcher.add_handler(CommandHandler("start", start))
    # dispatcher.add_handler(CommandHandler("help", help))

    # To start the bot:
    updater.start_polling()
    updater.idle()

#=======================================================================================================#
def equiped_chatgpt(update, context):
    global chatgpt
    global map_enabled
    if map_enabled:
        pass
    else:
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

#=======================================================================================================#

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
def handle_voice(update, context):
    message = update.effective_message
    if speech_enabled and message.voice:
        process_voice_message(update, context)
    else:
        pass

# 处理语音消息
def process_voice_message(update, context):
    global map_enabled
    message = update.effective_message
    file_id = message.voice.file_id
    file = context.bot.get_file(file_id)
    file.download(f'{file_id}.ogg')

    # 'zh-CN' 简体中文
    # 'zh-HK' 粤语
    # 'en-US' 英语(美国)
    language_list = ['zh-CN','zh-HK','en-US']
    language = language_list[0]

    processer = speech2text(audio_file_id=file_id)
    response = processer.process(language)

    if len(response.results)>0:
        transcript = response.results[0].alternatives[0].transcript
        if map_enabled:
            pass  # 当地图助手模式打开时，暂时忽略语音处理
        else:
            reply_message = chatgpt.submit(transcript)
            context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I couldn't recognize your voice.")

    os.remove(f'{file_id}.ogg')

#=======================================================================================================#

def map_assistant(update, context):
    global map_enabled
    map_enabled = True
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="I'm your map assistant, please tell me the location you are interested in!")
    global input_handler
    input_handler = MessageHandler(Filters.text & (~Filters.command), handle_user_input)
    dispatcher.add_handler(input_handler, group=1)  # 在启动地图助手模式后才根据内容返回信息添加按钮

def handle_user_input(update, context):
    # 先获取用户名及输入的内容
    user_id = update.effective_user.id
    user_input = update.effective_message.text

    # 存储用户数据到 MongoDB
    store_user_data(user_id, user_input)

    # 创建 inline keyboard
    keyboard = [
        [
            InlineKeyboardButton("Nearby", callback_data='nearby'),
            InlineKeyboardButton("Map", callback_data='map'),
            InlineKeyboardButton("Photo", callback_data='photo')
        ],
        [
            InlineKeyboardButton("Quit", callback_data='quit')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 发送 inline keyboard
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Got it! You may choose an option about {get_user_data(user_id)}:",
                             reply_markup=reply_markup)

# 处理 inline keyboard 按钮点击
def handle_inline_button(update, context):
    global map_enabled
    global input_handler
    if map_enabled:
        query = update.callback_query
        option = query.data

        user_id = query.from_user.id
        user_data = get_user_data(user_id)

        # 根据选项执行对应的功能函数
        if option == 'nearby':
            places = get_info(user_data)
            message = ""
            for place in places:
                Name = place['name']
                Address = place.get('vicinity', 'No address found')
                Rating = place.get('user_ratings_total','N/A')
                line = '-' * 40
                message += (f"·Name: {Name}\n"
                            f"·Address: {Address}\n"
                            f"·User-rating: {Rating}\n"
                            f"{line}\n")
            query.answer()
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)

        elif option == 'map':
            map_url = get_map(user_data)
            query.answer()
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=map_url)

        elif option == 'photo':
            photo_url = get_photo(user_data)
            query.answer()
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url)

        elif option == 'quit':
            map_enabled = False
            db.delete_data(user_id)

            # for group in dispatcher.handlers:     # 查看移除前的handler列表
            #     print(f"Handler group {group}:")
            #     for handler in dispatcher.handlers[group]:
            #         print(f" - {handler}")

            dispatcher.remove_handler(input_handler, group=1)

            # for group in dispatcher.handlers:     # 检查是否正确移除
            #     print(f"Handler group {group}:")
            #     for handler in dispatcher.handlers[group]:
            #         print(f" - {handler}")

            query.answer("Quit map assistant.") # 已处理该按钮信息
            context.bot.send_message(chat_id=update.effective_chat.id, text="You have quited the Map Assistant! Bye bye.")

def store_user_data(user_id, user_input):
    """
    将用户数据存储到 MongoDB
    """
    db.store_data(user_id, user_input)

    return None

#
def get_user_data(user_id):
    """
    从 MongoDB 获取用户数据
    """
    user_data = db.get_data(user_id)
    if user_data:
        return user_data
    else:
        return None

def get_info(user_data):
    if user_data:
        type_list = ['tourist_attraction', 'restaurant', 'park', 'shopping_mall',
                    'bakery', 'cafe', 'clothing_store', 'drugstore', 'university']
        type = type_list[0]  # 设置为可以选择的逻辑
        reply = map.place_info(user_data,type) # 获取位置相关信息

        return reply
        # 发送图片给用户


def get_map(user_data):
    if user_data:
        # 根据用户数据获取图片 URL
        image_url = map.get_location_map(user_data)

        return image_url

def get_photo(user_data):
    if user_data:
        # 根据用户数据获取图片 URL
        image_url = map.get_location_photo(user_data)

        return image_url

#=======================================================================================================#
# 基本功能
def start(update: Update, context: CallbackContext):
    message = update.message
    keyboard = [[KeyboardButton('/speaking'), KeyboardButton('/type_only')],
                [KeyboardButton('/map_assistant')]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        message.reply_text('Hello！Please @ me if you need help.', reply_markup=reply_markup)
    else:
        message.reply_text('Hello！You can talk to me directly.', reply_markup=reply_markup)


def help(update: Update, context: CallbackContext) -> None:
    pass


if __name__ == '__main__':
    main()
