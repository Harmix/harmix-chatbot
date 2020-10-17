import json
import os

from additional_functions_dir.create_user_data_dir import create_users_data_dir
from harmix_db.main_db_functions import update_sql
from survey import get_survey_button


def update_n_videos_last_upload(message, user_chat_id):
    try:
        print("\n update_n_videos_last_upload function ------------------------------------")

        # create user_dir if it is not in the users_data dir
        if user_chat_id not in os.listdir("users_data") or user_chat_id + "_data.json" \
                not in os.listdir(os.path.join('users_data', user_chat_id)):
            create_users_data_dir(message)
            print("update_n_videos_last_upload ERROR")

        full_file_path = os.path.join(os.getcwd(), 'users_data', user_chat_id, user_chat_id)
        with open(full_file_path + "_data" + ".json", "r", encoding='utf-8') as f:
            file_user_data = json.load(f)
            file_user_data["n_videos"] = file_user_data.get("n_videos", 0) + 1
            file_user_data["n_surveys"] = file_user_data.get("n_surveys", 0)

            # data in users_data table
            update_sql('users_data', 'n_videos', user_chat_id, file_user_data["n_videos"])
            update_sql('users_data', 'last_upload', user_chat_id, file_user_data["last_upload"])
            try:
                print("n_surveys n_videos", file_user_data["n_surveys"], file_user_data["n_videos"])
                # after 3 and 23 video each user should give a feedback.
                # if not - send the survey each 10th video untill he will not give a feedback
                if file_user_data["n_videos"] == 3:
                    get_survey_button(message)

                elif file_user_data["n_videos"] == 23:
                    get_survey_button(message)

                elif file_user_data["n_surveys"] == 0 and \
                        file_user_data["n_videos"] % 10 == 0:
                    get_survey_button(message)

                elif file_user_data["n_surveys"] == 1 and file_user_data["n_videos"] >= 8 and \
                        file_user_data["n_videos"] % 10 == 0:
                    get_survey_button(message)

            except:
                print("get_survey_button(message) ERROR")

        with open(full_file_path + "_data" + ".json", "w") as f:
            json.dump(file_user_data, f, ensure_ascii=False, indent=4)
    except:
        print("update_n_videos_last_upload ERROR - no such file")
