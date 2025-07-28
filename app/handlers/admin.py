from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Filter, Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from app.database import requests as rq
from app.database.models import Role, Answer
from app import keyboards as kb

admin = Router()

class TeacherFilter(Filter):
    async def __call__(self, message: Message):
        user = await rq.get_user(message.from_user.id)
        if user:
            return user.role == Role.TEACHER
        return False

class CreateTest(StatesGroup):
    GET_TOPIC_NAME = State()
    GET_QUESTION_COUNT = State()
    ASK_CATEGORIES = State()
    GET_CATEGORIES_NAMES = State()
    ASK_QUALITIES = State()
    GET_QUALITIES_NAMES = State()
    ASK_OVERALL_DESCRIPTION_NEEDED = State()
    GET_OVERALL_DESCRIPTION_COUNT = State()
    GET_OVERALL_DESCRIPTION_RANGE = State()
    ASK_QUALITY_DESCRIPTIONS_NEEDED = State()
    GET_QUALITY_DESCRIPTION_RANGE_COUNT = State()
    GET_QUALITY_DESCRIPTION_RANGE = State()
    FINALIZING_INITIAL_SETUP = State()
    GET_OVERALL_QUESTION_TYPE = State()
    CREATING_QUESTIONS_START = State()
    GET_QUESTION_TEXT = State()
    GET_QUESTION_TYPE = State()
    GET_QUESTION_TRUE_ANSWER = State()
    GET_QUESTION_SCALE_MAX = State()
    GET_QUESTION_IS_REVERSE = State()
    GET_QUESTION_QUALITY_LINK = State()
    GET_VARIANT_ANSWER_TEXT = State()
    GET_VARIANT_ANSWER_VALUE = State()
    GET_VARIANT_ANSWER_CATEGORY_LINK = State()
    ASK_ADD_MORE_ANSWERS = State()
    
class SetTopicAccess(StatesGroup):
    SELECT_TOPIC = State()
    SELECT_ACCESS_TYPE = State()
    GET_ACCESS_VALUE = State()
    ADD_MORE_ACCESS_RULES = State()
    
class EditTest(StatesGroup):
    SELECT_TOPIC_TO_EDIT = State()
    DISPLAY_QUESTIONS_FOR_EDIT = State()
    SELECT_QUESTION_TO_EDIT = State()
    SELECT_EDIT_OPTION = State()
    GET_NEW_QUESTION_TEXT = State()
    GET_NEW_TRUE_ANSWER = State()
    MANAGE_ANSWERS_MENU = State()
    SELECT_ANSWER_TO_MODIFY = State()
    SELECT_MODIFY_ANSWER_OPTION = State()
    GET_NEW_ANSWER_TEXT = State()
    GET_NEW_ANSWER_VALUE = State()
    GET_NEW_ANSWER_CATEGORY_NAME = State()
    ADD_NEW_ANSWER_DETAILS = State()
    CONFIRM_DELETE_ANSWER = State()

class DeleteTest(StatesGroup):
    SELECT_TOPIC_TO_DELETE = State()
    CONFIRM_DELETE = State()

@admin.message(TeacherFilter(), Command("create_test"))
async def start_create_test(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Введите название темы:")
    await state.set_state(CreateTest.GET_TOPIC_NAME)

@admin.message(CreateTest.GET_TOPIC_NAME)
async def get_topic_name(message: Message, state: FSMContext):
    await state.update_data(topic_name=message.text)
    await message.answer("Введите количество вопросов в тесте:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(CreateTest.GET_QUESTION_COUNT)

@admin.message(CreateTest.GET_QUESTION_COUNT)
async def get_question_count(message: Message, state: FSMContext):
    try:
        question_count = int(message.text)
        if question_count <= 0:
            await message.answer("Количество вопросов должно быть положительным числом.")
            return

        await state.update_data(question_count=question_count, current_question_num=1)
        await message.answer("Будут ли ответы иметь категории (например: зависимые, компетентные, агрессивные)?",
                             reply_markup=await kb.yes_no_keyboard())
        await state.set_state(CreateTest.ASK_CATEGORIES)
    except ValueError:
        await message.answer("Пожалуйста, введите целое число.")
        
@admin.message(CreateTest.ASK_CATEGORIES, F.text.in_(['Да', 'Нет', 'да', 'нет']))
async def ask_categories(message: Message, state: FSMContext):
    if message.text == "Да":
        await state.update_data(has_categories=True, temp_category_names=[])
        await message.answer("Отправьте названия категорий через '/'. Например: 'Зависимые/Компетентные/Агрессивные'")
        await state.set_state(CreateTest.GET_CATEGORIES_NAMES)
    else:
        await state.update_data(has_categories=False)
        await message.answer("Будут ли вопросы содержать в себе качества (например: Самоорганизация, Ориентация)?",
                             reply_markup=await kb.yes_no_keyboard())
        await state.set_state(CreateTest.ASK_QUALITIES)

@admin.message(CreateTest.ASK_CATEGORIES)
async def invalid_ask_categories(message: Message):
    await message.answer("Пожалуйста, ответьте 'Да' или 'Нет'.")
    
@admin.message(CreateTest.GET_CATEGORIES_NAMES)
async def get_categories_names(message: Message, state: FSMContext):
    categories_str = message.text
    categories_list = [c.strip() for c in categories_str.split('/') if c.strip()]
    if not categories_list:
        await message.answer("Пожалуйста, введите названия категорий через '/'")
        return
    await state.update_data(temp_category_names=categories_list)
    await message.answer("Будут ли вопросы содержать в себе качества (например: Самоорганизация, Ориентация)?",
                         reply_markup=await kb.yes_no_keyboard())
    await state.set_state(CreateTest.ASK_QUALITIES)

@admin.message(CreateTest.ASK_QUALITIES, F.text.in_(['Да', 'Нет', 'да', 'нет']))
async def ask_qualities(message: Message, state: FSMContext):
    if message.text == "Да":
        await state.update_data(has_qualities=True, temp_quality_names=[])
        await message.answer("Отправьте названия качеств через '/'. Например: 'Самоорганизация/Ориентация'")
        await state.set_state(CreateTest.GET_QUALITIES_NAMES)
    else:
        await state.update_data(has_qualities=False)
        user_data = await state.get_data()
        if not user_data['has_categories']:
            await message.answer("Будет ли общее описание результата теста (без категорий и качеств)?",
                                 reply_markup=await kb.yes_no_keyboard())
            await state.set_state(CreateTest.ASK_OVERALL_DESCRIPTION_NEEDED)
        else:
            await finalize_initial_setup(message, state)

@admin.message(CreateTest.ASK_QUALITIES)
async def invalid_ask_qualities(message: Message):
    await message.answer("Пожалуйста, ответьте 'Да' или 'Нет'.")

@admin.message(CreateTest.GET_QUALITIES_NAMES)
async def get_qualities_names(message: Message, state: FSMContext):
    qualities_str = message.text
    qualities_list = [q.strip() for q in qualities_str.split('/') if q.strip()]
    if not qualities_list:
        await message.answer("Пожалуйста, введите названия качеств через '/'")
        return
    await state.update_data(temp_quality_names=qualities_list)

    user_data = await state.get_data()
    if not user_data['has_categories']:
        await message.answer("Будет ли общее описание результата теста (без категорий и качеств)?",
                             reply_markup=await kb.yes_no_keyboard())
        await state.set_state(CreateTest.ASK_OVERALL_DESCRIPTION_NEEDED)
    else:
        await message.answer("Теперь зададим описания для каждого качества.", reply_markup=ReplyKeyboardRemove())
        await state.update_data(current_quality_desc_idx=0, quality_descriptions={})
        qual_name = user_data['temp_quality_names'][0]
        await message.answer(f"Для качества '{qual_name}': Сколько диапазонов описания будет (например, 3 для 'плохо', 'средне', 'отлично')?")
        await state.set_state(CreateTest.GET_QUALITY_DESCRIPTION_RANGE_COUNT)


@admin.message(CreateTest.ASK_OVERALL_DESCRIPTION_NEEDED, F.text.in_(['Да', 'Нет', 'да', 'нет']))
async def ask_overall_description_needed(message: Message, state: FSMContext):
    user_data = await state.get_data()
    if message.text == "Да":
        await state.update_data(has_overall_description=True, current_overall_desc_idx=0, overall_descriptions=[])
        await message.answer("Сколько диапазонов описания будет (например, 3 для 'плохо', 'средне', 'отлично')?",
                             reply_markup=ReplyKeyboardRemove())
        await state.set_state(CreateTest.GET_OVERALL_DESCRIPTION_COUNT)
    else:
        await state.update_data(has_overall_description=False)
        if user_data.get('has_qualities'):
            await message.answer("Теперь зададим описания для каждого качества.", reply_markup=ReplyKeyboardRemove())
            await state.update_data(current_quality_desc_idx=0, quality_descriptions={})
            qual_name = user_data['temp_quality_names'][0]
            await message.answer(f"Для качества '{qual_name}': Сколько диапазонов описания будет (например, 3 для 'плохо', 'средне', 'отлично')?")
            await state.set_state(CreateTest.GET_QUALITY_DESCRIPTION_RANGE_COUNT)
        else:
            await finalize_initial_setup(message, state)

@admin.message(CreateTest.ASK_OVERALL_DESCRIPTION_NEEDED)
async def invalid_ask_overall_description_needed(message: Message):
    await message.answer("Пожалуйста, ответьте 'Да' или 'Нет'.")

@admin.message(CreateTest.GET_OVERALL_DESCRIPTION_COUNT)
async def get_overall_description_count(message: Message, state: FSMContext):
    try:
        count = int(message.text)
        if count <= 0:
            await message.answer("Количество диапазонов должно быть положительным числом.")
            return
        await state.update_data(overall_desc_total_count=count)
        user_data = await state.get_data()
        current_idx = user_data['current_overall_desc_idx']
        await message.answer(f"Введите диапазон {current_idx + 1} и его описание в формате 'минимальное_значение-максимальное_значение/описание'.\n"
                             "Например: '0-5/Вы плохо справились'.")
        await state.set_state(CreateTest.GET_OVERALL_DESCRIPTION_RANGE)
    except ValueError:
        await message.answer("Пожалуйста, введите целое число.")

@admin.message(CreateTest.GET_OVERALL_DESCRIPTION_RANGE)
async def get_overall_description_range(message: Message, state: FSMContext):
    try:
        parts = message.text.split('/')
        if len(parts) != 2:
            raise ValueError("Неверный формат. Используйте 'мин-макс/описание'.")
        range_str, description_text = parts[0], parts[1]
        min_max = range_str.split('-')
        if len(min_max) != 2:
            raise ValueError("Неверный формат диапазона. Используйте 'мин-макс'.")
        min_val, max_val = int(min_max[0]), int(min_max[1])
        if min_val > max_val:
            await message.answer("Минимальное значение не может быть больше максимального.")
            return

        user_data = await state.get_data()
        current_descriptions = user_data.get('overall_descriptions', [])
        current_descriptions.append({'min': min_val, 'max': max_val, 'desc': description_text})
        await state.update_data(overall_descriptions=current_descriptions)

        current_idx = user_data['current_overall_desc_idx'] + 1
        await state.update_data(current_overall_desc_idx=current_idx)

        if current_idx < user_data['overall_desc_total_count']:
            await message.answer(f"Введите диапазон {current_idx + 1} и его описание в формате 'минимальное_значение-максимальное_значение/описание'.")
        else:
            if user_data['has_qualities']:
                await message.answer("Теперь зададим описания для каждого качества.", reply_markup=ReplyKeyboardRemove())
                await state.update_data(current_quality_desc_idx=0, quality_descriptions={})
                qual_name = user_data['temp_quality_names'][0]
                await message.answer(f"Для качества '{qual_name}': Сколько диапазонов описания будет (например, 3 для 'плохо', 'средне', 'отлично')?")
                await state.set_state(CreateTest.GET_QUALITY_DESCRIPTION_RANGE_COUNT)
            else:
                await finalize_initial_setup(message, state)

    except ValueError as e:
        await message.answer(f"Ошибка формата: {e}. Пожалуйста, используйте 'минимальное_значение-максимальное_значение/описание'.")

@admin.message(CreateTest.ASK_QUALITY_DESCRIPTIONS_NEEDED, F.text.in_(['Да', 'Нет', 'да', 'нет']))
async def ask_quality_descriptions_needed(message: Message, state: FSMContext):
    if message.text == "Да":
        user_data = await state.get_data()
        await state.update_data(current_quality_desc_idx=0, quality_descriptions={})
        qual_name = user_data['temp_quality_names'][0]
        await message.answer(f"Для качества '{qual_name}': Сколько диапазонов описания будет (например, 3 для 'плохо', 'средне', 'отлично')?",
                             reply_markup=ReplyKeyboardRemove())
        await state.set_state(CreateTest.GET_QUALITY_DESCRIPTION_RANGE_COUNT)
    else:
        await finalize_initial_setup(message, state)

@admin.message(CreateTest.GET_QUALITY_DESCRIPTION_RANGE_COUNT)
async def get_quality_description_range_count(message: Message, state: FSMContext):
    try:
        count = int(message.text)
        if count <= 0:
            await message.answer("Количество диапазонов должно быть положительным числом.")
            return

        user_data = await state.get_data()
        current_qual_name = user_data['temp_quality_names'][user_data['current_quality_desc_idx']]
        await state.update_data(
            {f'quality_desc_total_count_{current_qual_name}': count,
             f'current_quality_range_idx_{current_qual_name}': 0}
        )
        await message.answer(f"Для качества '{current_qual_name}': Введите диапазон 1 и его описание в формате 'минимальное_значение-максимальное_значение/описание'.")
        await state.set_state(CreateTest.GET_QUALITY_DESCRIPTION_RANGE)
    except ValueError:
        await message.answer("Пожалуйста, введите целое число.")

@admin.message(CreateTest.GET_QUALITY_DESCRIPTION_RANGE)
async def get_quality_description_range(message: Message, state: FSMContext):
    try:
        parts = message.text.split('/')
        if len(parts) != 2:
            raise ValueError("Неверный формат. Используйте 'мин-макс/описание'.")
        range_str, description_text = parts[0], parts[1]
        min_max = range_str.split('-')
        if len(min_max) != 2:
            raise ValueError("Неверный формат диапазона. Используйте 'мин-макс'.")
        min_val, max_val = int(min_max[0]), int(min_max[1])
        if min_val > max_val:
            await message.answer("Минимальное значение не может быть больше максимального.")
            return

        user_data = await state.get_data()
        current_qual_name = user_data['temp_quality_names'][user_data['current_quality_desc_idx']]

        quality_descriptions = user_data.get('quality_descriptions', {})
        if current_qual_name not in quality_descriptions:
            quality_descriptions[current_qual_name] = []
        quality_descriptions[current_qual_name].append({'min': min_val, 'max': max_val, 'desc': description_text})
        await state.update_data(quality_descriptions=quality_descriptions)

        current_range_idx_key = f'current_quality_range_idx_{current_qual_name}'
        total_range_count_key = f'quality_desc_total_count_{current_qual_name}'

        current_range_idx = user_data[current_range_idx_key] + 1
        await state.update_data({current_range_idx_key: current_range_idx})

        if current_range_idx < user_data[total_range_count_key]:
            await message.answer(f"Для качества '{current_qual_name}': Введите диапазон {current_range_idx + 1} и его описание.")
        else:
            current_quality_idx = user_data['current_quality_desc_idx'] + 1
            await state.update_data(current_quality_desc_idx=current_quality_idx)

            if current_quality_idx < len(user_data['temp_quality_names']):
                next_qual_name = user_data['temp_quality_names'][current_quality_idx]
                await message.answer(f"Для качества '{next_qual_name}': Сколько диапазонов описания будет?",
                                     reply_markup=ReplyKeyboardRemove())
                await state.set_state(CreateTest.GET_QUALITY_DESCRIPTION_RANGE_COUNT)
            else:
                await finalize_initial_setup(message, state)

    except ValueError as e:
        await message.answer(f"Ошибка формата: {e}. Пожалуйста, используйте 'минимальное_значение-максимальное_значение/описание'.")

async def finalize_initial_setup(message: Message, state: FSMContext):
    user_data = await state.get_data() 
    topic = await rq.add_topic(user_data['topic_name'],
                               user_data['question_count'],
                               message.from_user.id)
    await state.update_data(topic_id=topic.id)

    category_map = {}
    if user_data.get('has_categories'):
        for cat_name in user_data['temp_category_names']:
            category = await rq.add_category(topic.id, cat_name)
            category_map[cat_name] = category.id
    await state.update_data(category_map=category_map)

    quality_map = {}
    if user_data.get('has_qualities'):
        for qual_name in user_data['temp_quality_names']:
            quality = await rq.add_quality(topic.id, qual_name)
            quality_map[qual_name] = quality.id
    await state.update_data(quality_map=quality_map)

    if user_data.get('has_overall_description'):
        for desc in user_data['overall_descriptions']:
            await rq.add_description_range(topic.id, desc['min'], desc['max'], desc['desc'])

    if user_data.get('has_qualities') and user_data.get('quality_descriptions'):
        for qual_name, descriptions in user_data['quality_descriptions'].items():
            quality_id = quality_map.get(qual_name)
            if quality_id:
                for desc in descriptions:
                    await rq.add_quality_description_range(topic.id, quality_id, desc['min'], desc['max'], desc['desc'])

    await message.answer(f"Тема '{topic.topic_name}' успешно создана. Теперь укажите, какого типа будут ВСЕ вопросы в этом тесте:",
                         reply_markup= await kb.question_type_keyboard())
    await state.set_state(CreateTest.GET_OVERALL_QUESTION_TYPE)

async def create_next_question(message: Message, state: FSMContext):
    user_data = await state.get_data()
    current_question_num = user_data['current_question_num']
    total_questions = user_data['question_count']

    if current_question_num > total_questions:
        await message.answer("Все вопросы успешно созданы! Создание теста завершено.", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return

    await state.update_data(current_question_data={}, current_answers_data=[])
    await message.answer(f"Создание вопроса {current_question_num}/{total_questions}.\nВведите текст вопроса:")
    await state.set_state(CreateTest.GET_QUESTION_TEXT)

@admin.message(CreateTest.GET_OVERALL_QUESTION_TYPE, F.text.in_(['Да/Нет', 'Вариантный', 'Шкала']))
async def get_overall_question_type(message: Message, state: FSMContext):
    overall_q_type = message.text
    await state.update_data(overall_question_type=overall_q_type)
    await message.answer(f"Вы выбрали '{overall_q_type}' для ВСЕХ вопросов. Верно?", reply_markup=await kb.yes_no_keyboard())
    await state.set_state(CreateTest.CREATING_QUESTIONS_START)
    
@admin.message(CreateTest.GET_OVERALL_QUESTION_TYPE)
async def invalid_overall_question_type(message: Message):
    await message.answer("Пожалуйста, выберите тип вопроса из предложенных вариантов: 'Да/Нет', 'Вариантный' или 'Шкала'.")

@admin.message(CreateTest.CREATING_QUESTIONS_START, F.text.in_(['Да', 'Нет', 'да', 'нет']))
async def confirm_and_start_questions(message: Message, state: FSMContext):
    if message.text == "Да" or message.text == "Да":
        await message.answer("Отлично! Приступаем к созданию вопросов.", reply_markup=ReplyKeyboardRemove())
        await create_next_question(message, state)
    else:
        await message.answer("Пожалуйста, выберите тип вопросов заново:", reply_markup=await kb.question_type_keyboard())
        await state.set_state(CreateTest.GET_OVERALL_QUESTION_TYPE)

@admin.message(CreateTest.CREATING_QUESTIONS_START)
async def invalid_confirm_and_start_questions(message: Message):
    await message.answer("Пожалуйста, ответьте 'Да' или 'Нет' для подтверждения типа вопросов.")

@admin.message(CreateTest.GET_QUESTION_TEXT)
async def get_question_text(message: Message, state: FSMContext):
    await state.update_data(current_question_data={'text': message.text})
    
    user_data = await state.get_data()
    overall_q_type = user_data['overall_question_type']
    
    current_q_data = user_data.get('current_question_data', {})
    current_q_data['type'] = overall_q_type
    await state.update_data(current_question_data=current_q_data)

    if overall_q_type == "Да/Нет":
        await message.answer("Введите правильный ответ ('Да' или 'Нет'):", reply_markup=ReplyKeyboardRemove())
        await state.set_state(CreateTest.GET_QUESTION_TRUE_ANSWER)
    elif overall_q_type == "Вариантный":
        await message.answer("Введите первый вариант ответа. Формат: 'a)текст_ответа/значение_ответа'.\n"
                             "Пример: 'a)Лев Толстой/A'\n"
                             "Если у вас включены категории, добавьте категорию: 'b)текст_ответа/значение_ответа/Название_категории'.\n"
                             "Пример: 'b)Я хороший/A/Компетентные'", reply_markup=ReplyKeyboardRemove())
        await state.set_state(CreateTest.GET_VARIANT_ANSWER_TEXT)
    elif overall_q_type == "Шкала":
        await message.answer("Введите максимальное значение шкалы (например, '5' для шкалы от 1 до 5):", reply_markup=ReplyKeyboardRemove())
        await state.set_state(CreateTest.GET_QUESTION_SCALE_MAX)

@admin.message(CreateTest.GET_QUESTION_TRUE_ANSWER)
async def get_question_true_answer(message: Message, state: FSMContext):
    true_answer = message.text.strip()
    if true_answer not in ['Да', 'Нет', 'Yes', 'No', 'a', 'b', 'c', 'd', 'e', '-']:
        await message.answer("Пожалуйста, введите 'Да', 'Нет', 'Yes', 'No', 'a', 'b', 'c', 'd', 'e' или '-' (если нет правильного ответа).")
        return

    current_q_data = (await state.get_data()).get('current_question_data', {})
    current_q_data['true'] = true_answer
    await state.update_data(current_question_data=current_q_data)

    user_data = await state.get_data()
    if user_data.get('has_qualities'):
        await message.answer("Выберите качество, к которому относится этот вопрос:", reply_markup=await kb.select_quality_keyboard(user_data['topic_id']))
        await state.set_state(CreateTest.GET_QUESTION_QUALITY_LINK)
    else:
        await save_current_question(message, state)

@admin.message(CreateTest.GET_QUESTION_SCALE_MAX)
async def get_question_scale_max(message: Message, state: FSMContext):
    try:
        scale_max = int(message.text)
        if scale_max <= 1:
            await message.answer("Максимальное значение шкалы должно быть больше 1.")
            return

        current_q_data = (await state.get_data()).get('current_question_data', {})
        current_q_data['type'] = str(scale_max)
        await state.update_data(current_question_data=current_q_data)

        await message.answer("Шкала прямая или обратная? (Прямая: чем выше значение, тем лучше; Обратная: чем выше значение, тем хуже)",
                             reply_markup=await kb.scale_reverse_keyboard())
        await state.set_state(CreateTest.GET_QUESTION_IS_REVERSE)
    except ValueError:
        await message.answer("Пожалуйста, введите целое число.")

@admin.message(CreateTest.GET_QUESTION_IS_REVERSE, F.text.in_(['Прямая', 'Обратная']))
async def get_question_is_reverse(message: Message, state: FSMContext):
    is_reverse = True if message.text == "Обратная" else False
    current_q_data = (await state.get_data()).get('current_question_data', {})
    current_q_data['is_reverse'] = is_reverse
    await state.update_data(current_question_data=current_q_data)

    user_data = await state.get_data()
    if user_data.get('has_qualities'):
        await message.answer("Выберите качество, к которому относится этот вопрос:", reply_markup=await kb.select_quality_keyboard(user_data['topic_id']))
        await state.set_state(CreateTest.GET_QUESTION_QUALITY_LINK)
    else:
        await save_current_question(message, state)

@admin.message(CreateTest.GET_QUESTION_IS_REVERSE)
async def invalid_get_question_is_reverse(message: Message):
    await message.answer("Пожалуйста, выберите 'Прямая' или 'Обратная'.")

@admin.message(CreateTest.GET_VARIANT_ANSWER_TEXT)
async def get_variant_answer_text(message: Message, state: FSMContext):
    user_data = await state.get_data()
    parts = message.text.split('/')
    answer_text = parts[0].strip()
    answer_value = parts[1].strip() if len(parts) > 1 else None
    category_name = parts[2].strip() if len(parts) > 2 else None

    if not answer_text or not answer_value:
        await message.answer("Неверный формат. Пожалуйста, используйте a)'текст_ответа/значение_ответа'.")
        return

    current_answers = user_data.get('current_answers_data', [])
    answer_data = {'text': answer_text, 'value': answer_value}

    if user_data.get('has_categories'):
        if category_name:
            category_id = user_data['category_map'].get(category_name)
            if not category_id:
                await message.answer(f"Категория '{category_name}' не найдена. Пожалуйста, используйте существующую категорию или проверьте ввод.")
                return
            answer_data['category_id'] = category_id
        else:
            await message.answer("Вы указали, что ответы имеют категории, но не указали категорию для этого ответа. Формат: a)'текст_ответа/значение_ответа/Название_категории'")
            return
    else:
        answer_data['category_id'] = None

    current_answers.append(answer_data)
    await state.update_data(current_answers_data=current_answers)

    await message.answer("Ответ добавлен. Хотите добавить ещё?", reply_markup=await kb.add_or_finish_answers_keyboard())
    await state.set_state(CreateTest.ASK_ADD_MORE_ANSWERS)

@admin.message(CreateTest.ASK_ADD_MORE_ANSWERS, F.text.in_(['Добавить ещё ответ', 'Закончить ввод ответов']))
async def ask_add_more_answers(message: Message, state: FSMContext):
    if message.text == "Добавить ещё ответ":
        await message.answer("Введите следующий вариант ответа. Формат: a)'текст_ответа/значение_ответа/Название_категории' (если применимо).",
                             reply_markup=ReplyKeyboardRemove())
        await state.set_state(CreateTest.GET_VARIANT_ANSWER_TEXT)
    else:
        user_data = await state.get_data()
        if not user_data.get('current_answers_data'):
            await message.answer("Вы должны добавить хотя бы один вариант ответа. Пожалуйста, добавьте.")
            await state.set_state(CreateTest.GET_VARIANT_ANSWER_TEXT)
            return

        await message.answer("Теперь введите правильный ответ из введенных вариантов (например, 'a' или 'b').\n"
                             "Если правильного ответа нет (например, это опрос), отправьте '-'.", reply_markup=ReplyKeyboardRemove())
        await state.set_state(CreateTest.GET_QUESTION_TRUE_ANSWER)

@admin.message(CreateTest.ASK_ADD_MORE_ANSWERS)
async def invalid_ask_add_more_answers(message: Message):
    await message.answer("Пожалуйста, выберите 'Добавить ещё ответ' или 'Закончить ввод ответов'.")

@admin.callback_query(CreateTest.GET_QUESTION_QUALITY_LINK, F.data.startswith('select_qual:'))
async def get_question_quality_link(callback: CallbackQuery, state: FSMContext):
    quality_id_str = callback.data.split(':')[1]
    quality_id = int(quality_id_str) if quality_id_str != 'None' else None

    current_q_data = (await state.get_data()).get('current_question_data', {})
    current_q_data['quality_id'] = quality_id
    await state.update_data(current_question_data=current_q_data)

    await callback.message.edit_text("Качество выбрано.")
    await save_current_question(callback.message, state)
    await callback.answer()

async def save_current_question(message: Message, state: FSMContext):
    user_data = await state.get_data()
    q_data = user_data['current_question_data']
    topic_id = user_data['topic_id']

    if q_data['type'] == 'Вариантный' and 'true' not in q_data:
        await message.answer("Ошибка: для вариантного вопроса не указан правильный ответ.")
        return

    question = await rq.add_question(
        topic_id=topic_id,
        text=q_data['text'],
        q_type=q_data['type'],
        true_answer=q_data.get('true') if q_data.get('true') != '-' else None,
        is_reverse=q_data.get('is_reverse', False),
        quality_id=q_data.get('quality_id')
    )

    if q_data['type'] == 'Вариантный':
        for ans_data in user_data['current_answers_data']:
            await rq.add_answer(
                question_id=question.id,
                answer_text=ans_data['text'],
                answer_value=ans_data['value'],
                category_id=ans_data.get('category_id')
            )

    await message.answer("Вопрос и ответы сохранены.")
    current_question_num = user_data['current_question_num'] + 1
    await state.update_data(current_question_num=current_question_num)

    await create_next_question(message, state)
    
@admin.message(TeacherFilter(), Command("manage_access"))
async def manage_access_start(message: Message, state: FSMContext):
    await state.clear()
    topics = await rq.get_topics_by_creator(message.from_user.id)
    if not topics:
        await message.answer("У вас пока нет созданных тестов.")
        return
    await message.answer("Выберите тест, для которого хотите настроить доступ:",
                         reply_markup=await kb.teacher_topics_keyboard(message.from_user.id))
    await state.set_state(SetTopicAccess.SELECT_TOPIC)

@admin.callback_query(SetTopicAccess.SELECT_TOPIC, F.data.startswith('manage_access_topic_'))
async def select_access_topic(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает выбор темы для настройки доступа."""
    topic_id = int(callback.data.split('_')[3])
    await state.update_data(managing_topic_id=topic_id)
    
    await callback.message.edit_text(f"Тема выбрана: {topic_id}. Теперь выберите тип доступа:")
    
    await callback.message.answer("Выберите тип доступа, который вы хотите добавить для этого теста:",
                                  reply_markup=await kb.access_type_keyboard())
    
    await state.set_state(SetTopicAccess.SELECT_ACCESS_TYPE)
    await callback.answer() 

@admin.message(SetTopicAccess.SELECT_ACCESS_TYPE, F.text.in_(['Группа', 'Направление', 'Кафедра', 'Институт', 'Открытый для всех']))
async def select_access_type(message: Message, state: FSMContext):
    access_type_map = {
        "Группа": "group",
        "Направление": "stream",
        "Кафедра": "department",
        "Институт": "institute",
        "Открытый для всех": "open_to_all"
    }
    selected_type = access_type_map[message.text]
    await state.update_data(current_access_type=selected_type)

    if selected_type == 'open_to_all':
        user_data = await state.get_data()
        topic_id = user_data['managing_topic_id']
        await rq.add_topic_access(topic_id, 'open_to_all', 'true')
        await message.answer("Тест теперь открыт для всех.", reply_markup=ReplyKeyboardRemove())
        await message.answer("Хотите добавить ещё правила доступа для этого теста?", reply_markup=await kb.yes_no_keyboard())
        await state.set_state(SetTopicAccess.ADD_MORE_ACCESS_RULES)
    else:
        await message.answer(f"Введите значение для '{message.text}' (например, '605-01z' для группы, 'Управление в технических системах' для направления, 'Автоматики и компьютерных систем' для кафедры, 'Политехнический институт' для института):",
                             reply_markup=ReplyKeyboardRemove())
        await state.set_state(SetTopicAccess.GET_ACCESS_VALUE)

@admin.message(SetTopicAccess.SELECT_ACCESS_TYPE)
async def invalid_select_access_type(message: Message):
    await message.answer("Пожалуйста, выберите тип доступа из предложенных кнопок.")

@admin.message(SetTopicAccess.GET_ACCESS_VALUE)
async def get_access_value(message: Message, state: FSMContext):
    access_value = message.text.strip()
    if not access_value:
        await message.answer("Значение доступа не может быть пустым. Пожалуйста, введите значение.")
        return

    user_data = await state.get_data()
    topic_id = user_data['managing_topic_id']
    access_type = user_data['current_access_type']

    await rq.add_topic_access(topic_id, access_type, access_value)
    await message.answer(f"Правило доступа '{message.text}' добавлено для теста. Хотите добавить ещё правила доступа для этого теста?",
                         reply_markup=await kb.yes_no_keyboard())
    await state.set_state(SetTopicAccess.ADD_MORE_ACCESS_RULES)

@admin.message(SetTopicAccess.ADD_MORE_ACCESS_RULES, F.text.in_(['Да', 'Нет', 'да', 'нет']))
async def add_more_access_rules(message: Message, state: FSMContext):
    if message.text == "Да":
        user_data = await state.get_data()
        await message.answer("Выберите следующий тип доступа:", reply_markup=await kb.access_type_keyboard())
        await state.set_state(SetTopicAccess.SELECT_ACCESS_TYPE)
    else:
        await message.answer("Настройка доступа завершена. Вы можете вернуться к этому тесту позже с помощью команды /manage_access.",
                             reply_markup=ReplyKeyboardRemove())
        await state.clear()

@admin.message(SetTopicAccess.ADD_MORE_ACCESS_RULES)
async def invalid_add_more_access_rules(message: Message):
    await message.answer("Пожалуйста, ответьте 'Да' или 'Нет'.")
    
@admin.message(TeacherFilter(), Command("edit_test"))
async def start_edit_test(message: Message, state: FSMContext):
    await state.clear()
    topics = await rq.get_topics_by_creator(message.from_user.id)
    if not topics:
        await message.answer("У вас пока нет созданных тестов для редактирования.")
        return
    await message.answer("Выберите тест, который хотите отредактировать:",
                         reply_markup=await kb.teacher_editable_topics_keyboard(message.from_user.id))
    await state.set_state(EditTest.SELECT_TOPIC_TO_EDIT)
    
@admin.callback_query(EditTest.SELECT_TOPIC_TO_EDIT, F.data.startswith('edit_topic_'))
async def select_topic_to_edit(callback: CallbackQuery, state: FSMContext):
    topic_id = int(callback.data.split('_')[2])
    topic = await rq.get_topic(topic_id)
    
    if not topic:
        await callback.message.edit_text("Выбранная тема не найдена. Попробуйте еще раз.")
        await state.clear()
        await callback.answer()
        return
    
    await state.update_data(editing_topic_id=topic_id, editing_topic_name = topic.topic_name)
    await callback.message.edit_text(f"Вы выбрали тему с ID: {topic_id}:{topic.topic_name}. Загружаю вопросы...")
    
    await display_questions_for_editing(callback.message, state)
    await callback.answer()
    
async def display_questions_for_editing(message: Message, state: FSMContext):
    user_data = await state.get_data()
    topic_id = user_data['editing_topic_id']
    topic_name = user_data['editing_topic_name']
    questions = await rq.get_questions(topic_id)

    if not questions:
        await message.answer("ВВ этой теме пока нет вопросов. Вы можете добавить их, используя /create_test.")
        await state.clear()
        return

    questions_text = f"Список вопросов для темы '{topic_name}' (ID: {topic_id}):\n\n"
    questions_dict = {}
    for i, q in enumerate(questions):
        questions_text += f"{i+1}. {q.text}\n"
        if q.type == 'variant' or q.type == 'Вариантный':
            answers = await rq.get_answers(q.id)
            if answers:
                questions_text += "Варианты ответов:\n"
                for ans in answers:
                    correct_mark = " (Правильный)" if q.true and ans.answer == q.true else ""
                    category_info = ""
                    if ans.category:
                        category_obj = await rq.get_category(ans.category)
                        if category_obj:
                            category_info = f" (Категория: {category_obj.description})"
                    questions_text += f"{ans.answer_text} [{ans.answer}]{category_info}{correct_mark}\n"
            else:
                questions_text +="Вариантов ответов пока нет."
        elif q.type in ['yes_no', 'Да/Нет'] and q.true:
            questions_text += f"Правильный ответ: {q.true or 'не задан'}\n"
        elif int(q.type) > 1:
            questions_text += f"Шкала от 1 до {q.type}. Обратная шкала: {'Да' if q.is_reverse else 'Нет'}\n"
        
        questions_text += "\n"
        questions_dict[str(i+1)] = q.id
    
    await state.update_data(questions_for_edit_map=questions_dict)

    await message.answer(questions_text)
    await message.answer("Введите номер вопроса, который хотите отредактировать, или 'готово' для завершения редактирования темы.")
    await state.set_state(EditTest.SELECT_QUESTION_TO_EDIT)
    
@admin.message(EditTest.SELECT_QUESTION_TO_EDIT)
async def select_question_for_edit(message: Message, state: FSMContext):
    user_data = await state.get_data()
    questions_map = user_data.get('questions_for_edit_map')

    if message.text.lower() == 'готово':
        await message.answer("Редактирование темы завершено. Вы можете снова использовать /edit_test.", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return

    try:
        question_num = int(message.text)
        selected_question_id = questions_map.get(str(question_num))
        if not selected_question_id:
            raise ValueError("Неверный номер вопроса.")
    except (ValueError, TypeError):
        await message.answer("Пожалуйста, введите корректный номер вопроса или 'готово'.")
        return

    await state.update_data(editing_question_id=selected_question_id)
    await display_selected_question_options(message, state)
    await state.set_state(EditTest.SELECT_EDIT_OPTION)
    
async def display_selected_question_options(message: Message, state: FSMContext):
    user_data = await state.get_data()
    question_id = user_data['editing_question_id']
    question = await rq.get_question(question_id)
    
    current_q_text = f"Выбран вопрос для редактирования:\n" \
                     f"Тип: {question.type}\n" \
                     f"Текст: '{question.text}'\n"
    if question.true:
        current_q_text += f"Правильный ответ: '{question.true}'\n"

    edit_options_keyboard = await kb.edit_question_main_options_keyboard(question.type)

    await message.answer(current_q_text, reply_markup=edit_options_keyboard)
    
@admin.message(EditTest.SELECT_EDIT_OPTION, F.text.in_(['Редактировать текст вопроса', 'Изменить правильный ответ', 'Управление вариантами ответов', 
                                                        'Вернуться к списку вопросов темы', 'Завершить редактирование']))
async def select_edit_option(message: Message, state: FSMContext):
    user_data = await state.get_data()
    question_id = user_data['editing_question_id']
    question = await rq.get_question(question_id)
    
    if message.text == 'Редактировать текст вопроса':
        await message.answer("Введите новый текст вопроса:")
        await state.set_state(EditTest.GET_NEW_QUESTION_TEXT)
    elif message.text == 'Изменить правильный ответ':
        if question.type.isdigit():
            await message.answer("Для вопросов типа 'Шкала' нет 'правильного' ответа. Выберите другую опцию.", 
                                 reply_markup=await kb.edit_question_main_options_keyboard(question.type))
            return

        if question.type == 'variant' or question.type == 'Вариантный':
            answers = await rq.get_answers(question_id)
            if not answers:
                await message.answer("У этого вариантного вопроса нет ответов, вы не можете установить правильный ответ. Сначала добавьте варианты ответов.", reply_markup=await kb.edit_question_main_options_keyboard(question.type))
                return
            ans_options = ", ".join([f"'{a.answer}'" for a in answers])
            await message.answer(f"Введите НОВОЕ ЗНАЧЕНИЕ правильного ответа (выберите из значений вариантов: {ans_options}).\n"
                                 "Если правильного ответа нет (опрос), отправьте '-'.")
        elif question.type == 'yes_no' or question.type == 'Да/Нет':
            await message.answer("Введите новый правильный ответ ('Да' или 'Нет'):")
        elif int(question.type) > 1:
            await message.answer("Для вопросов типа 'Шкала' нет 'правильного' ответа. Выберите другую опцию.", reply_markup=await kb.edit_question_main_options_keyboard(question.type))
            return
        await state.set_state(EditTest.GET_NEW_TRUE_ANSWER)
    elif message.text == 'Управление вариантами ответов':
        if question.type != 'variant' and  question.type != 'Вариантный':
            await message.answer("Эта опция доступна только для 'Вариантных' вопросов.", reply_markup=await kb.edit_question_main_options_keyboard(question.type))
            return
        await display_manage_answers_menu(message, state)
        await state.set_state(EditTest.MANAGE_ANSWERS_MENU)
    elif message.text == 'Вернуться к списку вопросов темы':
        await display_questions_for_editing(message, state)
    elif message.text == 'Завершить редактирование':
        await message.answer("Редактирование тестов завершено. Вы можете снова использовать /edit_test.", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        
@admin.message(EditTest.GET_NEW_QUESTION_TEXT)
async def get_new_question_text(message: Message, state: FSMContext):
    user_data = await state.get_data()
    question_id = user_data['editing_question_id']
    new_text = message.text.strip()
    if not new_text:
        await message.answer("Текст вопроса не может быть пустым. Введите новый текст вопроса:")
        return

    await rq.update_question_text(question_id, new_text)
    question = await rq.get_question(question_id)
    await message.answer("Текст вопроса успешно обновлен. Выберите следующую опцию:", reply_markup=await kb.edit_question_main_options_keyboard(question.type))
    await state.set_state(EditTest.SELECT_EDIT_OPTION)
    
@admin.message(EditTest.GET_NEW_TRUE_ANSWER)
async def get_new_true_answer(message: Message, state: FSMContext):
    user_data = await state.get_data()
    question_id = user_data['editing_question_id']
    new_true_answer = message.text.strip()

    question = await rq.get_question(question_id)
    
    if question.type == 'yes_no' or question.type == 'Да/Нет':
        if new_true_answer.lower() not in ['да', 'нет', 'yes', 'no']:
            await message.answer("Для вопроса 'Да/Нет' правильный ответ должен быть 'Да' или 'Нет'. Повторите ввод:")
            return
        if new_true_answer.lower() == 'да': new_true_answer = 'Yes'
        elif new_true_answer.lower() == 'нет': new_true_answer = 'No'
    elif question.type == 'variant' or question.type == 'Вариантный':
        if new_true_answer != '-':
            answers = await rq.get_answers(question_id)
            valid_answers = [a.answer for a in answers]
            if new_true_answer not in valid_answers:
                await message.answer(f"Правильный ответ должен быть одним из существующих вариантов: {', '.join(valid_answers)}. Повторите ввод:")
                return
    
    await rq.update_question_true_answer(question_id, new_true_answer if new_true_answer != '-' else None)

    await message.answer("Правильный ответ успешно обновлен. Выберите следующую опцию:", reply_markup=await kb.edit_question_main_options_keyboard(question.type))
    await state.set_state(EditTest.SELECT_EDIT_OPTION)

async def display_manage_answers_menu(message: Message, state: FSMContext):
    user_data = await state.get_data()
    question_id = user_data['editing_question_id']
    answers = await rq.get_answers(question_id)

    answers_text = "Текущие варианты ответов:\n\n"
    answers_map_by_num = {}
    if answers:
        for i, ans in enumerate(answers):
            category_info = ""
            if ans.category:
                category_obj = await rq.get_category(ans.category)
                if category_obj:
                    category_info = f" (Категория: {category_obj.description})"
            answers_text += f"{i+1}. Текст: '{ans.answer_text}' | Значение: '{ans.answer}'{category_info}\n"
            answers_map_by_num[str(i+1)] = ans.id
    else:
        answers_text += "    Вариантов ответов пока нет.\n"

    await state.update_data(answers_for_edit_map=answers_map_by_num)
    
    await message.answer(answers_text)
    await message.answer("Выберите действие:", reply_markup=await kb.manage_answers_options_keyboard())

@admin.message(EditTest.MANAGE_ANSWERS_MENU, F.text.in_(['Редактировать существующий', 'Добавить новый', 'Удалить', 'Вернуться к опциям вопроса']))
async def manage_answers_option(message: Message, state: FSMContext):
    user_data = await state.get_data()
    answers_map = user_data.get('answers_for_edit_map', {})

    if message.text == 'Редактировать существующий':
        if not answers_map:
            await message.answer("Нет вариантов для редактирования. Добавьте новый.", reply_markup=await kb.manage_answers_options_keyboard())
            return
        await message.answer("Введите номер варианта ответа для редактирования:")
        await state.set_state(EditTest.SELECT_ANSWER_TO_MODIFY)
        await state.update_data(context_for_answer_modify='edit')
    elif message.text == 'Добавить новый':
        await message.answer("Введите текст, значение и опционально категорию нового ответа в формате a)'текст_ответа/значение_ответа/Название_категории'.\nПример: 'Лев Толстой/A/Компетентные'")
        await state.set_state(EditTest.ADD_NEW_ANSWER_DETAILS)
    elif message.text == 'Удалить':
        if not answers_map:
            await message.answer("Нет вариантов для удаления.", reply_markup=await kb.manage_answers_options_keyboard())
            return
        await message.answer("Введите номер варианта ответа для удаления:")
        await state.set_state(EditTest.SELECT_ANSWER_TO_MODIFY)
        await state.update_data(context_for_answer_modify='delete')
    elif message.text == 'Вернуться к опциям вопроса':
        await display_selected_question_options(message, state)
        await state.set_state(EditTest.SELECT_EDIT_OPTION)

@admin.message(EditTest.SELECT_ANSWER_TO_MODIFY)
async def select_answer_to_modify(message: Message, state: FSMContext):
    user_data = await state.get_data()
    answers_map = user_data.get('answers_for_edit_map', {})
    context = user_data.get('context_for_answer_modify', 'edit')

    try:
        answer_num = int(message.text)
        selected_answer_id = answers_map.get(str(answer_num))
        if not selected_answer_id:
            raise ValueError("Неверный номер варианта ответа.")
    except (ValueError, TypeError):
        await message.answer("Пожалуйста, введите корректный номер варианта ответа.")
        return
    
    await state.update_data(editing_answer_id=selected_answer_id)
    
    answer = await rq.get_answer(selected_answer_id)
    
    if context == 'delete':
        await message.answer(f"Вы уверены, что хотите удалить вариант ответа: '{answer.answer_text}'?", reply_markup=await kb.yes_no_keyboard())
        await state.set_state(EditTest.CONFIRM_DELETE_ANSWER)
    else:
        current_ans_text = f"Редактирование варианта ответа №{answer_num}:\n" \
                           f"Текст: '{answer.answer_text}'\n" \
                           f"Значение: '{answer.answer}'\n"
        if answer.category:
            category_obj = await rq.get_category(answer.category)
            if category_obj:
                current_ans_text += f"Категория: '{category_obj.description}'\n"

        await message.answer(current_ans_text)
        await message.answer("Выберите опцию редактирования:", reply_markup=await kb.edit_single_answer_options_keyboard())
        await state.set_state(EditTest.SELECT_MODIFY_ANSWER_OPTION)

@admin.message(EditTest.SELECT_MODIFY_ANSWER_OPTION, F.text.in_(['Изменить текст', 'Изменить значение', 'Изменить категорию', 'Удалить этот вариант', 'Вернуться к списку вариантов']))
async def select_modify_answer_option(message: Message, state: FSMContext):
    user_data = await state.get_data()
    answer_id = user_data['editing_answer_id']
    answer = await rq.get_answer(answer_id)

    if message.text == 'Изменить текст':
        await message.answer("Введите новый текст варианта ответа:")
        await state.set_state(EditTest.GET_NEW_ANSWER_TEXT)
    elif message.text == 'Изменить значение':
        await message.answer("Введите новое значение варианта ответа (например, 'A', 'B', 'C'):")
        await state.set_state(EditTest.GET_NEW_ANSWER_VALUE)
    elif message.text == 'Изменить категорию':
        topic_id = user_data['editing_topic_id']
        categories_keyboard = await kb.select_category_keyboard(topic_id)
        if not categories_keyboard.inline_keyboard:
            await message.answer("В этой теме нет доступных категорий. Выберите другую опцию.", reply_markup=await kb.edit_single_answer_options_keyboard())
            return
        await message.answer("Выберите новую категорию для этого варианта ответа:", reply_markup=categories_keyboard)
        await state.set_state(EditTest.GET_NEW_ANSWER_CATEGORY_NAME)
    elif message.text == 'Удалить этот вариант':
        await message.answer(f"Вы уверены, что хотите удалить вариант ответа: '{answer.answer_text}'?", reply_markup=await kb.yes_no_keyboard())
        await state.set_state(EditTest.CONFIRM_DELETE_ANSWER)
    elif message.text == 'Вернуться к списку вариантов':
        await display_manage_answers_menu(message, state)
        await state.set_state(EditTest.MANAGE_ANSWERS_MENU)

@admin.message(EditTest.GET_NEW_ANSWER_TEXT)
async def get_new_answer_text(message: Message, state: FSMContext):
    user_data = await state.get_data()
    answer_id = user_data['editing_answer_id']
    new_text = message.text.strip()
    if not new_text:
        await message.answer("Текст не может быть пустым. Введите новый текст:")
        return

    await rq.update_answer_text(answer_id, new_text)
    await message.answer("Текст варианта ответа обновлен.")
    await display_manage_answers_menu(message, state)
    await state.set_state(EditTest.MANAGE_ANSWERS_MENU)

@admin.message(EditTest.GET_NEW_ANSWER_VALUE)
async def get_new_answer_value(message: Message, state: FSMContext):
    user_data = await state.get_data()
    answer_id = user_data['editing_answer_id']
    new_value = message.text.strip()
    if not new_value:
        await message.answer("Значение не может быть пустым. Введите новое значение:")
        return

    await rq.update_answer_value(answer_id, new_value)
    await message.answer("Значение варианта ответа обновлено.")
    await display_manage_answers_menu(message, state)
    await state.set_state(EditTest.MANAGE_ANSWERS_MENU)

@admin.callback_query(EditTest.GET_NEW_ANSWER_CATEGORY_NAME, F.data.startswith('select_cat:'))
async def get_new_answer_category_name(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    answer_id = user_data['editing_answer_id']
    category_id_str = callback.data.split(':')[1]
    category_id = int(category_id_str) if category_id_str != 'None' else None

    await rq.update_answer_category(answer_id, category_id)
    await callback.message.edit_text("Категория варианта ответа обновлена.") 
    await display_manage_answers_menu(callback.message, state)
    await state.set_state(EditTest.MANAGE_ANSWERS_MENU)
    await callback.answer()

@admin.message(EditTest.ADD_NEW_ANSWER_DETAILS)
async def add_new_answer_details(message: Message, state: FSMContext):
    user_data = await state.get_data()
    question_id = user_data['editing_question_id']
    
    parts = message.text.split('/')
    answer_text = parts[0].strip()
    answer_value = parts[1].strip() if len(parts) > 1 else None
    category_name = parts[2].strip() if len(parts) > 2 else None

    if not answer_text or not answer_value:
        await message.answer("Неверный формат. Пожалуйста, используйте a)'текст_ответа/значение_ответа' и опционально '/Название_категории'.")
        return
    
    category_id = None
    topic_id = user_data['editing_topic_id']
    categories_in_topic = await rq.get_categories(topic_id)
    if categories_in_topic:
        if category_name:
            found_category = None
            for cat in categories_in_topic:
                if cat.description.lower() == category_name.lower():
                    found_category = cat
                    break
            
            if found_category:
                category_id = found_category.id
            else:
                await message.answer(f"Категория '{category_name}' не найдена в этой теме. Пожалуйста, используйте существующую категорию из списка тем или проверьте ввод.")
                return
        else:
            await message.answer("Вы указали, что ответы имеют категории, но не указали категорию для этого ответа. Формат: a)'текст_ответа/значение_ответа/Название_категории'")
            return
    else:
        if category_name:
            await message.answer("Категории не были включены для этой темы, указанная категория будет проигнорирована.")

    await rq.add_answer(question_id, answer_text, answer_value, category_id)
    await message.answer("Новый вариант ответа добавлен.")
    await display_manage_answers_menu(message, state)
    await state.set_state(EditTest.MANAGE_ANSWERS_MENU)

@admin.message(EditTest.CONFIRM_DELETE_ANSWER, F.text.in_(['Да', 'Нет', 'да', 'нет']))
async def confirm_delete_answer(message: Message, state: FSMContext):
    if message.text == 'Да':
        user_data = await state.get_data()
        answer_id = user_data['editing_answer_id']
        answer = await rq.get_answer(answer_id)

        success = await rq.delete_answer(answer_id)
        if success:
            await message.answer(f"Вариант ответа '{answer.answer_text}' успешно удален.")
            question = await rq.get_question(answer.question_id)
            if question and question.true == answer.answer:
                await rq.update_question_true_answer(question.id, None)
                await message.answer("Поле 'правильный ответ' для вопроса также было сброшено.")

        else:
            await message.answer("Произошла ошибка при удалении варианта ответа.")
    else:
        await message.answer("Удаление варианта ответа отменено.")
    
    await display_manage_answers_menu(message, state)
    await state.set_state(EditTest.MANAGE_ANSWERS_MENU)

@admin.message(TeacherFilter(), Command("delete_test"))
async def start_delete_test(message: Message, state: FSMContext):
    await state.clear()
    topics = await rq.get_topics_by_creator(message.from_user.id)
    if not topics:
        await message.answer("У вас пока нет созданных тестов для удаления.")
        return
    await message.answer("Выберите тест, который хотите удалить:",
                         reply_markup=await kb.teacher_deletable_topics_keyboard(message.from_user.id))
    await state.set_state(DeleteTest.SELECT_TOPIC_TO_DELETE)
    
@admin.callback_query(DeleteTest.SELECT_TOPIC_TO_DELETE, F.data.startswith('delete_topic_'))
async def select_topic_to_delete(callback: CallbackQuery, state: FSMContext):
    topic_id = int(callback.data.split('_')[2])
    topic = await rq.get_topic(topic_id)
    if not topic:
        await callback.message.edit_text("Выбранная тема не найдена. Попробуйте еще раз.")
        await state.clear()
        await callback.answer()
        return

    await state.update_data(deleting_topic_id=topic_id, deleting_topic_name=topic.topic_name)

    await callback.message.edit_text(f"Вы выбрали тему: '{topic.topic_name}'.\n\n"
                                     f"ВНИМАНИЕ! Это действие удалит ТЕМУ И ВСЕ СВЯЗАННЫЕ С НЕЙ ДАННЫЕ (вопросы, ответы, результаты, настройки доступа)!\n")
    await callback.message.answer("Вы уверены, что хотите продолжить?",
                                  reply_markup=await kb.yes_no_keyboard())
    await state.set_state(DeleteTest.CONFIRM_DELETE)
    await callback.answer()
    
@admin.message(DeleteTest.CONFIRM_DELETE, F.text.in_(['Да', 'Нет', 'да', 'нет']))
async def confirm_delete(message: Message, state: FSMContext):
    if message.text == 'Да':
        user_data = await state.get_data()
        topic_id = user_data['deleting_topic_id']
        topic_name = user_data['deleting_topic_name']
        success = await rq.delete_topic_and_all_related_data(topic_id)
        
        if success:
            await message.answer(f"Тема '{topic_name}' и все связанные данные успешно удалены.", reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer(f"Произошла ошибка при удалении темы '{topic_name}'. Попробуйте позже или обратитесь к администратору.", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Удаление отменено.", reply_markup=ReplyKeyboardRemove())
    await state.clear()

@admin.message(DeleteTest.CONFIRM_DELETE)
async def invalid_confirm_delete(message: Message):
    await message.answer("Пожалуйста, ответьте 'Да' или 'Нет'.")