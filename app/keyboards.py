from aiogram.types import InlineKeyboardButton, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database.requests import get_all_topics, get_questions, get_users, get_answer, get_all_topics, get_questions, get_users, get_answers, get_categories, get_qualities, get_topics_for_user, get_topics_by_creator
from app.database.models import User, Role

QUESTION_TYPE_SCALE = 'scale'
YES_NO_CALLBACK = 'yes_no_choice'
QUESTION_TYPE_CALLBACK = 'q_type_choice'
NEXT_QUESTION_CALLBACK = 'next_q'
FINISH_TEST_CALLBACK = 'finish_test_creation'
ADD_ANSWER_CALLBACK = 'add_ans'
FINISH_ANSWERS_CALLBACK = 'finish_ans'

async def create_callback_data(action, question_id, answer, category=None):
    return f"{action}:{question_id}:{answer}:{category}"

async def create_role_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Студент"),
                KeyboardButton(text="Преподаватель")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

async def yes_no_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Да"),
                KeyboardButton(text="Нет")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

async def question_type_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Да/Нет"),
                KeyboardButton(text="Вариантный")
            ],
            [
                KeyboardButton(text="Шкала")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

async def scale_reverse_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Прямая"),
                KeyboardButton(text="Обратная")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

async def add_or_finish_answers_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Добавить ещё ответ")
            ],
            [
                KeyboardButton(text="Закончить ввод ответов")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

async def select_category_keyboard(topic_id: int) -> InlineKeyboardBuilder:
    categories = await get_categories(topic_id)
    keyboard = InlineKeyboardBuilder()
    if categories:
        for cat in categories:
            keyboard.add(InlineKeyboardButton(text=cat.description, callback_data=f"select_cat:{cat.id}"))
    keyboard.add(InlineKeyboardButton(text="Без категории", callback_data="select_cat:None"))
    return keyboard.adjust(2).as_markup()

async def select_quality_keyboard(topic_id: int) -> InlineKeyboardBuilder:
    qualities = await get_qualities(topic_id)
    keyboard = InlineKeyboardBuilder()
    if qualities:
        for qual in qualities:
            keyboard.add(InlineKeyboardButton(text=qual.description, callback_data=f"select_qual:{qual.id}"))
    keyboard.add(InlineKeyboardButton(text="Без качества", callback_data="select_qual:None"))
    return keyboard.adjust(2).as_markup()

async def all_topics(user_data: User):
    topics = await get_topics_for_user(user_data)
    keyboard = InlineKeyboardBuilder()
    if not topics:
        return None
    for topic in topics:
        keyboard.add(InlineKeyboardButton(text=topic.topic_name, callback_data=f"topic_{topic.id}"))
    return keyboard.adjust(1).as_markup()

async def teacher_topics_keyboard(teacher_tg_id):
    topics = await get_topics_by_creator(teacher_tg_id)
    keyboard = InlineKeyboardBuilder()
    if not topics:
        return None
    for topic in topics:
        keyboard.add(InlineKeyboardButton(text=topic.topic_name, callback_data=f"manage_access_topic_{topic.id}"))
    return keyboard.adjust(1).as_markup()

async def access_type_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Группа"),
                KeyboardButton(text="Направление")
            ],
            [
                KeyboardButton(text="Кафедра"),
                KeyboardButton(text="Институт")
            ],
            [
                KeyboardButton(text="Открытый для всех")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

async def all_users():
    users = await get_users()
    keyboard = InlineKeyboardBuilder()
    for user in users:
        keyboard.add(InlineKeyboardButton(text=f'{user.name}, {user.group}', callback_data=f"user_{user.tg_id}"))
    return keyboard.adjust(1).as_markup()

async def answering(question_id, question_type):
    keyboard = InlineKeyboardBuilder()
    if question_type == 'yes_no' or question_type == 'Да/Нет':
        keyboard.add(InlineKeyboardButton(text="Да", callback_data=await create_callback_data('answer', question_id, 'Yes')))
        keyboard.add(InlineKeyboardButton(text="Нет", callback_data=await create_callback_data('answer', question_id, 'No')))
        return keyboard.adjust(2).as_markup()
    elif question_type == 'variant' or question_type == 'Вариантный':
        answers = await get_answers(question_id)
        for answer in answers:
            keyboard.add(InlineKeyboardButton(text=answer.answer_text[:2], 
                        callback_data=await create_callback_data('answer', 
                                                                 question_id, 
                                                                 answer.answer, 
                                                                 answer.category)))
        return keyboard.adjust(2).as_markup()
    elif int(question_type)>1:
        variants = int(question_type)
        for variant in range (1, variants+1): 
                keyboard.add(InlineKeyboardButton(text=str(variant), 
                    callback_data=await create_callback_data('answer', 
                                                       question_id, 
                                                       str(variant))))
    return keyboard.adjust(2).as_markup()

async def teacher_editable_topics_keyboard(teacher_tg_id: int):
    topics = await get_topics_by_creator(teacher_tg_id)
    keyboard = InlineKeyboardBuilder()
    if not topics:
        return None
    for topic in topics:
        keyboard.add(InlineKeyboardButton(text=topic.topic_name, callback_data=f"edit_topic_{topic.id}_{topic.topic_name}"))
    return keyboard.adjust(1).as_markup()

async def edit_question_main_options_keyboard(question_type: str) -> ReplyKeyboardMarkup:
        keyboard_rows=[
            [
                KeyboardButton(text="Редактировать текст вопроса")
            ],
            [
                KeyboardButton(text="Изменить правильный ответ")
            ]
        ]
        if question_type == 'variant' or question_type == 'Вариантный':
            keyboard_rows.append([
            KeyboardButton(text="Управление вариантами ответов")
        ])

        keyboard_rows.append([
        KeyboardButton(text="Вернуться к списку вопросов темы")
    ])
        keyboard_rows.append([
        KeyboardButton(text="Завершить редактирование")
    ])

        keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_rows,
        resize_keyboard=True,
        one_time_keyboard=True
    )
        return keyboard

async def teacher_deletable_topics_keyboard(teacher_tg_id: int):
    topics = await get_topics_by_creator(teacher_tg_id)
    keyboard = InlineKeyboardBuilder()
    if not topics:
        return None
    for topic in topics:
        keyboard.add(InlineKeyboardButton(text=topic.topic_name, callback_data=f"delete_topic_{topic.id}"))
    return keyboard.adjust(1).as_markup()

async def manage_answers_options_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Редактировать существующий")
            ],
            [
                KeyboardButton(text="Добавить новый")
            ],
            [
                KeyboardButton(text="Удалить")
            ],
            [
                KeyboardButton(text="Вернуться к опциям вопроса")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

async def edit_single_answer_options_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Изменить текст")
            ],
            [
                KeyboardButton(text="Изменить значение")
            ],
            [
                KeyboardButton(text="Изменить категорию")
            ],
            [
                KeyboardButton(text="Удалить этот вариант")
            ],
            [
                KeyboardButton(text="Вернуться к списку вариантов")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard