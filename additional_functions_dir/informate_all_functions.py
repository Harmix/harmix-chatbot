import os
import time

import telebot
import json
from additional_functions_dir.create_user_data_dir import create_users_data_dir

from config_api import API_TOKEN
from harmix_db.models import Users

bot = telebot.TeleBot(API_TOKEN)


def informate_all(message, language):
    try:
        user_chat_id = str(message.chat.id)
    except:
        user_chat_id = str(message.message.chat.id)

    full_file_path = os.path.join(os.getcwd(), 'users_data', user_chat_id, user_chat_id + '_data')

    try:
        with open(full_file_path + ".json", "r", encoding='utf-8') as f:
            user_data = json.load(f)
    except:
        create_users_data_dir(message)
        user_data = {}
    languages = list(set(['ua', 'uk', 'ru']) - set([language]))
    if is_informate_all(message, languages[0]):
        bot.send_message(user_chat_id, 'already informate_all_' + languages[0].upper())
    elif is_informate_all(message, languages[1]):
        bot.send_message(user_chat_id, 'already informate_all_' + languages[1].upper())
    else:
        try:
            user_data['informate_all'][language] = True
        except:
            user_data['informate_all'] = {language: True}

        try:
            files_path = [value['photo'] for value in user_data['input_informate_all_values'][language] if
                          list(value.keys())[0] == 'photo']
            for file_path in files_path:
                os.remove(file_path)
        except:
            print("already deleted informating messages")
        try:
            user_data['input_informate_all_values'][language] = []
        except:
            user_data['input_informate_all_values'] = {}

        bot.send_message(user_chat_id, 'message recording started')

        try:
            with open(full_file_path + ".json", "w") as f:
                json.dump(user_data, f)
        except:
            print("informate_all ERROR - no such file")


def informate_all_end(message, language):
    try:
        user_chat_id = str(message.chat.id)
    except:
        user_chat_id = str(message.message.chat.id)

    full_file_path = os.path.join(os.getcwd(), 'users_data', user_chat_id, user_chat_id + '_data')
    try:
        with open(full_file_path + ".json", "r", encoding='utf-8') as f:
            user_data = json.load(f)
    except:
        create_users_data_dir(message)
        user_data = {}

    try:
        if user_data['informate_all'][language]:
            user_data['informate_all'][language] = False

            try:
                input_values = user_data['input_informate_all_values'][language]

                for user in Users.query.filter_by(language=language).all():
                    print(user.username, user.chat_id)
                    time.sleep(1)
                    try:
                        for input_value in input_values:
                            # if list(input_value.keys())[0] == 'text':
                            try:
                                bot.send_message(user.chat_id, input_value['text'])
                                # else:
                            except:
                                try:
                                    print("send photo to users")
                                    image = open(input_value['photo'], 'rb')
                                    bot.send_photo(user.chat_id, image)
                                    image.close()
                                except:
                                    print("image = open(input_value['photo'], 'rb') ERROR")

                    except Exception as error:
                        print("informate_all_end ERROR - no such chat", error)

                try:
                    files_path = [value['photo'] for value in user_data['input_informate_all_values'][language] if
                                  list(value.keys())[0] == 'photo']

                    for file_path in files_path:
                        os.remove(file_path)
                except:
                    print("already deleted informating messages in informate_all_end")

                user_data['input_informate_all_values'][language] = []

            except:
                print("Keyerror in informate_all_end")
                user_data['input_informate_all_values'][language] = []

    except:
        print("general ERROR in informate_all_end")
        user_data['informate_all'] = {}
        user_data['informate_all'][language] = False

    try:
        with open(full_file_path + ".json", "w") as f:
            json.dump(user_data, f)
    except:
        print("informate_all_end ERROR - no such file")


def is_informate_all(message, language):
    try:
        user_chat_id = str(message.chat.id)
    except:
        user_chat_id = str(message.message.chat.id)

    full_file_path = os.path.join(os.getcwd(), 'users_data', user_chat_id, user_chat_id + '_data')

    try:
        with open(full_file_path + ".json", "r", encoding='utf-8') as f:
            user_data = json.load(f)

        return user_data['informate_all'][language]
    except:
        return False


def save_input_values(message, language):
    try:
        user_chat_id = str(message.chat.id)
    except:
        user_chat_id = str(message.message.chat.id)

    full_file_path = os.path.join(os.getcwd(), 'users_data', user_chat_id, user_chat_id + '_data')
    with open(full_file_path + ".json", "r", encoding='utf-8') as f:
        user_data = json.load(f)
    try:
        user_data['input_informate_all_values'][language].append({'text': message.text})
    except:
        user_data['input_informate_all_values'][language] = [{'text': message.text}]

    try:
        bot.send_message(user_chat_id, "message was saved")
        with open(full_file_path + ".json", "w") as f:
            json.dump(user_data, f)
    except:
        print("save_input_values ERROR")


def save_photo(message, language):
    try:
        user_chat_id = str(message.chat.id)
    except:
        user_chat_id = str(message.message.chat.id)

    full_file_path = os.path.join(os.getcwd(), 'users_data', user_chat_id, user_chat_id + '_data')

    try:
        with open(full_file_path + ".json", "r", encoding='utf-8') as f:
            user_data = json.load(f)
    except:
        create_users_data_dir(message)
        user_data = {}

    image_id = message.photo[-1].file_id
    image_info = bot.get_file(image_id)

    downloaded_file = bot.download_file(image_info.file_path)

    image_path = os.path.join(os.getcwd(), 'users_data', user_chat_id, image_id + '.jpg')
    try:
        with open(image_path, 'wb') as f:
            f.write(downloaded_file)
    except:
        print('file exist')

    try:
        user_data['input_informate_all_values'][language].append({'photo': image_path})
    except:
        user_data['input_informate_all_values'][language] = [{'photo': image_path}]

    bot.send_message(user_chat_id, "image was saved")
    try:
        with open(full_file_path + ".json", "w") as f:
            json.dump(user_data, f)
    except:
        print("save_photo ERROR")
