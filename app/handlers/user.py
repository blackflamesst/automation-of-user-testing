from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from app.database import requests as rq
from app import keyboards as kb
from app.keyboards import all_topics, create_role_keyboard
from app.generate import ai_generate
from app.database.models import Role, User

USER_ANSWER_CALLBACK = 'answer'
NONE_CATEGORY = "None"

user = Router()

class Process(StatesGroup):
    role = State()
    name = State()
    city = State()
    univercity = State()
    institute = State()
    department = State()
    stream = State()
    group = State()
    age = State()
    
@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await rq.add_user(message.from_user.id)
    if not user:
        await message.answer('Добро пожаловать!\nВыберите вашу роль:', reply_markup= await create_role_keyboard())
        await state.set_state(Process.role)
    else:
        user_data = await rq.get_user(message.from_user.id)
        if not user_data.name:
            await message.answer('Добро пожаловать снова! Пожалуйста, продолжите заполнение вашего профиля. Введите ваше ФИО:', reply_markup=ReplyKeyboardRemove())
            await state.set_state(Process.name)
        else:
            if user_data.role == Role.STUDENT:
                await message.answer('Вам доступна команда /topic для выбора темы тестирования')
                await message.answer('Вам доступна команда /res для просмотра всех своих результатов')
            elif user_data.role == Role.TEACHER:
                await message.answer('Вы вошли как преподаватель')
                await message.answer('Вам доступна команда /create_test для создания теста')
                await message.answer('Вам доступна команда /manage_access для настройки доступа к тестам')
                await message.answer('Вам доступна команда /edit_test для редактирования теста')
                await message.answer('Вам доступна команда /delete_test для удаления теста')
            
@user.message(Process.role, F.text.in_(['Студент', 'Преподаватель']))
async def get_role(message: Message, state: FSMContext):
    if message.text == "Студент":
        await state.update_data(role=Role.STUDENT)
    else:
        await state.update_data(role=Role.TEACHER)
    await message.answer('Введите ваше ФИО', reply_markup=ReplyKeyboardRemove())
    await state.set_state(Process.name)

@user.message(Process.role)
async def invalid_role(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, выберите роль из предложенных вариантов: Студент или Преподаватель")

@user.message(Process.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Process.city)
    await message.answer('Введите название города обучения')

@user.message(Process.city)
async def get_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(Process.univercity)
    await message.answer('Введите сокращённое название университета (например, "СурГУ", "ПАО Газпром"), если нет, отправьте "-":')
    
@user.message(Process.univercity)
async def get_univercity(message: Message, state: FSMContext):
    univercity_val = message.text if message.text != '-' else None
    await state.update_data(univercity=univercity_val)
    await state.set_state(Process.institute)
    await message.answer('Введите название вашего института (например, "Политехнический"), если нет, отправьте "-":')
    
@user.message(Process.institute)
async def get_institute(message: Message, state: FSMContext):
    institute_val = message.text if message.text != '-' else None
    await state.update_data(institute=institute_val)
    await state.set_state(Process.department)
    await message.answer('Введите название вашей кафедры (например, "Автоматики и компьютерных систем"), если нет, отправьте "-":')
    
@user.message(Process.department)
async def get_department(message: Message, state: FSMContext):
    department_val = message.text if message.text != '-' else None
    await state.update_data(department=department_val)
    await state.set_state(Process.stream)
    await message.answer('Введите название вашего направления (например, "Управление в технических системах"), если нет, отправьте "-":')

@user.message(Process.stream)
async def get_stream(message: Message, state: FSMContext):
    stream_val = message.text if message.text != '-' else None
    await state.update_data(stream=stream_val)
    await state.set_state(Process.group)
    await message.answer('Введите номер группы (если вы не состоите в группе, отправьте "-"), например: 605-01z, используя символы от a до z, если они имеются ')
    
@user.message(Process.group)
async def get_group(message: Message, state: FSMContext):
    group_val = message.text if message.text != '-' else None
    await state.update_data(group=message.text)
    await state.set_state(Process.age)
    await message.answer('Введите ваш возраст')
    
@user.message(Process.age)
async def choose_topic(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    user_data = await state.get_data()
    
    group_val = user_data['group'] if user_data['group'] != '-' else None
    city_val = user_data['city'] if user_data['city'] != '-' else None
    univercity_val = user_data['univercity'] if user_data['univercity'] != '-' else None
    institute_val = user_data.get('institute') if user_data.get('institute') != '-' else None
    department_val = user_data.get('department') if user_data.get('department') != '-' else None
    stream_val = user_data.get('stream') if user_data.get('stream') != '-' else None
    
    await rq.edit_user(
        tg_id=message.from_user.id,
        name=user_data['name'],
        group=group_val,
        age=user_data['age'],
        username=message.from_user.username,
        city=city_val,
        univercity=univercity_val,
        institute=institute_val,
        department=department_val,
        stream=stream_val,
        role=user_data['role'])
    await message.answer('Вы успешно зарегистрированы')
    if user_data['role'] == Role.STUDENT:
        await message.answer('Вам доступна команда /topic для выбора темы тестирования')
        await message.answer('Вам доступна команда /res для просмотра всех своих результатов')
    elif user_data['role'] == Role.TEACHER:
        await message.answer('Вы вошли как преподаватель')
        await message.answer('Вам доступна команда /create_test для создания теста')
        await message.answer('Вам доступна команда /manage_access для настройки доступа к тестам')
        await message.answer('Вам доступна команда /edit_test для редактирования теста')
        await message.answer('Вам доступна команда /delete_test для удаления теста')
    await state.clear()

@user.message(Command('topic'))
async def choosing_theme(message: Message):
    user = await rq.get_user(message.from_user.id)
    if not user or not user.name:
        await message.answer("Пожалуйста, сначала зарегистрируйтесь, используя команду /start.")
        return
    
    available_topics_markup = await kb.all_topics(user) 
    if available_topics_markup:
        await message.answer('Выберите какой тест хотите пройти', reply_markup=available_topics_markup)
    else:
        await message.answer('В настоящее время для вас нет доступных тестов.')

@user.message(Command('res'))
async def show_user_results(message: Message):
    topics = await rq.get_topics()
    for topic in topics:
        result = await rq.get_result_from_user(message.from_user.id, topic.id)
        results_by_category = await rq.get_results_from_user_by_categories(message.from_user.id, topic.id)
        results_by_qualities = await rq.get_results_from_user_by_qualities(message.from_user.id, topic.id)
        if result or results_by_category or results_by_qualities:
            await message.answer(f"Тема: {topic.topic_name}")
        if result:
            description = await rq.get_description(result.result, topic.id)
            await message.answer(description.description)
        if results_by_category:
            for result_by_category in results_by_category:
                val = "{:.1f}".format(result_by_category.result/topic.questions_count*100)
                category = await rq.get_category(result_by_category.category_id)
                await message.answer(f"Категория: {category.description}\nРезультат: {str(val)}%")
        if results_by_qualities:
            for result_by_quality in results_by_qualities:
                quality = await rq.get_quality(result_by_quality.quality_id)
                description = await rq.get_description_from_quality(result_by_quality.result, result_by_quality.quality_id, topic.id)
                await message.answer(f"{quality.description}: {description.description}")
    
@user.callback_query(F.data.startswith('topic_'))
async def start_test(callback: CallbackQuery):
    await callback.answer('Вы выбрали тему')
    theme = callback.data.split('_')[1]
    categories = await rq.get_categories(theme)
    if categories:
        await rq.clear_and_create_category_results(callback.from_user.id, theme, categories)
    qualities = await rq.get_qualities(theme)
    if qualities:
        await rq.clear_and_create_quality_results(callback.from_user.id, theme, qualities)

    questions = await rq.get_questions(theme)
    question = questions[0]
    if question:
        await rq.edit_user_topic(callback.from_user.id, theme)
        await handle_question(callback, question)

@user.callback_query(F.data.startswith(f'{USER_ANSWER_CALLBACK}:'))
async def test(callback: CallbackQuery):
    action, question_id_any, user_answer, category = callback.data.split(':')
    question_id = int(question_id_any)
    question = await rq.get_question(question_id)
    
    if category != NONE_CATEGORY:
        await rq.edit_result_by_category(callback.from_user.id, int(category), question.topic)

    if question.true:
        if user_answer == question.true:
            if question.quality:
                await rq.edit_result_by_quality(callback.from_user.id, question.quality, question.topic)
            if category == NONE_CATEGORY:
                await rq.edit_result_on_user(callback.from_user.id)
            await callback.answer()
        else:
            await callback.answer()
    else:
        value = int(question.type)
        user_answer = int(user_answer)
        if question.is_reverse:
            user_answer = value - user_answer + 1
        if question.quality:
            await rq.edit_result_by_quality(callback.from_user.id, question.quality, question.topic, user_answer)
        if category == NONE_CATEGORY:
            await rq.edit_result_on_user(callback.from_user.id, user_answer)
        await callback.answer()

    next_question = await rq.get_next_question(question.topic, question_id)

    if next_question:
        if next_question.type != 'variant' and next_question.type != 'Вариантный':
            await callback.message.edit_text(next_question.text, reply_markup=await kb.answering(next_question.id, next_question.type))
        else:
            await send_question(callback, next_question.id)
    else:
        theme = await rq.get_topic(question.topic)
        student_user = await rq.get_user(callback.from_user.id)
        await callback.message.edit_text(f"Тест завершён!\nТема: {theme.topic_name}")
        
        ai_prompt = f"Оцени результаты теста по теме {theme.topic_name} и дай рекомендации по улучшению знаний и отправь мне пожалуйста источники, где это можно изучить.  Вот результаты:\n"
        
        student_results_text = f"Ваши результаты по тесту '{theme.topic_name}':\n"
        
        if category == NONE_CATEGORY:
            if student_user.selected_topic is not None and student_user.count_true_answers is not None:
                overall_description = await rq.get_description(student_user.count_true_answers, question.topic)
                await rq.add_result(callback.from_user.id, question.topic, student_user.count_true_answers)
                if overall_description:
                    student_results_text += f"\nОбщий результат: {overall_description.description}"
                    ai_prompt += f"Общий результат: {overall_description.description}\n"
                else:
                    student_results_text += f"\nОбщий балл: {student_user.count_true_answers}"
                    ai_prompt += f"Общий балл: {student_user.count_true_answers}\n"
        else:
            results_by_categories = await rq.get_results_from_user_by_categories(callback.from_user.id, question.topic)
            if results_by_categories:
                student_results_text += "\n\nРезультаты по категориям:\n"
                for result_by_category in results_by_categories:
                    percentage_val = (result_by_category.result/theme.questions_count*100) if theme.questions_count else 0
                    value_formatted = "{:.1f}".format(percentage_val)
                    category_description = await rq.get_category(result_by_category.category_id)
                    if category_description:
                        display_message = f"Категория: - {category_description.description} : {str(value_formatted)}%"
                        student_results_text += display_message + "\n"
                        ai_prompt += display_message + "\n"
                        
        results_by_qualities = await rq.get_results_from_user_by_qualities(callback.from_user.id, question.topic)
        if results_by_qualities:
            student_results_text += "\n\nРезультаты по качествам:\n"
            for result_by_quality in results_by_qualities:
                quality = await rq.get_quality(result_by_quality.quality_id)
                quality_description = await rq.get_description_from_quality(result_by_quality.result, result_by_quality.quality_id, question.topic)
                if quality and quality_description:
                    display_message = f"{quality.description}: {quality_description.description}"
                    student_results_text += display_message + "\n"
                    ai_prompt += f"{display_message}\n"
                elif quality:
                    display_message = f"  - {quality.description}: {result_by_quality.result} баллов"
                    student_results_text += display_message + "\n"
                    ai_prompt += display_message + "\n"
        
        await rq.clear_topic_result(callback.from_user.id)
        
        creator_tg_id = theme.topic_creator
        if creator_tg_id and creator_tg_id != callback.from_user.id:
            try:
                teacher_message = f"✅ Обучающийся {student_user.name}: ({student_user.group}) завершил тест '{theme.topic_name}'.\n\n"
                teacher_message += "--- Результаты ученика ---\n"
                teacher_message += student_results_text.replace("Ваши результаты", "Результаты ученика")
                
                await callback.bot.send_message(chat_id=creator_tg_id, text=teacher_message)

                print(f"Результаты теста для {student_user.name} отправлены преподавателю {creator_tg_id}.")
            except Exception as e:
                print(f"Не удалось отправить результаты преподавателю {creator_tg_id}: {e}")
                
        await callback.message.answer(student_results_text)
        await callback.message.answer("Генерирую рекомендации...")
        ai_response = await ai_generate(ai_prompt)
        await callback.message.answer(ai_response)

async def handle_question(callback: CallbackQuery, question):
    if question.type == 'variant' or question.type == 'Вариантный':
        await send_question(callback, question.id)
    else:
        await callback.message.edit_text(question.text, reply_markup=await kb.answering(question.id, question.type))

async def send_question(callback: CallbackQuery, question_id: int):
    question = await rq.get_question(question_id)
    answers = await rq.get_answers(question_id)
    answer_texts = "\n".join([answer.answer_text for answer in answers])
    full_text = f"{question.text}\n\n{answer_texts}"
    await callback.message.edit_text(full_text, reply_markup=await kb.answering(question.id, question.type))