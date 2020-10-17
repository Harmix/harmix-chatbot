from additional_functions_dir.id_code import generate_id_code
from harmix_db.main_db_functions import update_sql


def renovate_buy_user_id_web(user_chat_id):
    # data in users_data table
    buy_user_id_web = generate_id_code(user_chat_id)
    update_sql('users_data', 'buy_user_id_web', user_chat_id, buy_user_id_web)

    return buy_user_id_web
