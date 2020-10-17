import os
import telebot
import json


def phrase_on_language(function):
    """

    :param message: a message to translate
    :param function: a function from which we translate phrases
    to find the special phrase in phrases.json
    :return: translated phrase on user language
    """
    # try:
    #     user_chat_id = str(message.chat.id)
    # except:
    #     user_chat_id = str(message.message.chat.id)
    
    # user_chat_id = '511986933'
    # 
    # full_file_path = os.path.join(os.getcwd(), 'users_data', user_chat_id, user_chat_id)
    full_phrases_path = os.path.join(os.getcwd(), 'phrases')

    # try:
    #     with open(full_file_path + '_data' + ".json", "r", encoding='utf-8') as f:
    #         users_data = json.load(f)
    # 
    #     language = users_data["language"]
    # 
    # except:
    #     print('phrase_on_language error - users_data = json.load(f) or language_phrase = phrases[function][language]')
    #     language = "en"
    
    language = "uk"

    with open(full_phrases_path + ".json", "r", encoding='utf-8') as f:
        phrases = json.load(f)
        language_phrase = phrases[function][language]

    return language_phrase

