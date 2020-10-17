import os
import telebot
import json

from additional_functions_dir.create_user_data_dir import create_users_data_dir
from config_api import API_TOKEN
from harmix_db.main_db import db
from harmix_db.models import Users


def phrase_on_language(message, function, user_chat_id=""):
    """

    :param message: a message to translate
    :param function: a function from which we translate phrases
    to find the special phrase in phrases.json
    :return: translated phrase on the user language
    """
    if user_chat_id == "":
        if isinstance(message, dict):
            user_chat_id = message["chat"]["id"]
        else:
            try:
                user_chat_id = str(message.chat.id)
            except:
                user_chat_id = str(message.message.chat.id)

    full_file_path = os.path.join(os.getcwd(), 'users_data', user_chat_id, user_chat_id)
    full_phrases_path = os.path.join(os.getcwd(), 'templates', 'phrases')

    try:
        with open(full_file_path + '_data' + ".json", "r", encoding='utf-8') as f:
            user_data = json.load(f)
            language = user_data["language"]

    except:
        create_users_data_dir(message)
        print('phrase_on_language error - user_data = json.load(f) or language_phrase = phrases[function][language]')
        if db.session.query(Users.id).filter_by(chat_id=user_chat_id).scalar():
            user_db = Users.query.filter_by(chat_id=user_chat_id).first()
            language = user_db.language

        else:
            language = "uk"

    with open(full_phrases_path + ".json", "r", encoding='utf-8') as f:
        phrases = json.load(f)
        language_phrase = phrases[function][language]

    return language_phrase
