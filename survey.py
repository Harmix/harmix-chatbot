import json
import logging
import os

import telebot


from additional_functions_dir.create_user_data_dir import create_users_data_dir
from harmix_db.main_db_functions import update_sql
from harmix_db.models import Survey
from language_functions import phrase_on_language
from config_api import API_TOKEN

bot = telebot.TeleBot(API_TOKEN)


def get_survey_button(message):
    try:
        language_phrase = phrase_on_language(message, "survey_buttons")
    except:
        create_users_data_dir(message)
        language_phrase = phrase_on_language(message, "survey_buttons")

    keyboard = telebot.types.InlineKeyboardMarkup()

    keyboard.row(
        telebot.types.InlineKeyboardButton(language_phrase[0], callback_data='survey')
    )

    bot.send_message(message.chat.id, '📨📈📊 ' + language_phrase[1],
                     reply_markup=keyboard)


def keyboard_buttons_survey(message, question):
    try:
        language_answers_button = phrase_on_language(message, "answers")
        questions = phrase_on_language(message, 'questions')
    except:
        create_users_data_dir(message)
        language_answers_button = phrase_on_language(message, "answers")
        questions = phrase_on_language(message, 'questions')

    n_question = questions.index(question)
    keyboard = telebot.types.InlineKeyboardMarkup()

    for i in range(len(language_answers_button)):
        keyboard.row(
            telebot.types.InlineKeyboardButton(language_answers_button[i],
                                               callback_data=language_answers_button[i] + str(n_question))
        )

    bot.send_message(message.chat.id, question,
                     reply_markup=keyboard)


def update_question_answer_db(user_chat_id, message, n_question, ru_answer):
    full_file_path = os.path.join(os.getcwd(), 'users_data', user_chat_id, user_chat_id)
    print(":update_question_answer_db")
    if user_chat_id not in os.listdir("users_data") or user_chat_id + "_data.json" \
            not in os.listdir(os.path.join('users_data', user_chat_id)):
        create_users_data_dir(message)
        print("get file_user_data['n_surveys'] ERROR")

    with open(full_file_path + "_data" + ".json", "r", encoding='utf-8') as f:
        file_user_data = json.load(f)
        if file_user_data['n_surveys'] >= 1:
            update_sql('answers_on_survey', 'question' + str(n_question + 1),
                       user_chat_id + "_survey_" + str(file_user_data['n_surveys'] + 1), ru_answer)
        else:
            update_sql('answers_on_survey', 'question' + str(n_question + 1),
                       user_chat_id, ru_answer)


def update_answer(answer_text, language_answers, ru_answers, survey_dict, ru_question, answer,
                  full_survey_answer_path, n_question, user_chat_id):
    if answer_text in language_answers:
        ru_answer = ru_answers[language_answers.index(answer_text)]
        survey_dict[ru_question][ru_answer] += 1

        try:
            # update data in answers_on_survey table SQL
            # create_user_answers(answer, ru_answer)
            with open(full_survey_answer_path + ".json", "w", encoding='utf-8') as f:
                json.dump(survey_dict, f, ensure_ascii=False, indent=4)

        except:
            print("update_answer ERROR")

        update_question_answer_db(user_chat_id, answer.from_user, n_question, ru_answer)


def opt_answers_in_dict_from_buttons(answer, n_question):
    """

    :return: save user answer from buttons on a special question in DB
    """
    full_phrases_path = os.path.join(os.getcwd(), 'templates', 'phrases')
    language_answers = phrase_on_language(answer, 'answers')

    with open(full_phrases_path + ".json", "r", encoding="utf-8") as f:
        phrases = json.load(f)
        ru_answers = phrases['answers']['ru']
        ru_questions = phrases['questions']['ru']

    ru_question = ru_questions[n_question]

    answer_text = ''
    try:
        answer_text = answer.data
    except:
        pass

    answer_text = answer_text[:len(answer_text) - 1]

    full_survey_answer_path = os.path.join(os.getcwd(), 'templates', 'answers_on_survey')

    try:
        user_chat_id = str(answer.from_user.id)
        if user_chat_id not in os.listdir("users_data") or user_chat_id + "_data.json" \
                not in os.listdir(os.path.join('users_data', user_chat_id)):
            create_users_data_dir(answer)
            print("opt_answers_in_dict_from_buttons ERROR")

        with open(full_survey_answer_path + ".json", "r", encoding='utf-8') as f:
            survey_dict = json.load(f)
            # username = create_username_for_db(answer)
            print("answer", answer)
            try:
                update_answer(answer_text, language_answers, ru_answers, survey_dict, ru_question, answer,
                              full_survey_answer_path, n_question, user_chat_id)

            except:
                with open(full_phrases_path + ".json", "r", encoding='utf-8') as f:
                    phrases = json.load(f)
                    language_answers = phrases['answers']['uk']

                update_answer(answer_text, language_answers, ru_answers, survey_dict, ru_question, answer,
                              full_survey_answer_path, n_question, user_chat_id)

    except:
        print('answers_in_dict_from_buttons error - if answer_text in language_answers: or'
              ' json.dump(survey_dict, f, ensure_ascii=False, indent=4)')


def opt_answers_in_dict(answer, n_question):
    """

    :return: save user answer on a special question in DB
    """
    full_phrases_path = os.path.join(os.getcwd(), 'templates', 'phrases')

    try:
        user_chat_id = str(answer.chat.id)
        if user_chat_id not in os.listdir("users_data") or user_chat_id + "_data.json" \
                not in os.listdir(os.path.join('users_data', user_chat_id)):
            create_users_data_dir(answer)
            print("opt_answers_in_dict_from_buttons ERROR")

        with open(full_phrases_path + ".json", "r", encoding="utf-8") as f:
            phrases = json.load(f)
            ru_questions = phrases['questions']['ru']

        ru_question = ru_questions[n_question]

        full_phrases_path = os.path.join(os.getcwd(), 'templates', 'answers_on_survey')
        with open(full_phrases_path + ".json", "r", encoding='utf-8') as f:
            survey_dict = json.load(f)

            # update data in answers_on_survey table SQL
            # username = create_username_for_db(answer)
            username = Survey.query.filter_by(chat_id=user_chat_id).first().username
            print("username", username)
            print(" answer", answer)

            user_answer = username + ':   ' + answer.text
            survey_dict[ru_question].append(user_answer)
            # create_user_answers(answer, answer.text)
            update_question_answer_db(user_chat_id, answer.from_user, n_question, answer.text)
            # update_sql('answers_on_survey', 'question' + str(n_question + 1), user_chat_id, answer.text)

        with open(full_phrases_path + ".json", "w", encoding='utf-8') as f:
            json.dump(survey_dict, f, ensure_ascii=False, indent=4)

    except:
        print('answers_in_dict error - ru_questions = phrases[\'questions\'][\'ru\']'
              ' or update_sql(\'answers_on_survey\',')


def survey_buttons(message):
    """
    :return: a button starting a survey
    """
    try:
        language_phrase = phrase_on_language(message, "survey_buttons")
    except:
        create_users_data_dir(message)
        language_phrase = phrase_on_language(message, "survey_buttons")

    keyboard = telebot.types.InlineKeyboardMarkup()

    keyboard.row(
        telebot.types.InlineKeyboardButton(language_phrase[0], callback_data='survey')
    )

    bot.send_message(message.chat.id, language_phrase[1],
                     reply_markup=keyboard)
