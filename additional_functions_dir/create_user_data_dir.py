import os
from datetime import datetime

import json

from harmix_db.main_db import db
from harmix_db.models import Users


def create_users_data_dir(message, extension="mp4"):
    flag_in_db = 0
    if isinstance(message, dict):
        user_chat_id = message["chat"]["id"]
    else:
        try:
            try:
                user_chat_id = str(message.chat.id)
            except:
                user_chat_id = str(message.from_user.id)
        except:
            user_chat_id = message
    try:
        # update data in answers_on_survey table SQL
        user_data_from_db = ""
        if db.session.query(Users.id).filter_by(chat_id=user_chat_id).scalar() is not None:
            user_data_from_db = Users.query.filter_by(chat_id=user_chat_id).first()
            flag_in_db = 1

    except:
        print("create_users_data_dir error - db.session.query(Users.id)."
              "filter_by(chat_id=user_chat_id).scalar() is not None")

    path = "users_data/{}".format(user_chat_id)

    try:
        os.mkdir(path)
    except OSError:
        print("Creation of the directory %s failed or this directory exists" % path)
    else:
        print("Successfully created the directory %s " % path)

    try:
        if isinstance(message, dict):
            start_position_extension = message["document"]["file_name"].rfind('.')
            file_extension = message["document"]["file_name"][start_position_extension + 1:]
        else:
            start_position_extension = str(message.document.file_name).rfind('.')
            file_extension = str(message.document.file_name)[start_position_extension + 1:]
    except:
        file_extension = extension

    print("user_chat_id, file_extension", user_chat_id, file_extension)
    user_data = json.loads("{}")
    user_data["video_name"] = user_chat_id + "." + file_extension
    user_data['last_upload'] = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')

    if flag_in_db == 0:
        user_data['n_videos'] = 0
        user_data['language'] = "uk"
        user_data['n_surveys'] = 0

    else:
        try:
            user_data['language'] = user_data_from_db.language
            user_data['n_videos'] = user_data_from_db.n_videos
            user_data['last_function_before_pay'] = user_data_from_db.last_function_before_pay
            user_data['last_message_before_pay'] = user_data_from_db.last_message_before_pay

            if user_data_from_db.n_surveys is not None:
                user_data['n_surveys'] = int(user_data_from_db.n_surveys)
            else:
                user_data['n_surveys'] = 0
        except:
            user_data['n_videos'] = 0
            user_data['language'] = "uk"
            user_data['n_surveys'] = 0

    # trying to change directory and download a video to user's dir
    full_file_path = os.path.join(os.getcwd(), 'users_data', user_chat_id, user_chat_id)
    try:
        with open(full_file_path + "_data" + ".json", "w", encoding="utf-8") as f:
            json.dump(user_data, f, indent=4)
    except:
        # mkdir for special user
        path = os.path.join('users_data', user_chat_id)
        try:
            os.mkdir(path)
        except OSError:
            print("Creation of the directory %s failed or this directory exists" % path)
        else:
            print("Successfully created the directory %s " % path)

        with open(full_file_path + "_data" + ".json", "w", encoding="utf-8") as f:
            json.dump(user_data, f, indent=4)
