import base64
import json
import os
import gc
import logging

from datetime import date, datetime
from threading import Thread

import requests
import telebot
import telegram

from transliterate import translit
from bs4 import BeautifulSoup
from telebot import types

from additional_functions_dir.files_functions import update_n_videos_last_upload
from additional_functions_dir.fucntions_with_video import (
    delete_previous_video,
    clean_audio_change_upload,
)
from additional_functions_dir.paymnet_functions import check_subscription
from additional_functions_dir.renovate_buy_user_id_web import renovate_buy_user_id_web
from additional_functions_dir.renovate_id_code import renovate_id_code_db
from additional_services.liqpay import LiqPay
from telebot.types import LabeledPrice
from flask import request, redirect, render_template

from additional_functions import (
    send_typing_action,
    send_other_musics,
    confirm_answer_keyboard,
    write_in_user_file,
    add_logs
)

from additional_functions_dir.buttons import (
    improve_and_upload_buttons,
    language_buttons,
    make_continue_editing_button,
    start_upload_video_buttons,
    upload_less_20,
)
from additional_functions_dir.buttons import payment_buttons, more_20_mb_videos_buttons
from additional_functions import allowed_file

from harmix_db.main_db import db, app
from harmix_db.models import Survey, Users

from survey import (
    get_survey_button,
    keyboard_buttons_survey,
    opt_answers_in_dict_from_buttons,
    opt_answers_in_dict,
)
from additional_functions_dir.create_user_data_dir import create_users_data_dir
from harmix_db.main_db_functions import (
    update_sql,
    if_user_in_db,
    insert_new_survey_answer,
    insert_first_survey,
)
from language_functions import phrase_on_language
from additional_functions_dir.get_username import create_username_for_db
from additional_functions_dir.informate_all_functions import (
    informate_all_end,
    informate_all,
    is_informate_all,
    save_photo,
    save_input_values,
)

bot = telebot.TeleBot(API_TOKEN)

# More about Payments: https://core.telegram.org/bots/payments
prices = [
    LabeledPrice(label="Uploading video files more than 20 MB", amount=50),
    LabeledPrice("Adding fade effects to your video", 50),
]


@bot.message_handler(commands=["start"])
def start_message(message):
    create_users_data_dir(message)
    try:
        user_info = message.from_user
    except:
        user_info = message.message.from_user
    username = user_info.first_name
    try:
        username = translit(username, reversed=True)
    except: pass
    bot.send_message(
        message.chat.id,
        "Hi, {}! I'm Harmix bot рџ™‚\n"
        "I can help you to choose the right music for your video".format(
            username
        ),
    )
    bot.send_message(
        message.chat.id,
        "By continuing to work, you agree to the <a href='{}'>Upload Terms</a>, "
        "<a href='{}'>Terms of Use</a> and <a href='{}'>Privacy Policy</a>.".format(
            UPLOAD_TERM, TERM_OF_USE, PRIVACY_POLICY
        ),
        parse_mode=telegram.ParseMode.HTML,
        disable_web_page_preview=True,
    )

    username = create_username_for_db(message)
    if_user_in_db(message, str(message.chat.id), username)
    choose_language_buttons(message)


@bot.message_handler(commands=["info"])
def send_info(message):
    try:
        language_phrases = phrase_on_language(message, "send_info")

    except:
        create_users_data_dir(message)
        language_phrases = phrase_on_language(message, "send_info")

    bot.send_message(message.chat.id, language_phrases)


@bot.message_handler(commands=["terms_of_use"])
def send_terms_of_use(message):
    bot.send_message(message.chat.id, TERM_OF_USE)


@bot.message_handler(commands=["upload_terms"])
def send_upload_terms(message):
    bot.send_message(message.chat.id, UPLOAD_TERM)


@bot.message_handler(commands=["privacy_policy"])
def send_privacy_policy(message):
    bot.send_message(message.chat.id, PRIVACY_POLICY)


@bot.message_handler(commands=["support"])
def send_support(message):
    try:
        language_phrases = phrase_on_language(message, "send_support")

    except:
        create_users_data_dir(message)
        language_phrases = phrase_on_language(message, "send_support")

    bot.send_message(
        message.chat.id,
        language_phrases[0].format(ADMINS_USERNAMES[0], ADMINS_USERNAMES[1]),
    )


def command_pay(message):
    bot.send_invoice(
        message.chat.id,
        title="рџЏ† Harmix Pro РµР¶РµРјРµСЃСЏС‡РЅС‹Р№ С‚Р°СЂРёС„РЅС‹Р№ РїР»Р°РЅ рџЏ†",
        description="Harmix bot premium functions",
        provider_token=PROVIDER_PAY_TOKEN,
        currency="USD",
        is_flexible=False,  # True If you need to set up Shipping Fee
        prices=prices,
        start_parameter="harmix-bot-month-subscription",
        invoice_payload="HARMIX BOT MONTH SUBSCRIPTION",
    )


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(
        pre_checkout_query.id,
        ok=True,
        error_message="Aliens tried to steal your card's CVV, but we successfully protected "
        "your credentials, "
        " try to pay again in a few minutes, we need a small rest.",
    )


@bot.message_handler(commands=["buy_subscription"])
def buy_subscription(message):
    payment_buttons(message)


@bot.message_handler(commands=["subscription_status"])
def subscription_status(message):
    user_chat_id = str(message.chat.id)
    try:
        language_phrases = phrase_on_language(message, "subscription_status")
        error_phrases = phrase_on_language(message, "subscription_status")

    except:
        create_users_data_dir(message)
        language_phrases = phrase_on_language(message, "subscription_status")
        error_phrases = phrase_on_language(message, "subscription_status")

    try:
        if check_subscription(user_chat_id):
            user_data_db = Users.query.filter_by(chat_id=user_chat_id).first()
            bot.send_message(
                message.chat.id,
                language_phrases[0].format(user_data_db.subscription_term),
                parse_mode=telegram.ParseMode.HTML,
            )

        else:
            bot.send_message(
                message.chat.id, language_phrases[1], parse_mode=telegram.ParseMode.HTML
            )

    except:
        print("subscription_status ERROR")
        bot.send_message(message.chat.id, error_phrases[2])


@bot.message_handler(content_types=["successful_payment"])
def got_payment(message, user_chat_id=""):
    if user_chat_id != "":
        message_chat_id = int(user_chat_id)

    else:
        user_chat_id = str(message.chat.id)
        message_chat_id = message.chat.id

    try:
        language_phrases = phrase_on_language(message, "got_payment", user_chat_id)

    except:
        create_users_data_dir(message)
        language_phrases = phrase_on_language(message, "got_payment", user_chat_id)

    bot.send_message(
        message_chat_id, language_phrases[0], parse_mode=telegram.ParseMode.HTML
    )

    try:
        # update subscription_end_day in db after payment
        user_data_db = Users.query.filter_by(chat_id=user_chat_id).first()
        if message == "":
            print(
                "user_data_db.last_message_before_pay",
                user_data_db.last_message_before_pay,
            )
            message = json.loads(user_data_db.last_message_before_pay)

        start_day = date.today()
        subscription_end_month = start_day.month + 1
        subscription_end_day = date(
            start_day.year, subscription_end_month, start_day.day
        )
        print("subscription_end_day", subscription_end_day)

        update_sql(
            "users_data", "subscription_term", user_chat_id, str(subscription_end_day)
        )

        if user_data_db.last_function_before_pay == "fade_effects":
            change_parameters_buttons(message)

        elif user_data_db.last_function_before_pay == "upload_more_20mb":
            more_20_mb_videos_buttons(message, user_data_db)
    except:
        print("Users.query.filter_by(chat_id=user_chat_id) ERROR")


@bot.message_handler(content_types=["photo"])
def get_photo(message):
    if is_informate_all(message, "uk"):
        save_photo(message, "uk")
    elif is_informate_all(message, "ua"):
        save_photo(message, "ua")
    elif is_informate_all(message, "ru"):
        save_photo(message, "ru")


def pre_checkout_callback(update):
    print("pre_checkout_callback")
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload != "Custom-Payload":
        # answer False pre_checkout_query
        query.answer(ok=False, error_message="Something went wrong...")
    else:
        query.answer(ok=True)


@bot.message_handler(content_types=["video"])
def get_video(message):
    user_chat_id = str(message.chat.id)
    username, language_phrases, error_phrases = clean_audio_change_upload(
        message, user_chat_id
    )
    if_user_in_db(message, user_chat_id, username)

    try:
        file_id = message.video.file_id
        file_size = message.video.file_size
        if file_size <= 20 * 10 ** 6:
            file_info = bot.get_file(file_id)
            start_position_extension = str(file_info.file_path).rfind(".")
            file_extension = str(file_info.file_path)[start_position_extension + 1:]
        else:
            start_position_extension = str(message.video.mime_type).rfind("/")
            file_extension = str(message.video.mime_type)[start_position_extension + 1:]

        # mkdir for special user
        path = "users_data/{}".format(user_chat_id)
        try:
            os.mkdir(path)
        except OSError:
            print("Creation of the directory %s failed or this directory exists" % path)
        else:
            print("Successfully created the directory %s " % path)

        with open(
            os.path.join(
                os.getcwd(), "users_data", user_chat_id, user_chat_id + "_data.json"
            ),
            "r",
            encoding="utf=8",
        ) as user_file:
            user_file_json = json.load(user_file)
            user_file_json["video_name"] = user_chat_id + "." + file_extension
            user_file_json["file_id"] = file_id
            user_file_json["chat_id"] = user_chat_id
            user_file_json["file_size"] = file_size
            user_file_json["get_url"] = 0

            user_file_json["file_extension"] = file_extension

        with open(
            os.path.join("users_data", user_chat_id, user_chat_id + "_data.json"),
            "w",
            encoding="utf-8",
        ) as user_data:
            json.dump(user_file_json, user_data, ensure_ascii=False, indent=4)

        if_user_in_db(message, user_chat_id, username)
        confirm_answer_keyboard(message, language_phrases)

    except:
        print(
            "get_video ERROR - file_id = message.video.file_id or "
            "downloaded_file = bot.download_file(file_info.file_path or new_file.write(downloaded_file))"
        )
        bot.send_message(message.chat.id, error_phrases[4])


@bot.message_handler(content_types=["document"])
def get_user_file(message):
    user_chat_id = str(message.chat.id)
    username, language_phrases, error_phrases = clean_audio_change_upload(
        message, user_chat_id
    )

    if_user_in_db(message, user_chat_id, username)

    try:
        file_id = message.document.file_id
        start_position_extension = str(message.document.file_name).rfind(".")
        file_extension = str(message.document.file_name)[start_position_extension + 1:]
        with open(
            os.path.join("users_data", user_chat_id, user_chat_id + "_data.json"),
            "r",
            encoding="utf-8",
        ) as user_data:
            json_user_data = json.load(user_data)
            json_user_data["file_id"] = file_id
            json_user_data["chat_id"] = user_chat_id
            json_user_data["get_url"] = 0

            json_user_data["file_size"] = message.document.file_size
            json_user_data["chat_id"] = user_chat_id

            json_user_data["file_extension"] = file_extension

        with open(
            os.path.join("users_data", user_chat_id, user_chat_id + "_data.json"),
            "w",
            encoding="utf-8",
        ) as user_data:
            json.dump(json_user_data, user_data, ensure_ascii=False, indent=4)

        if_user_in_db(message, user_chat_id, username)
        confirm_answer_keyboard(message, language_phrases)

    except:
        print(
            "get_document ERROR - file_id = message.video.file_id or "
            "downloaded_file = bot.download_file(file_info.file_path or new_file.write(downloaded_file))"
        )
        bot.send_message(message.chat.id, error_phrases[4])


def download_file_after_confirm(message):
    user_chat_id = str(message.chat.id)
    try:
        language_phrases = phrase_on_language(message, "get_video_less_20")
        error_phrases = phrase_on_language(message, "send_video_to_user")

    except:
        create_users_data_dir(message)
        language_phrases = phrase_on_language(message, "get_video_less_20")
        error_phrases = phrase_on_language(message, "send_video_to_user")

    try:
        with open(
            os.path.join("users_data", user_chat_id, user_chat_id + "_data.json"),
            "r",
            encoding="utf-8",
        ) as user_data:
            user_file_json = json.load(user_data)
            file_id = user_file_json["file_id"]
            file_size = user_file_json["file_size"]
            file_extension = user_file_json["file_extension"]
    except:
        print("download_file_after_confirm ERROR - json.load(user_data)")
        bot.send_message(message.chat.id, error_phrases[4])

    if "username_for_db" not in user_file_json.keys():
        username_for_db = create_username_for_db(message)
        user_file_json["username_for_db"] = username_for_db

    try:
        # check a size of the video
        if file_size <= 20 * 10 ** 6:
            if file_extension.lower() in ALLOWED_EXTENSIONS:
                file_info = bot.get_file(file_id)

                # mkdir for special user
                path = "users_data/{}".format(user_chat_id)
                try:
                    os.mkdir(path)
                except OSError:
                    print(
                        "Creation of the directory %s failed or this directory exists"
                        % path
                    )
                else:
                    print("Successfully created the directory %s " % path)

                user_file_json["video_name"] = user_chat_id + "." + file_extension
                downloaded_file = bot.download_file(file_info.file_path)

                # trying to change directory and download a video to user's dir
                full_file_path = os.path.join(
                    os.getcwd(), "users_data", user_chat_id, user_chat_id
                )
                with open(full_file_path + "." + file_extension, "wb") as new_file:
                    new_file.write(downloaded_file)

            else:
                print("bad a format of file")
                bot.send_message(message.chat.id, language_phrases[1])

        else:
            print("more 20 mb upload file")

            user_data_db = Users.query.filter_by(chat_id=user_chat_id).first()
            update_sql("users_data", "video_size_buttons", user_chat_id, "1")

            if check_subscription(user_chat_id):
                more_20_mb_videos_buttons(message, user_data_db)
            else:
                payment_buttons(message, "premium_function1")

        with open(
            os.path.join(
                os.getcwd(), "users_data", user_chat_id, user_chat_id + "_data.json"
            ),
            "w",
            encoding="utf=8",
        ) as user_file:
            json.dump(user_file_json, user_file, ensure_ascii=False, indent=4)

    except:
        print("download_file_after_confirm ERROR - general")
        bot.send_message(message.chat.id, error_phrases[4])


@bot.message_handler(commands=["change_language"])
def choose_language_buttons(message):
    """
    :return: a keyboard with languages to change
    """
    language_buttons(message)


@bot.message_handler(commands=["start_survey"])
def survey_buttons(message):
    """
    :return: a button to start a survey
    """
    get_survey_button(message)


def start_survey(message, n_question=0):
    """
    :return: start every new question for user
    """
    try:
        user_chat_id = str(message.chat.id)
    except:
        user_chat_id = str(message.message.chat.id)

    try:
        questions = phrase_on_language(message, "questions")
    except:
        create_users_data_dir(message)
        questions = phrase_on_language(message, "questions")

    try:
        n_question = int(message.data[-1]) + 1
        message = message.message
    except:
        pass

    if n_question == 0:
        keyboard_buttons_survey(message, questions[n_question])
        username = create_username_for_db(message)
        full_file_path = os.path.join(
            os.getcwd(), "users_data", user_chat_id, user_chat_id
        )
        print("before if user_chat_id not in os.listdir in start_survey")

        if user_chat_id not in os.listdir(
            "users_data"
        ) or user_chat_id + "_data.json" not in os.listdir(
            os.path.join("users_data", user_chat_id)
        ):
            create_users_data_dir(message)
            print("get file_user_data['n_surveys'] ERROR")

        with open(full_file_path + "_data" + ".json", "r", encoding="utf-8") as f:
            file_user_data = json.load(f)

            if file_user_data["n_surveys"] >= 1:
                try:
                    insert_new_survey_answer(
                        user_chat_id, file_user_data["n_surveys"], username
                    )

                except:
                    # make rollback if error in db
                    db.session.rollback()
                    insert_new_survey_answer(
                        user_chat_id, file_user_data["n_surveys"], username
                    )

            else:
                try:
                    insert_first_survey(user_chat_id, username)

                except:
                    db.session.rollback()
                    insert_first_survey(user_chat_id, username)

    # if the question need buttons to answer
    elif n_question == 1:
        keyboard_buttons_survey(message, questions[n_question])
    elif n_question in (2, 3):
        bot.send_message(message.chat.id, questions[n_question])

    # if user writes answer without buttons
    if n_question < 4:
        write_in_user_file(
            message, n_question, "n_answered_question", function="make_new"
        )

    # after last question - print thank you
    elif n_question >= 4:
        msg_thanks = phrase_on_language(message, "start_survey")
        bot.send_message(message.chat.id, "рџ„рџ‘Ќ " + msg_thanks)
        write_in_user_file(
            message, 1, "n_surveys", user_chat_id="", function="change_number"
        )
        write_in_user_file(
            message, 0, "n_answered_question", user_chat_id="", function="make_new"
        )

        upload_new_video = phrase_on_language(message, "start_message")
        bot.send_message(message.chat.id, upload_new_video)


def answers_in_dict_from_buttons(answer):
    """
    :param answer: a callback from buttons of the question
    :return: write answer in answers_on_survey.json to analys all comments of users on the survey
    """
    # n_question is the last digit from answer that I added in keyboard_buttons_survey function in callback
    n_question = 0
    try:
        n_question = int(answer.data[-1])
    except:
        pass

    opt_answers_in_dict_from_buttons(answer, n_question)

    if n_question < 2:
        start_survey(answer, n_question + 1)


def answers_in_dict(answer, n_question):
    """
   :param answer: user answer without buttons
   :return: write answer in answers_on_survey.json to analys all comments of users on the survey
   """
    print("get answer_in_dict")
    opt_answers_in_dict(answer, n_question)
    write_in_user_file(answer, 0, "n_answered_question", "", function="make_new")

    # give a new question
    start_survey(answer, n_question + 1)


@bot.message_handler(commands=["upload_new_video"])
def upload_new_video(message):
    """
    :return: a question if user want to upload this video
    """
    user_chat_id = str(message.chat.id)
    if_user_in_db(message, user_chat_id)

    user = Users.query.filter_by(chat_id=user_chat_id).first()
    if user.video_size_buttons == "1":
        start_upload_video_buttons(message)
    elif user.video_size_buttons == "0":
        upload_less_20(message)
        # simple_upload_video_buttons(message)


@bot.message_handler(commands=["informate_all_UK"])
def informate_all_uk(message):
    informate_all(message, "uk")


@bot.message_handler(commands=["informate_all_UK_end"])
def informate_all_uk_end(message):
    informate_all_end(message, "uk")


@bot.message_handler(commands=["informate_all_UA"])
def informate_all_ua(message):
    informate_all(message, "ua")


@bot.message_handler(commands=["informate_all_UA_end"])
def informate_all_ua_end(message):
    informate_all_end(message, "ua")


@bot.message_handler(commands=["informate_all_RU"])
def informate_all_ru(message):
    informate_all(message, "ru")


@bot.message_handler(commands=["informate_all_RU_end"])
def informate_all_ru_end(message):
    informate_all_end(message, "ru")


@bot.message_handler(content_types=["text"])
def get_text(message):
    flag_informate = 0

    if message.from_user.id in ADMINS_CHAT_ID:
        # if user choose the same parameter in keyboard like вњ…Enable
        if is_informate_all(message, "uk"):
            save_input_values(message, "uk")
            flag_informate = 1
        elif is_informate_all(message, "ua"):
            save_input_values(message, "ua")
            flag_informate = 1
        elif is_informate_all(message, "ru"):
            save_input_values(message, "ru")
            flag_informate = 1

    if flag_informate == 0:
        if message.text.startswith("вњ…"):
            message.text = message.text[1:]

        user_chat_id = str(message.chat.id)
        error_phrases = phrase_on_language(message, "send_video_to_user")

        # answer on Are you sure that you want to upload this video? (Type YES/NO)
        yes_lst = ["YES", "РўРђРљ", "Р”Рђ"]
        no_lst = ["NO", "РќР†", "РќР•Рў"]
        try:
            language_phrases = phrase_on_language(message, "get_text")
        except:
            create_users_data_dir(message)
            language_phrases = phrase_on_language(message, "get_text")

        try:
            ready_ans = message.text.strip().upper()
            try:
                with open(
                    os.path.join(
                        "users_data", user_chat_id, user_chat_id + "_data.json"
                    ),
                    "r",
                    encoding="utf-8",
                ) as user_file:
                    user_json = json.load(user_file)
                    n_answered_question = user_json.get("n_answered_question", 0)
            except:
                n_answered_question = -1
                print("get_text ERROR - no such file")

            print("n_answered_question", n_answered_question)
            if n_answered_question in (2, 3):
                answers_in_dict(message, n_answered_question)

            elif ready_ans in yes_lst:
                bot.send_message(message.from_user.id, "рџ¤–рџ”ЃрџЋћв†ЄпёЏрџЋ¶ " + language_phrases[0])

                download_file_after_confirm(message)
                with open(
                    os.path.join(
                        "users_data", user_chat_id, user_chat_id + "_data.json"
                    ),
                    "r",
                    encoding="utf-8",
                ) as user_file:
                    user_json = json.load(user_file)
                    file_extension = user_json["file_extension"]

                if user_chat_id + "." + file_extension in os.listdir(
                    os.path.join("users_data", user_chat_id)
                ):
                    adapt_video(message)

            elif ready_ans in no_lst:
                language_phrases = phrase_on_language(message, "start_message")
                bot.send_message(message.chat.id, language_phrases)

            else:
                try:
                    # take text parameter for changing from user and send it to new keyboard
                    full_file_path = os.path.join(
                        os.getcwd(), "users_data", user_chat_id, user_chat_id
                    )

                    flag_stop_func = 0
                    try:
                        data = json.load(
                            open(full_file_path + ".json", "r", encoding="utf-8")
                        )
                    except:
                        print("ERROR: no full_file_path + '.json'")
                        error_phrases = phrase_on_language(message, "send_video_to_user")
                        bot.send_message(user_chat_id, error_phrases[4])
                        flag_stop_func = 1

                    if flag_stop_func != 1:
                        parameters = [
                            "genre",
                            "mood",
                            "instrument",
                            "vocal",
                            "fade_effects",
                            "original_video_volume",
                            "music_volume",
                            "number_of_video_tracks",
                        ]

                        # find a list of parameters with special user language
                        language_parameters = phrase_on_language(message, "parameters")
                        full_phrases_path = os.path.join(
                            os.getcwd(), "templates", "phrases"
                        )

                        with open(
                            full_phrases_path + ".json", "r", encoding="utf-8"
                        ) as f:
                            phrases = json.load(f)
                            dict_uk_choices = phrases["choices"]["uk"]

                        with open(full_file_path + ".json", "w", encoding="utf-8") as f:
                            json.dump(data, f, ensure_ascii=False, indent=4)

                        dict_language_choices = phrase_on_language(message, "choices")

                        changed_parameter = ""

                        for key in dict_language_choices.keys():
                            if message.text in dict_language_choices[key]:
                                flag_message_in_choices = 1
                                changed_parameter = str(key)
                                break

                        # if user change parameter and buttons appear second time -
                        # if input_parameter 'vocal' then message.text in int and then input in data.json
                        if flag_message_in_choices == 1:
                            position_uk_parameter = language_parameters.index(
                                changed_parameter
                            )
                            uk_parameter = parameters[position_uk_parameter]

                            # it does not work for "music_volume": ["10 ","20 ","40 ","60 ", "80 ", "100 "]
                            if message.text[-1].isdigit():
                                if message.text == "0.5":
                                    data[uk_parameter] = 0.5
                                elif message.text == "0" or message.text == "1":
                                    data[uk_parameter] = int(message.text)
                            else:
                                position = dict_language_choices[changed_parameter].index(
                                    message.text
                                )
                                if message.text in ["Enable", "РЈРІС–РјРєРЅРµРЅС–", "Р’РєР»СЋС‡РµРЅРЅС‹Рµ"]:
                                    data[uk_parameter] = 1
                                elif message.text in ["Disable", "Р’РёРјРєРЅРµРЅС–", "Р’С‹РєР»СЋС‡РµРЅРЅС‹Рµ"]:
                                    data[uk_parameter] = 0
                                else:
                                    data[uk_parameter] = dict_uk_choices[uk_parameter][
                                        position
                                    ]

                            try:
                                with open(
                                    full_file_path + ".json", "w", encoding="utf-8"
                                ) as f:
                                    json.dump(data, f)

                            except:
                                print(
                                    "get_text ERROR - dict_uk_choices = phrases['choices']['uk']"
                                )
                                bot.send_message(message.chat.id, error_phrases[4])

                            change_parameters_buttons(message)

                        elif flag_message_in_choices != 1:
                            print("get_text-------------------------------------")
                            bot.send_message(message.chat.id, language_phrases[1])

                except:
                    bot.send_message(message.chat.id, language_phrases[1])

        except:
            print("get_text ERROR general")
            bot.send_message(
                message.chat.id, "Something went wrong, please upload your video again"
            )


@send_typing_action
def adapt_video(message):
    """
    :return: post to server, get json and, if user wish, change parameters with keyboard
    """
    if isinstance(message, dict):
        user_chat_id = message["chat"]["id"]

    else:
        user_chat_id = str(message.chat.id)

    full_file_path = os.path.join(os.getcwd(), "users_data", user_chat_id, user_chat_id)
    error_phrases = phrase_on_language(message, "send_video_to_user")

    try:
        with open(
            os.path.join(
                os.getcwd(), "users_data", user_chat_id, user_chat_id + "_data.json"
            ),
            "r",
            encoding="utf=8",
        ) as user_file:
            user_file_json = json.load(user_file)

        full_video_path = os.path.join(
            os.getcwd(), "users_data", user_chat_id, user_file_json["video_name"]
        )
        # Open video and send POST with video to server
        with open(full_video_path, "rb") as video_file:
            file_ = {"file": (user_file_json["video_name"], video_file)}
            upload_response = requests.post(upload_url, files=file_)

        gc.collect()
        # Get json and, if user wish, change parameters
        data = json.loads(upload_response.text)

        data["fade_effects"] = 0
        data["music_volume"], data["original_video_volume"] = "100%", "0 %"

        if not user_file_json.get("get_url", 0):
            data["get_url"] = 0

        else:
            data["get_url"] = 1

        print("data[get_url]", data["get_url"])
        print("adapt-----------------------------------")

        data["selected_music"] = 0
        with open(full_file_path + ".json", "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        # delete should be in this place exactly after sending post to server
        delete_previous_video(user_chat_id)

    except:
        print(
            "adapt_video ERROR - upload_response = requests.post(upload_url, files=file_) "
            "or json.dump(data, f)"
        )
        bot.send_message(message.chat.id, error_phrases[4])

    skip_flag = 1
    change_parameters_buttons(message, skip_flag)


def send_video_to_user(message):
    bot.send_chat_action(message.chat.id, "upload_video")
    user_chat_id = str(message.chat.id)
    error_phrases = phrase_on_language(message, "send_video_to_user")
    try:
        language_phrases = phrase_on_language(message, "send_video_to_user")
    except:
        create_users_data_dir(message)
        language_phrases = phrase_on_language(message, "send_video_to_user")

    full_file_path = os.path.join(os.getcwd(), "users_data", user_chat_id, user_chat_id)

    try:
        try:
            with open(full_file_path + ".json", "r") as f:
                data = json.load(f)
        except:
            print("ERROR: no user_dir")
            create_users_data_dir(message)

        # post json file with parameters changed by user and send it to user
        combine_response = requests.post(combine_url, json=data)
        gc.collect()

        print(
            'combine_response.headers["Content-Type"]',
            combine_response.headers["Content-Type"],
        )

        # a json of 5 musics that also can be special for this video
        music_data = json.loads(combine_response.headers["X-Extra-Info-JSON"])
        print("music_data in send_video", music_data)

        with open(full_file_path + "musics5_for_video" + ".json", "w") as musics5_file:
            json.dump(music_data, musics5_file, indent=4)

        # if video too long - send a link to download adapted video
        if combine_response.headers["Content-Type"][:4] == "text":
            video_url = (
                combine_response.content.decode()
                + "?t="
                + str(datetime.now()).replace(" ", "_").replace(":", "-")
            )
            music_url = music_data["extra_music"][music_data["selected_music"]][
                "download-link"
            ]
            bot.send_message(
                message.chat.id,
                language_phrases[6].format(video_url, music_url),
                parse_mode=telegram.ParseMode.HTML,
            )
            update_n_videos_last_upload(message, user_chat_id)
            improve_and_upload_buttons(message)
            gc.collect()

        else:
            # if video less 20 mb - send a video in telegram
            binary_string = combine_response.content

            with open(
                os.path.join(
                    os.getcwd(), "users_data", user_chat_id, user_chat_id + "_data.json"
                ),
                "r",
                encoding="utf=8",
            ) as user_file:
                user_file_json = json.load(user_file)

            video_from_server_path = os.path.join(
                os.getcwd(),
                "users_data",
                user_chat_id,
                "downloaded_video_" + user_file_json["video_name"],
            )

            with open(video_from_server_path, "wb") as video_file:
                video_file.write(binary_string)

            gc.collect()

            file_size = 0
            # Get the size (in bytes)
            # of specified path
            try:
                file_size = os.path.getsize(video_from_server_path)
            except:
                print(
                    "Path '%s' does not exists or is inaccessible"
                    % video_from_server_path
                )

            try:
                if file_size < 2 * 10 ** 7 and file_size != 0:
                    with open(video_from_server_path, "rb") as video:
                        bot.send_message(message.chat.id, "рџ†•рџЋ¬ " + language_phrases[0])
                        if combine_response.headers["Content-Type"][:5] == "video" \
                                and combine_response.headers["Content-Type"][6:9] != "mp4":
                            bot.send_document(
                                message.chat.id,
                                video,
                                caption=language_phrases[1],
                                parse_mode=telegram.ParseMode.HTML,
                            )

                        else:
                            bot.send_video(
                                message.chat.id,
                                video,
                                caption=language_phrases[1],
                                parse_mode=telegram.ParseMode.HTML,
                            )

                    update_n_videos_last_upload(message, user_chat_id)
                    os.remove(video_from_server_path)
                    print("send send_video improve_buttons")
                    improve_and_upload_buttons(message)
                    gc.collect()
            except:
                print(
                    "send_video_to_user ERROR -  json.dump(file_user_data, f) "
                    "or update_sql('users_data', 'n_videos', username, file_user_data[\"n_videos\"]) or"
                    'file_user_data["n_videos"] = file_user_data.get("n_videos", 0) + 1'
                )
                bot.send_message(message.chat.id, error_phrases[4])

    except:
        print(
            "send_video_to_user ERROR - data = json.load(f) or video_file.write(binary_string) "
            "or json.dump(music_data, musics5_file, indent=4)"
        )
        bot.send_message(message.chat.id, error_phrases[4])


@send_typing_action
def change_parameters_buttons(message, skip_flag=0):
    """

    :return: a keyboard with video  or changed by user parameters
    """
    if isinstance(message, dict):
        user_chat_id = message["chat"]["id"]
        message_chat_id = int(user_chat_id)
    else:
        user_chat_id = str(message.chat.id)
        message_chat_id = message.chat.id

    error_phrases = phrase_on_language(message, "send_video_to_user")

    try:
        button_parameters = phrase_on_language(message, "parameters")
        vocal_marks = phrase_on_language(message, "vocal_marks")
        fade_marks = phrase_on_language(message, "fade_marks")

    except:
        create_users_data_dir(message)
        button_parameters = phrase_on_language(message, "parameters")
        vocal_marks = phrase_on_language(message, "vocal_marks")
        fade_marks = phrase_on_language(message, "fade_marks")

    full_file_path = os.path.join(os.getcwd(), "users_data", user_chat_id, user_chat_id)

    keyboard = telebot.types.InlineKeyboardMarkup()
    data = dict()
    try:
        data = json.load(open(full_file_path + ".json", "r", encoding="utf-8"))

        parameters = [
            "genre",
            "mood",
            "instrument",
            "vocal",
            "fade_effects",
            "original_video_volume",
            "music_volume",
        ]
        vocal_mark = ""

        # for change vocal on Lyrics and 0 or other digits on "Any lyrics", "Without lyrics", "With lyrics"
        # for print it in buttons for user(the same for fade_effects)
        
        fade_mark = ""
        if data["fade_effects"] == 0:
            fade_mark = fade_marks[0]

        elif data["fade_effects"] == 1:
            fade_mark = fade_marks[1]

        full_phrases_path = os.path.join(os.getcwd(), "templates", "phrases")
        with open(full_phrases_path + ".json", "r", encoding="utf-8") as f:
            phrases = json.load(f)
            dict_uk_choices = phrases["choices"]["uk"]

        dict_language_choices = phrase_on_language(message, "choices")

        print("parameter_buttons_change cycle")

        # display in keyboard all parameters from user_id_data.json
        for parameter in parameters:
            pos = parameters.index(parameter)

            language_parameter = button_parameters[pos]

            button_parameter = language_parameter[0].upper() + language_parameter[1:]

            button_parameter = " ".join(button_parameter.split("_"))
            if parameter == "vocal":
                if language_parameter in dict_uk_choices["vocal"]:
                    button_parameter = "Lyrics"

                keyboard.row(
                    telebot.types.InlineKeyboardButton(
                        "{0}: {1}".format(button_parameter, vocal_mark),
                        callback_data=parameter,
                    )
                )

            elif parameter == "fade_effects":
                if check_subscription(user_chat_id):
                    keyboard.row(
                        telebot.types.InlineKeyboardButton(
                            "{0}: {1}".format(button_parameter, fade_mark),
                            callback_data=parameter,
                        )
                    )

                else:
                    keyboard.row(
                        telebot.types.InlineKeyboardButton(
                            "{0}: {1}".format(button_parameter, fade_mark),
                            callback_data="premium_function0",
                        )
                    )

            else:
                position = dict_uk_choices[parameter].index(data[parameter])

                keyboard.row(
                    telebot.types.InlineKeyboardButton(
                        "{0}: {1}".format(
                            button_parameter,
                            dict_language_choices[language_parameter][position],
                        ),
                        callback_data=parameter,
                    )
                )

        # if parameters buttons appear first or after sent adapt video than add SKIP button
        if skip_flag == 1:
            language_phrases = phrase_on_language(message, "next")
            keyboard.row(
                telebot.types.InlineKeyboardButton(
                    "вЏ© " + language_phrases[0], callback_data="Next"
                )
            )

            language_phrases = phrase_on_language(message, "change_parameters_buttons")
            msg_buttons = bot.send_message(
                message_chat_id, "рџ’ЎрџЋЁрџЋј " + language_phrases, reply_markup=keyboard
            )

        # if parameters buttons appear not first or after sent adapt video than add CONTINUE button
        else:
            language_phrases = phrase_on_language(message, "next")
            keyboard.row(
                telebot.types.InlineKeyboardButton(
                    "вћЎпёЏ " + language_phrases[1], callback_data="Next"
                )
            )

            try:
                full_file_path = os.path.join(
                    os.getcwd(), "users_data", user_chat_id, user_chat_id
                )
                with open(
                    full_file_path + "_data" + ".json", "r", encoding="utf-8"
                ) as f:
                    file_user_data = json.load(f)
                    chat_id = file_user_data["chat_id"]
                    message_id = file_user_data["message_id_buttons"]
                    bot.delete_message(chat_id, message_id)

            except Exception:
                print("change_parameters_buttons ERROR - open file _data")

            language_phrases = phrase_on_language(message, "change_parameters_buttons")
            msg_buttons = bot.send_message(
                message_chat_id, "рџ’ЎрџЋЁрџЋј " + language_phrases, reply_markup=keyboard
            )

    except:
        print(
            "change_parameters_buttons ERROR -  data = json.load(open(full_file_path "
        )
        bot.send_message(message_chat_id, error_phrases[4])

    # save message_id of msg_buttons in user_id_data.json to delete this message when new buttons arise
    try:
        full_file_path = os.path.join(
            os.getcwd(), "users_data", user_chat_id, user_chat_id
        )
        with open(full_file_path + "_data" + ".json", "r", encoding="utf-8") as f:
            file_user_data = json.load(f)
            message_id = msg_buttons.message_id
            file_user_data["message_id_buttons"] = message_id

        with open(full_file_path + "_data" + ".json", "w") as f:
            json.dump(file_user_data, f, ensure_ascii=False, indent=4)

    except:
        print(
            "change_parameters_buttons ERROR -   file_user_data['message_id_buttons'] = message_id"
        )


@bot.callback_query_handler(func=lambda call: True)
def take_input(query):
    """
    :param query: a data from  buttons function that is in callback
    """
    try:
        message = query["message"]
    except:
        message = query.message

    if isinstance(message, dict):
        user_chat_id = message["chat"]["id"]

    else:
        user_chat_id = str(message.chat.id)

    try:
        data = query.data
    except:
        data = query["data"]

    print("data query", data)
    try:
        language_phrases = phrase_on_language(message, "take_input")

    except:
        create_users_data_dir(message)
        language_phrases = phrase_on_language(message, "take_input")

    error_phrases = phrase_on_language(message, "send_video_to_user")

    # trying to change directory and download a video to user's dir
    full_file_path = os.path.join(os.getcwd(), "users_data", user_chat_id, user_chat_id)

    if data == "Next":
        bot.send_message(user_chat_id, language_phrases[0])
        send_video_to_user(message)

    # to take language that chose user and write in user_data.json
    elif (data == "ua") or (data == "ru") or (data == "uk"):
        try:
            try:
                with open(
                    full_file_path + "_data" + ".json", "r", encoding="utf-8"
                ) as f:
                    file_user_data = json.load(f)
                    file_user_data["language"] = data

                with open(full_file_path + "_data" + ".json", "w") as f:
                    json.dump(file_user_data, f, ensure_ascii=False, indent=4)
            except:
                create_users_data_dir(message)

        except:
            with open(full_file_path + "_data" + ".json", "r", encoding="utf-8") as f:
                file_user_data = json.load(f)
                file_user_data["language"] = data

            with open(full_file_path + "_data" + ".json", "w") as f:
                json.dump(file_user_data, f, ensure_ascii=False, indent=4)

        # update data in users_data table
        # username = create_username_for_db(message)
        print("lang", data)
        update_sql("users_data", "language", user_chat_id, data)

        language_phrases = phrase_on_language(message, "start")
        upload_new_video(message)
        # start_upload_video_buttons(message)

    elif data == "survey":
        start_survey(message)

    elif data == "improve":
        send_other_musics(message)

    elif data == "change_music_params":
        change_parameters_buttons(message)

    elif data == "upload_new_video":
        upload_new_video(message)

    elif data == "upload_video2":
        upload_less_20(message)

    elif data == "video_more_20":
        username = create_username_for_db(message)
        if_user_in_db(message, user_chat_id, username)
        if check_subscription(user_chat_id):
            user_data_db = Users.query.filter_by(chat_id=user_chat_id).first()
            more_20_mb_videos_buttons(message, user_data_db)
        else:
            payment_buttons(message, "premium_function1")

    elif data == "original_video_volume":
        type_keyboard(message, data)

    elif data.startswith("audio_"):
        try:
            language_phrases = phrase_on_language(message, "get_text")

        except:
            create_users_data_dir(message)
            language_phrases = phrase_on_language(message, "get_text")

        bot.send_message(user_chat_id, language_phrases[0], disable_notification=True)

        full_file_path = os.path.join(
            os.getcwd(), "users_data", user_chat_id, user_chat_id
        )

        try:
            with open(full_file_path + ".json", "r") as json_about_video:
                video_data = json.loads(json_about_video.read())

            video_data["selected_music"] = int(data[-1])
            with open(full_file_path + ".json", "w") as f:
                json.dump(video_data, f, ensure_ascii=False, indent=4)

            send_video_to_user(message)
        except:
            print(
                "take_input ERROR -  video_data = json.loads(json_about_video.read())"
            )
            bot.send_message(user_chat_id, error_phrases[4])

    # send query to other function to write answer on questions with buttons in json
    elif "premium" in data:
        payment_buttons(message, data)

    elif data[-1].isdigit():
        print("answers_in_dict_from_buttons")
        answers_in_dict_from_buttons(query)

    elif data == "pay_in_telegram":
        command_pay(message)

    elif data == "continue_edit":
        # callback to button I uploaded video to the site to start adapt it
        with open(full_file_path + "_data" + ".json", "r", encoding="utf-8") as f:
            file_user_data = json.load(f)
            try:
                if file_user_data["video_name"] in os.listdir(
                    os.path.join("users_data", user_chat_id)
                ):
                    try:
                        language_phrases = phrase_on_language(message, "get_text")

                    except:
                        create_users_data_dir(message)
                        language_phrases = phrase_on_language(message, "get_text")

                    bot.send_message(user_chat_id, language_phrases[0])
                    adapt_video(message)

                else:
                    make_continue_editing_button(
                        message, str(user_chat_id), "", function="single_button"
                    )
            except:
                print(
                    "take_input ERROR -  video_data = json.loads(json_about_video.read())"
                )
                bot.send_message(user_chat_id, error_phrases[4])

    else:
        try:
            type_keyboard(message, data)
        except UnboundLocalError:
            print("ERROR !!! not data in user_dir")


def type_keyboard(message, data):
    """
    :return: make a keyboard of different lists of parameters ("genre", 'mood', 'instrument', 'vocal', 'fade_effects')
    """
    error_phrases = phrase_on_language(message, "send_video_to_user")

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    full_phrases_path = os.path.join(os.getcwd(), "templates", "phrases")
    with open(full_phrases_path + ".json", "r", encoding="utf-8") as f:
        phrases = json.load(f)
        dict_uk_choices = phrases["choices"]["uk"]

    parameters = [
        "genre",
        "mood",
        "instrument",
        "vocal",
        "fade_effects",
        "original_video_volume",
        "music_volume",
    ]

    # find a list of parameters with special user language
    pos = parameters.index(data)
    try:
        language_parameters = phrase_on_language(message, "parameters")
        dict_language_choices = phrase_on_language(message, "choices")
    except:
        create_users_data_dir(message)
        language_parameters = phrase_on_language(message, "parameters")
        dict_language_choices = phrase_on_language(message, "choices")

    type_list = dict_language_choices[language_parameters[pos]]
    uk_type_list = dict_uk_choices[parameters[pos]]
    if data == "vocal":
        type_list = phrase_on_language(message, "vocal_marks")

    elif data == "fade_effects":
        type_list = phrase_on_language(message, "fade_marks")

    user_chat_id = str(message.chat.id)
    full_file_path = os.path.join(os.getcwd(), "users_data", user_chat_id, user_chat_id)

    try:
        with open(full_file_path + ".json", "r") as f:
            file_data = json.load(f)
    except:
        print("type_keyboard ERROR -  file_data = json.load(f)")
        bot.send_message(message.chat.id, error_phrases[4])

    vocal_mark, fade_mark = "", ""
    for i, type_input in enumerate(type_list):
        # change parameter from user_video.json from 0 or 1 on words to input it in buttons
        if data in ["vocal", "РІРѕРєР°Р»"]:
            vocal_mark = file_data[data]
            vocal_marks = phrase_on_language(message, "vocal_marks")

        elif data == "fade_effects":
            fade_mark = file_data[data]
            fade_marks = phrase_on_language(message, "fade_marks")

            if fade_mark == 0:
                fade_mark = fade_marks[0]

            elif fade_mark == 1:
                fade_mark = fade_marks[1]

        if type_input == vocal_mark:
            type_input = "вњ…" + type_input

        elif type_input == fade_mark:
            type_input = "вњ…" + type_input

        elif file_data[data] == uk_type_list[i]:
            type_input = "вњ…" + type_input

        markup.add(type_input)  # Names of buttons

    language_phrase = phrase_on_language(message, "type_keyboard")
    bot.send_message(message.chat.id, language_phrase, reply_markup=markup)


def async_slow_function(user_chat_id):
    thr = Thread(target=take_input, args=[{"message": {"chat": {"id": user_chat_id}}, "data": "continue_edit"}])
    thr.start()
    return thr


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """

    :return: get video more 20 MB on the site and save it in user dir
    """
    error = ""

    if request.method == 'POST':
        print("upload_file POST")
        print(request)
        file = request.files['files[]']
        if file and allowed_file(file.filename):
            user_chat_id = request.form.get('user_id', None)
            print("user_id_code_web", user_chat_id)

            # tmp_dir = os.getcwd()
            full_file_path = os.path.join("users_data", user_chat_id)
            file_extension = file.filename.rsplit('.', 1)[1]

            filename = user_chat_id + "." + file_extension

            try:
                file.save(os.path.join(full_file_path, filename))

            except:
                print("ERROR file did not saved")
                logging.warning("file did not saved, not such directory")
                create_users_data_dir({"chat": {"id": user_chat_id},
                                       "document": {"file_name": filename}})
                file.save(os.path.join(full_file_path, filename))

            write_in_user_file("", 1, "get_url", user_chat_id, "make_new")
            write_in_user_file("", filename, "video_name", user_chat_id)
            print("before return")
            async_slow_function(user_chat_id)

            # take_input({"message": {"chat": {"id": user_chat_id}}, "data": "continue_edit"})
            return redirect("https://t.me/harmix_bot")

        else:
            error = "Extension do not match!!! Please upload only these extensions:" \
                    " 'mp4', 'avi', 'webm', 'mkv', 'flv', 'mov', 'wmv', 'm4v', '3gp', 'ogv', 'ogg', 'vob'"

    user_id_code_web = request.args.get('user_id_code_web', "0")
    print("user_id_code_web from url", user_id_code_web)

    try:
        if db.session.query(Users.id).filter_by(user_id_code_web=user_id_code_web).scalar() is None:
            return render_template('wrong_user_id_code.html')

        else:
            user_data_db = Users.query.filter_by(user_id_code_web=user_id_code_web).first()
            print(" user_data_db.chat_id", user_data_db.chat_id)
            if user_data_db.chat_id == "0":
                special_language_upload_page = 'harmix_upload_form_{}.html'.format(user_data_db.language)

                return render_template(special_language_upload_page, user_id=user_data_db.chat_id, error=error)

            if user_data_db.subscription_term != "0":
                y1, m1, d1 = [int(x) for x in user_data_db.subscription_term.split('-')]
                subscription_end_day = date(y1, m1, d1)
                my = date.today()
                print("today in app", subscription_end_day)
                if subscription_end_day >= date.today():
                    renovate_id_code_db(user_data_db.chat_id)
                    special_language_upload_page = 'harmix_upload_form_{}.html'.format(user_data_db.language)

                    return render_template(special_language_upload_page, user_id=user_data_db.chat_id, error=error)
    except:
        print("db ERROR in upload_file")
    return render_template('wrong_user_id_code.html')


@app.route("/" + API_TOKEN, methods=["POST"])
def get_message():
    print("get")
    bot.process_new_updates(
        [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))]
    )
    return "!", 200


if __name__ == "__main__":
    add_logs()
    app.run()
    # bot.polling()
