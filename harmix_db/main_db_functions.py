from datetime import datetime
import json
import os

from additional_functions_dir.get_chat_id import create_chat_id_for_db
from additional_functions_dir.id_code import generate_id_code
from harmix_db.main_db import db
from harmix_db.models import Users, Survey


def write_in_user_data_db(answers):
    insert_param = Users(answers)

    db.session.add(insert_param)
    db.session.commit()
    db.session.close()


def write_in_survey_answers_db(answers):
    insert_param = Survey(answers)

    db.session.add(insert_param)
    db.session.commit()
    db.session.close()


def insert_sql(table_name, answers):
    """ insert a new vendor into the vendors table """
    print("insert")
    if db.session.query(Users.id).filter_by(chat_id=answers["chat_id"]).scalar() is None:
        if table_name == 'users_data':
            try:
                write_in_user_data_db(answers)

            except:
                print("rollback in insert_sql")
                db.session.rollback()
                write_in_user_data_db(answers)

    elif db.session.query(Survey.id).filter_by(chat_id=answers["chat_id"]).scalar() is None:
        if table_name == 'answers_on_survey':
            try:
                write_in_survey_answers_db(answers)

            except:
                print("rollback in insert_sql")
                db.session.rollback()
                write_in_survey_answers_db(answers)



def insert_new_survey_answer(user_chat_id, n_survey, chat_id):
    if db.session.query(Survey.id).filter_by(chat_id=user_chat_id + "_survey_" + str(
            n_survey + 1)).scalar() is None:
        insert_param = Survey(chat_id=chat_id + "_survey_" + str(n_survey + 1),
                                      chat_id=user_chat_id + "_survey_" + str(
                                          n_survey + 1))
        db.session.add(insert_param)
        db.session.commit()
        db.session.close()


def insert_first_survey(user_chat_id, chat_id):
    if db.session.query(Survey.id).filter_by(chat_id=user_chat_id).scalar() is None:
        insert_param = Survey(chat_id=chat_id,
                                      chat_id=user_chat_id)

        db.session.add(insert_param)
        db.session.commit()
        db.session.close()


def update_sql(name_table, name_parameter, user_chat_id, parameter):
    """ update vendor name based on the vendor id """
    print("\nupdate, parameter", parameter)
    if name_table == "users_data":
        try:
            Users.query.filter_by(chat_id=user_chat_id) \
                .update({name_parameter: parameter})
        except:
            print("rollback in update_sql")
            db.session.rollback()
            Users.query.filter_by(chat_id=user_chat_id) \
                .update({name_parameter: parameter})

    elif name_table == "answers_on_survey":
        try:
            Survey.query.filter_by(chat_id=user_chat_id) \
                .update({name_parameter: parameter})
        except:
            print("rollback in update_sql")
            db.session.rollback()
            Survey.query.filter_by(chat_id=user_chat_id) \
                .update({name_parameter: parameter})

    db.session.commit()
    db.session.close()


def if_user_in_db(message, user_chat_id, chat_id=""):
    try:
        if db.session.query(Users.id).filter_by(chat_id=user_chat_id).scalar() is None:
            if chat_id == "":
                chat_id = create_chat_id_for_db(message)

            start_collect_user_data(message, chat_id)
    except:
        db.session.rollback()
        raise
    finally:
        db.session.close()
