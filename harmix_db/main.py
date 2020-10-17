#!/usr/bin/python
from datetime import datetime
import json
import os

import psycopg2
from harmix_db import config


def get_parts(retrieve_parameters, title_table):
    """ query parts from the parts table """
    conn = None
    try:
        params = config.config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT {} FROM {}".format(', '.join(retrieve_parameters), title_table))
        rows = cur.fetchall()
        rows_copy = []
        for row in rows:
            rows_copy.append(row)

        cur.close()
        return rows_copy
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def create_tables():
    """ create tables in the PostgreSQL database"""
    conn = None
    try:
        # read the connection parameters
        params = config.config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def insert_sql(table_name, answers):
    """ insert a new vendor into the vendors table """
    n_values = ['%s'] * len(answers)
    n_values = ', '.join(map(str, n_values))

    name_columns = ''

    sql = """INSERT INTO {0} ({1}) 
            VALUES ({2})""".format(table_name, name_columns, n_values)
    conn = None
    try:
        # read database configuration
        params = config.config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, answers)
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def update_sql(name_table, name_parameter, chat_id, parameter):
    """ update vendor name based on the vendor id """
    print("update")
    sql = """ UPDATE {}
                SET {} = %s
                WHERE chat_id = %s""".format(name_table, name_parameter)
    conn = None
    updated_rows = 0
    try:
        # read database configuration
        params = config.config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the UPDATE  statement
        cur.execute(sql, (str(parameter), chat_id))
        # get the number of updated rows
        updated_rows = cur.rowcount
        # Commit the changes to the database
        conn.commit()
        # Close communication with the PostgreSQL database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return updated_rows


def start_collect_user_data(message, chat_id):
    try:
        user_chat_id = str(message.chat.id)
    except:
        user_chat_id = str(message.message.chat.id)

    if user_chat_id in os.listdir(os.path.join(os.getcwd(), 'users_data')):
        full_file_path = os.path.join(os.getcwd(), 'users_data', user_chat_id, user_chat_id)
        with open(full_file_path + "_data" + ".json", "r", encoding='utf-8') as f:
            file_user_data = json.load(f)
            insert_sql('users_data', [chat_id, file_user_data['language'],
                                      file_user_data['n_videos'], file_user_data['last_upload'],
                                      file_user_data['last_upload_on_web']])

    else:
        insert_sql('users_data', [chat_id, "uk", 0, datetime.today().strftime('%Y-%m-%d-%H:%M:%S'), "0"])


def if_user_in_db(message, chat_id):
    users_inf = get_parts(['chat_id'], 'users_data')
    flag_in_db = 0
    # search chat_id in database
    for user_data in users_inf:
        if user_data[0] == chat_id:
            flag_in_db = 1
            break

    if flag_in_db == 0:
        start_collect_user_data(message, chat_id)
