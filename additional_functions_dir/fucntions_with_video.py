from datetime import datetime
import json
import os

import telebot

from additional_functions_dir.create_user_data_dir import create_users_data_dir
from additional_functions_dir.get_chat_id import create_chat_id_for_db
from config_api import API_TOKEN
from language_functions import phrase_on_language

bot = telebot.TeleBot(API_TOKEN)


def delete_previous_video(user_chat_id):
    try:
        with open(os.path.join(os.getcwd(), "users_data", user_chat_id, user_chat_id + "_data.json"), 'r',
                  encoding="utf=8") \
                as user_file:
            user_file_json = json.load(user_file)
    except:
        print("delete_previous_video ERROR - no such file")

    # delete previous uploaded file to save more memory
    try:
        video_from_server_path = os.path.join('users_data', user_chat_id,
                                              user_file_json["video_name"])
        os.remove(video_from_server_path)
    except:
        print("first file upload - not 'video_name' in user_chat_id + '_data.json' ")


def clean_audio_change_upload(message, user_chat_id):
    """

    :return: clean audios downloaded from user dir which are top 4 special for the video
    and update last_upload a video to understand active users in general
    """
    try:
        # delete musics_for_video dir if it exists to start work with a new video
        audios_path = os.path.join(os.getcwd(), 'users_data', user_chat_id, 'musics_for_video')

        try:
            language_phrases = phrase_on_language(message, 'get_video_less_20')
            error_phrases = phrase_on_language(message, 'send_video_to_user')

        except:
            create_users_data_dir(message)
            language_phrases = phrase_on_language(message, 'get_video_less_20')
            error_phrases = phrase_on_language(message, 'send_video_to_user')

        chat_id = create_chat_id_for_db(message)

        if user_chat_id not in os.listdir("users_data") or user_chat_id + "_data.json" \
                not in os.listdir(os.path.join('users_data', user_chat_id)):
            create_users_data_dir(message)
            print("clean_audio_change_upload ERROR")

        # last upload refresh
        full_file_path = os.path.join(os.getcwd(), 'users_data', user_chat_id, user_chat_id)
        with open(full_file_path + "_data" + ".json", "r", encoding='utf-8') as f:
            file_user_data = json.load(f)
            file_user_data['last_upload'] = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')

        with open(full_file_path + "_data" + ".json", "w") as f:
            json.dump(file_user_data, f, ensure_ascii=False, indent=4)

        try:
            if os.listdir(audios_path):
                for the_file in os.listdir(audios_path):
                    file_path = os.path.join(audios_path, the_file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        print(e)

        except:
            print('musics_for_video dir is empty')

    except:
        print('get_video error - general')
        try:
            bot.send_message(message.chat.id, error_phrases[4])
        except:
            bot.send_message(message.chat.id, "Something went wrong ! Please. upload your video once more")

    return chat_id, language_phrases, error_phrases
