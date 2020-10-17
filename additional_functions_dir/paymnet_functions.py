from datetime import date

from harmix_db.main_db_functions import if_user_in_db
from harmix_db.models import Users


def check_subscription(user_chat_id):
    user_data_db = Users.query.filter_by(chat_id=user_chat_id).first()

    if user_data_db.subscription_term != "0":
        try:
            y1, m1, d1 = [int(x) for x in user_data_db.subscription_term.split('-')]
            subscription_end_day = date(y1, m1, d1)
            my = date.today()
            print("today", subscription_end_day)
            print(subscription_end_day >= my)

            if subscription_end_day >= date.today():
                return True

        except:
            print("check_subscription [int(x) for x in user_data_db.subscription_term.split('-')] ERROR")

    return False
