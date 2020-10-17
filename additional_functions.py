import gc
import logging
import os
import telebot
import json
import requests
from multiprocessing.pool import ThreadPool
from multiprocessing import Process

from functools import wraps
from pydub import AudioSegment
import re

from telegram import ChatAction
from telebot import types

from harmix_db.main_db_functions import update_sql
from language_functions import phrase_on_language
from config_api import API_TOKEN, ALLOWED_EXTENSIONS
from additional_functions_dir.create_user_data_dir import create_users_data_dir

bot = telebot.TeleBot(API_TOKEN)


def add_logs():
    log_formatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
    )
    root_logger = logging.getLogger()

    log_path, file_name = "logs", "harmix_bot"
    file_handler = logging.FileHandler("{0}/{1}.log".format(log_path, file_name))
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def write_in_user_file(message, data, key_name, user_chat_id="", function=""):
    if user_chat_id == "":
        try:
            user_chat_id = str(message.chat.id)
        except:
            user_chat_id = str(message.from_user.id)

    print("write_in_user_file")
    try:
        write_in_file(data, key_name, user_chat_id, function)

    except:
        create_users_data_dir(message)
        write_in_file(data, key_name, user_chat_id, function)


def write_in_file(data, key_name, user_chat_id="", function=""):
    full_file_path = os.path.join(os.getcwd(), 'users_data', user_chat_id, user_chat_id)
    with open(full_file_path + "_data" + ".json", "r", encoding='utf-8') as f:
        file_user_data = json.load(f)

        if function == 'make_new':
            file_user_data[key_name] = data
            print("file_user_data[key_name]", file_user_data[key_name])

        elif function == "change_number":
            file_user_data[key_name] = file_user_data.get(key_name, 0)
            file_user_data[key_name] += data
            print("file_user_data n_surveys", file_user_data[key_name])
            if key_name == "n_surveys":
                print("update_sql(users_data, n_surveys")
                update_sql("users_data", "n_surveys", user_chat_id, str(file_user_data[key_name]))

        else:
            try:
                file_user_data[key_name] = file_user_data.get(key_name, [])
                file_user_data[key_name].append(data)

            except:
                print("write_in_user_file - add not like file_user_data[key_name].append(data), "
                      "but in such a way - file_user_data[key_name] = data")
                file_user_data[key_name] = data

    with open(full_file_path + "_data" + ".json", "w", encoding='utf-8') as f:
        json.dump(file_user_data, f, ensure_ascii=False, indent=4)


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(message, *args, **kwargs):
        try:
            bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

        except:
            bot.send_chat_action(chat_id=message["chat"]["id"], action=ChatAction.TYPING)

        return func(message, *args, **kwargs)

    return command_func


def delete_video(message, video_from_server_path):
    # If the file exists, delete it
    try:
        os.remove(video_from_server_path)
    except:
        print('downloaded_video does not exist')


def download_url(url):
    # assumes that the last segment after the / represents the file name
    # if url is abc/xyz/file.txt, the file name will be file.txt
    url_end = url.rfind("|")
    url_for_download = url[:url_end]
    file_name = url[url_end + 1:]

    try:
        r = requests.get(url_for_download, stream=True)
        if r.status_code == requests.codes.ok:
            with open(file_name, 'wb') as f:
                for data in r:
                    f.write(data)

        # collect unnecessary garbage
        gc.collect()

    except:
        print('download_url error - r = requests.get(url_for_download, stream=True)')

    return file_name


def cut_music(url):
    url_end = url.rfind("|")
    audio_name = url[url_end + 1:]
    try:
        song = AudioSegment.from_mp3(audio_name)

        # if the audio is longer then 60 sec - cut it to 60 sec
        len_s = len(song)
        if len_s > 60 * 1000:
            pos = audio_name.rfind(".")
            new_audio_name = audio_name[:pos] + '_trim' + '.mp3'
            thirty_seconds = 30 * 1000
            mid = len(song) // 2

            middle_seconds_song = song[mid - thirty_seconds: mid + thirty_seconds]
            middle_seconds_song.export(new_audio_name, format='mp3')
            gc.collect()
            audio_name, new_audio_name = new_audio_name, audio_name
            os.remove(new_audio_name)
    except:
        print("cut_music ERROR")


def send_other_musics(message):
    """
    :return: 4 songs with 60 sec duration - other top 4 special for this video
    """
    try:
        language_phrases = phrase_on_language(message, "send_video_to_user")

    except:
        create_users_data_dir(message)
        language_phrases = phrase_on_language(message, "send_video_to_user")

    user_chat_id = str(message.chat.id)
    error_phrases = phrase_on_language(message, 'send_video_to_user')

    full_file_path = os.path.join(os.getcwd(), 'users_data', user_chat_id, user_chat_id)
    try:
        with open(full_file_path + 'musics5_for_video' + ".json", 'r') as musics5_file:
            musics5 = json.load(musics5_file)

    except:
        bot.send_message(message.chat.id, language_phrases[3])

    audios_path = os.path.join(os.getcwd(), 'users_data', user_chat_id, 'musics_for_video')
    try:
        os.mkdir(audios_path)
    except OSError:
        print("Creation of the directory %s failed or this directory exists" % audios_path)
    else:
        print("Successfully created the directory %s " % audios_path)

    audio_names = []
    # if dir is empty - save
    urls = []
    titles = []
    n_selected_music = ''

    bot.send_message(message.chat.id, language_phrases[5])
    bot.send_chat_action(message.chat.id, 'upload_audio')

    try:
        for i in range(len(musics5["extra_music"])):
            url = musics5["extra_music"][i]["download-link"]
            title = musics5["extra_music"][i]["title"]
            title = re.sub(r"[#%!@*']", "", title)
            title = re.findall(r"[\w']+", title)
            title = '_'.join(title)
            titles.append(title)
            audio_name = os.path.join(audios_path, title + '.mp3')
            audio_names.append(audio_name)

            # add | to url to get audio_name from download_url func
            # and do not download soundtracks which are in the dir
            if not title + '.mp3' in os.listdir(audios_path) \
                    and not title + '_trim.mp3' in os.listdir(audios_path):
                print("added title", title)
                url += '|' + audio_name
                urls.append(url)
    except:
        print('send_other_musics error -  range(len(musics5["extra_music"]))')
        bot.send_message(message.chat.id, error_phrases[4])

    try:
        # checking if this audio_names not in dir for get similar music -> change genre ->
        # -> get similar music and do not download musics that are in the dir
        if urls:
            # Run several multiple threads. Each call will take the next element in urls list
            # download urls
            pool = ThreadPool(len(urls))
            results = pool.map(download_url, urls)
            pool.close()

            proc = []

            # cut soundtracks which are longer 60 sec
            for url in urls:
                print("audio_name0", url)

                p = Process(target=cut_music, args=(url,))
                p.start()
                proc.append(p)

                n_selected_music = musics5["selected_music"]

            for p in proc:
                p.join()

            gc.collect()

        try:
            with open(full_file_path + ".json", "r") as f:
                data = json.loads(f.read())

            n_selected_music = data["selected_music"]

        except:
            print('send_other_musics error - data = json.loads(f.read())')
            bot.send_message(message.chat.id, error_phrases[4])

    except:
        print('send_other_musics error -  range(len(musics5["extra_music"])) '
              'or  pool = '
              'ThreadPool(len(musics5["extra_music"]))')
        bot.send_message(message.chat.id, error_phrases[4])

    if n_selected_music != '':
        try:
            with open(full_file_path + "_data" + ".json", "r", encoding='utf-8') as f:
                file_user_data = json.load(f)
                file_user_data["n_selected_music"] = n_selected_music

            with open(full_file_path + "_data" + ".json", "w") as f:
                json.dump(file_user_data, f)
        except:
            print('send_other_musics error - file_user_data["n_selected_music"] = n_selected_music')
            bot.send_message(message.chat.id, error_phrases[4])

        try:
            language_phrases = phrase_on_language(message, "send_other_musics")

        except:
            create_users_data_dir(message)
            language_phrases = phrase_on_language(message, "send_other_musics")

        audios = []
        # add mark to name to trimmed audios which now are less than 60 sec
        # it is special to delete a full audio from dir and save time
        for audio_name in audio_names:
            try:
                try:
                    audio = open(audio_name, 'rb')
                except:
                    pos = audio_name.rfind('.')
                    audio_name = audio_name[:pos] + "_trim" + audio_name[pos:]
                    audio = open(audio_name, 'rb')
                audios.append(audio)

            except:
                print('send_other_musics error - audio = open(audio_name')
                bot.send_message(message.chat.id, error_phrases[4])

        n_on_button_audios = [0 for i in range(5)]
        n_audio = 1
        for i in range(len(n_on_button_audios)):
            if i == n_selected_music:
                n_on_button_audios[i] = 0

            else:
                n_on_button_audios[i] = n_audio
                n_audio += 1

        try:
            for i in range(len(musics5["extra_music"])):
                if n_on_button_audios[i] != 0:
                    if i == 0:
                        bot.send_audio(message.chat.id, audios[i])

                    else:
                        bot.send_audio(message.chat.id, audios[i], disable_notification=True)

        except:
            pass
        length_cycle = len(audios)

        keyboard = telebot.types.InlineKeyboardMarkup()

        n_audio_buttons = []
        for i in range(length_cycle):
            if n_on_button_audios[i] != 0:
                callback_button = telebot.types.InlineKeyboardButton(text=str(n_on_button_audios[i]),
                                                                     callback_data='audio_' + str(i))
                n_audio_buttons.append(callback_button)

        keyboard.add(*n_audio_buttons)
        bot.send_message(message.chat.id, language_phrases[1],
                         reply_markup=keyboard)

        for audio in audios:
            audio.close()

    else:
        print("send_other_musics ERROR")
        bot.send_message(message.chat.id, error_phrases[4])


def confirm_answer_keyboard(message, answer_user_language):
    """
    :return: a keyboard to answer if user want to upload this video
    """
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)

    type_input = answer_user_language[2][0]
    markup.add(type_input)

    type_input = answer_user_language[2][1]
    markup.add(type_input)

    bot.send_message(message.chat.id, answer_user_language[0], reply_markup=markup)
