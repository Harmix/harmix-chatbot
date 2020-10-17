from additional_functions_dir.id_code import generate_id_code
from harmix_db.main_db_functions import update_sql


def renovate_id_code_db(user_chat_id):
    # data in users_data table
    user_id_code_web = generate_id_code(user_chat_id)
    update_sql('users_data', 'user_id_code_web', user_chat_id, user_id_code_web)

    return user_id_code_web
