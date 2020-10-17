import telebot
import telegram

from additional_functions_dir.create_user_data_dir import create_users_data_dir
from additional_functions_dir.fucntions_with_video import delete_previous_video
from additional_functions_dir.renovate_id_code import renovate_id_code_db
from config_api import API_TOKEN, HEROKU_WEB_URL, UPLOAD_TERM, TERM_OF_USE, PRIVACY_POLICY
from harmix_db.main_db_functions import update_sql
from harmix_db.models import Users
from language_functions import phrase_on_language
from additional_functions_dir.renovate_buy_user_id_web import renovate_buy_user_id_web

bot = telebot.TeleBot(API_TOKEN)
PREMIUM_FUNCTIONS = {
    "premium_function0": "fade_effects",
    "premium_function1": "upload_more_20mb"
}


def start_upload_video_buttons(message):
    """
    :return: buttons with Upload more or less 20 mb video
    """
    try:
        language_phrase = phrase_on_language(message, "start_upload_video_buttons")
    except:
        create_users_data_dir(message)
        language_phrase = phrase_on_language(message, "start_upload_video_buttons")

    keyboard = telebot.types.InlineKeyboardMarkup()

    keyboard.row(
        telebot.types.InlineKeyboardButton(language_phrase[0], callback_data='upload_video2')
    )

    keyboard.row(
        telebot.types.InlineKeyboardButton(language_phrase[1], callback_data='video_more_20')
    )

    bot.send_message(message.chat.id, language_phrase[2],
                     reply_markup=keyboard, disable_notification=True)


def payment_buttons(message, query_data=""):
    try:
        language_phrases = phrase_on_language(message, 'get_video_less_20')

    except:
        create_users_data_dir(message)
        language_phrases = phrase_on_language(message, 'get_video_less_20')

    if isinstance(message, dict):
        user_chat_id = message["chat"]["id"]
    else:
        user_chat_id = str(message.chat.id)

    print("\n payment_buttons function ------------------------------------")
    print("message before update", message)
    if query_data != "":
        # save last function before payment to start this function when user get a subscription on site
        update_sql("users_data", "last_function_before_pay",
                   str(message.chat.id), PREMIUM_FUNCTIONS[query_data])

        file_name = """{"file_name": ""}"""
        try:
            if message.document.file_name is not None and message.document.file_name != False and \
                    message.document.file_name != True:
                file_name = """{"file_name": \"""" + str(message.document.file_name) + "\"}"
                print("file_name", file_name)
        except:
            print("message.document.file_name ERRor")

        message_chat_id = """{"id": \"""" + str(message.chat.id) + "\"" + "}"

        update_sql("users_data", "last_message_before_pay",
                   str(message.chat.id), '{' + """"chat": {}, "document": {}""".format(message_chat_id,
                                                                                       str(file_name)).replace("\'",
                                                                                                               "\"") + '}')

    keyboard = telebot.types.InlineKeyboardMarkup()
    user_data = Users.query.filter_by(chat_id=user_chat_id).first()

    buy_user_id_web = user_data.buy_user_id_web
    if buy_user_id_web is None:
        buy_user_id_web = renovate_buy_user_id_web(user_chat_id)

    flask_url = "{}buy_subscription?buy_user_id_web={}".format(HEROKU_WEB_URL, buy_user_id_web)

    keyboard.row(
        telebot.types.InlineKeyboardButton(language_phrases[6][0], callback_data='pay_in_telegram')
    )

    keyboard.row(
        telebot.types.InlineKeyboardButton(language_phrases[6][1], url=flask_url)
    )

    keyboard.row(
        telebot.types.InlineKeyboardButton("✖ " + language_phrases[8], callback_data="upload_new_video")
    )

    bot.send_message(message.chat.id, language_phrases[5])

    bot.send_message(message.chat.id, language_phrases[9].format(
        UPLOAD_TERM, TERM_OF_USE, PRIVACY_POLICY),
                     parse_mode=telegram.ParseMode.HTML,
                     reply_markup=keyboard,
                     disable_web_page_preview=True)


def more_20_mb_videos_buttons(message, user_data=""):
    if isinstance(message, dict):
        user_chat_id = message["chat"]["id"]
        message_chat_id = int(user_chat_id)

    else:
        user_chat_id = str(message.chat.id)
        message_chat_id = message.chat.id

    try:
        language_phrases = phrase_on_language(message, 'get_video_less_20')

    except:
        create_users_data_dir(message)
        language_phrases = phrase_on_language(message, 'get_video_less_20')

    if user_data == "":
        user_data = Users.query.filter_by(chat_id=user_chat_id).first()

    user_id_code_web = user_data.user_id_code_web
    print("\n more_20_mb_videos_buttons function ------------------------------------")
    print("user_id_code_web0", user_id_code_web)
    if user_id_code_web is None:
        user_id_code_web = renovate_id_code_db(user_chat_id)

    print("user_id_code_web1", user_id_code_web)
    delete_previous_video(user_chat_id)

    keyboard = telebot.types.InlineKeyboardMarkup()
    flask_url = "{}upload?user_id_code_web={}".format(HEROKU_WEB_URL, user_id_code_web)
    keyboard.row(
        telebot.types.InlineKeyboardButton('🎬️ ' + language_phrases[3], url=flask_url)
    )
    make_continue_editing_button(message, user_chat_id, keyboard, "")
    # bot.send_message(message_chat_id, "😢 " + language_phrases[10] + " 😎", disable_notification=True)
    bot.send_message(message_chat_id, language_phrases[7],
                     reply_markup=keyboard, disable_notification=True)


def improve_and_upload_buttons(message):
    """
    :return: a button to improve video(send top 4 tracks for the video) or upload a new video
    or change parameters buttons
    """
    try:
        language_phrase = phrase_on_language(message, "improve_and_upload_buttons")
    except:
        create_users_data_dir(message)
        language_phrase = phrase_on_language(message, "improve_and_upload_buttons")

    keyboard = telebot.types.InlineKeyboardMarkup()

    keyboard.row(
        telebot.types.InlineKeyboardButton('📚 ' + language_phrase[0], callback_data='improve')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('📋 ' + language_phrase[3], callback_data='change_music_params')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('🔄 ' + language_phrase[2], callback_data='upload_new_video')
    )

    bot.send_message(message.chat.id, language_phrase[1],
                     reply_markup=keyboard, disable_notification=True)


def make_continue_editing_button(message, user_chat_id, keyboard, function=""):
    delete_previous_video(user_chat_id)

    try:
        language_phrase = phrase_on_language(message, "improve_and_upload_buttons")
    except:
        create_users_data_dir(message)
        language_phrase = phrase_on_language(message, "improve_and_upload_buttons")

    if function == "single_button":
        keyboard = telebot.types.InlineKeyboardMarkup()

    # keyboard.row(
    #     telebot.types.InlineKeyboardButton(language_phrase[4],
    #                                        callback_data='continue_edit')
    # )
    keyboard.row(
        telebot.types.InlineKeyboardButton('🔄 ' + language_phrase[2], callback_data='upload_new_video')
    )
    if function == "single_button":
        bot.send_message(user_chat_id, "⛔️‼️ " + language_phrase[5],
                                 reply_markup=keyboard, disable_notification=True)


def language_buttons(message):
    keyboard = telebot.types.InlineKeyboardMarkup()

    keyboard.row(
        telebot.types.InlineKeyboardButton('🇺🇦 Українська', callback_data='ua')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('🇺🇸 English', callback_data='uk')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton('🇷🇺 Русский', callback_data='ru')
    )

    bot.send_message(message.chat.id, 'Choose a language:\n\n'
                                      'You can change it at any time using /change_language command.',
                     reply_markup=keyboard)


def upload_less_20(message):
    try:
        language_phrases = phrase_on_language(message, "take_input")

    except:
        create_users_data_dir(message)
        language_phrases = phrase_on_language(message, "take_input")

    bot.send_message(message.chat.id, language_phrases[1], disable_notification=True)
