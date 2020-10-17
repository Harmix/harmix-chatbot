import json
import os
from pathlib import Path

from harmix_db import main


def create_users_data_dir(username, user_chat_id):
    users_inf = main.get_parts(['username', 'language', 'n_videos'], 'users_data')
    flag_in_db = 0
    user_insert_data_in_json = []
    if users_inf:
        # check username in database
        for user_data in users_inf:
            if user_data[0] == username:
                user_insert_data_in_json.append(user_data[1])
                user_insert_data_in_json.append(user_data[2])
                flag_in_db = 1
                break

    tmp_dir = os.getcwd()
    full_file_path = os.path.join(tmp_dir, 'users_data', user_chat_id)

    # mkdir for special user
    os.chdir(os.path.join(tmp_dir, "users_data"))
    user_directory = Path(full_file_path)
    user_directory.mkdir(exist_ok=True)
    os.chdir("..")

    user_data = dict()

    if flag_in_db == 0:

        string = '{"language": "' + 'uk' + '"}'
        user_data = json.loads(string)
        user_data["n_videos"] = 0

    else:
        user_data['language'] = user_insert_data_in_json[0]
        user_data['n_videos'] = user_insert_data_in_json[1]

    # trying to change directory and download a video to user's dir
    full_file_path = os.path.join(os.getcwd(), 'users_data', user_chat_id)
    with open(full_file_path + user_chat_id + "_data" + ".json", "w", encoding="utf-8") as f:
        json.dump(user_data, f)