from harmix_db.main_db import db
from harmix_db.models import Users


if __name__ == '__main__':
    # User is the name of table that has a column name
    users = Users.query.all()
    video_size_button = 0

    for user in users:
        # if user.username == "Service Helper Harmix":
        if user.n_surveys is None or user.n_surveys == "":
            print("user.username", user.username)
            # web_order_id = "{}_order_id_0".format(user.chat_id)
            Users.query.filter_by(chat_id=user.chat_id) \
                .update({"n_surveys": video_size_button})

            db.session.commit()
        #
        # if user.n_answered_question is None or user.n_answered_question == "" or user.n_answered_question == 1:
        #     print("user.username", user.username)
        #     # web_order_id = "{}_order_id_0".format(user.chat_id)
        #     Users.query.filter_by(chat_id=user.chat_id) \
        #         .update({"n_answered_question": video_size_button})
        #
        #     db.session.commit()
        #
        # if user.get_url is None or user.get_url == "" or user.get_url == 1:
        #     print("user.username", user.username)
        #     # web_order_id = "{}_order_id_0".format(user.chat_id)
        #     Users.query.filter_by(chat_id=user.chat_id) \
        #         .update({"get_url": video_size_button})
        #
        #     db.session.commit()
