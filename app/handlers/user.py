from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from app.database import requests as rq
from app import keyboards as kb
from app.keyboards import all_topics

user = Router()

class Process(StatesGroup):
    name = State()
    group = State()
    age = State()
    
@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await rq.add_user(message.from_user.id)
    if not user:
        await message.answer('Добро пожаловать\n\nВведите ваше имя')
        await state.set_state(Process.name)
    else:
        await message.answer('Вам доступна команда /theme для выбора темы тестирования')
        await message.answer('Вам доступна команда /res для просмотра всех своих результатов')

@user.message(Process.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Process.group)
    await message.answer('Введите номер группы (если вы не состоите в группе, отправьте "-")')
    
@user.message(Process.group)
async def get_group(message: Message, state: FSMContext):
    await state.update_data(group=message.text)
    await state.set_state(Process.age)
    await message.answer('Введите ваш возраст')
    
@user.message(Process.age)
async def choose_topic(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    user = await state.get_data()
    await rq.edit_user(message.from_user.id,
                       user['name'],
                       user['group'],
                       user['age'],
                       message.from_user.username)
    await message.answer('Вы успешно зарегистрированы')
    await message.answer('Вам доступна команда /theme для выбора темы тестирования')
    await message.answer('Вам доступна команда /res для просмотра всех своих результатов')
    await state.clear()

@user.message(Command('theme'))
async def choosing_theme(message: Message):
    await message.answer('Выберите какой тест хотите пройти', reply_markup=await all_topics())

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

@user.callback_query(F.data.startswith('answer:'))
async def test(callback: CallbackQuery):
    action, question_id, user_answer, category = callback.data.split(':')
    question = await rq.get_question(question_id)
    if category != "None":
        await rq.edit_result_by_category(callback.from_user.id, category, question.topic)
        print("LOG CATEGORY ISZZZZZZZZZZZZZZZZ ", category)

    if question.true:
        if user_answer == question.true:
            if question.quality:
                print("LOG Question quality us", question.quality)
                await rq.edit_result_by_quality(callback.from_user.id, question.quality, question.topic)
            if category == "None":
                await rq.edit_result_on_user(callback.from_user.id)
                print("LOG USPESHNO")
            print("LOG CATEGORY IS ", category)
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
        if category == "None":
            await rq.edit_result_on_user(callback.from_user.id, user_answer)
        await callback.answer()

    next_question = await rq.get_next_question(question.topic, question_id)

    if next_question:
        if next_question.type != 'variant':
            await callback.message.edit_text(next_question.text, reply_markup=await kb.answering(next_question.id, next_question.type))
        else:
            await send_question(callback, next_question.id)
    else:
        theme = await rq.get_topic(question.topic)
        await callback.message.edit_text(f"Тема: {theme.topic_name}")
        if category == "None":
            user = await rq.get_user(callback.from_user.id)
            description = await rq.get_description(user.count_true_answers, question.topic)
            await rq.add_result(callback.from_user.id, question.topic, user.count_true_answers)
            await callback.message.answer(description.description)
        else:
            results_by_categories = await rq.get_results_from_user_by_categories(callback.from_user.id, question.topic)
            for result_by_category in results_by_categories:
                val = "{:.1f}".format(result_by_category.result/theme.questions_count*100)
                category_description = await rq.get_category(result_by_category.category_id)
                await callback.message.answer(f"Категория: {category_description.description} - {str(val)}%")
        if question.quality is not None:
            results_by_qualities = await rq.get_results_from_user_by_qualities(callback.from_user.id, question.topic)
            for result_by_quality in results_by_qualities:
                quality = await rq.get_quality(result_by_quality.quality_id)
                description = await rq.get_description_from_quality(result_by_quality.result, result_by_quality.quality_id, question.topic)
                await callback.message.answer(f"{quality.description}: {description.description}")
        await rq.clear_topic_result(callback.from_user.id)

async def handle_question(callback: CallbackQuery, question):
    if question.type == 'variant':
        await send_question(callback, question.id)
    else:
        await callback.message.edit_text(question.text, reply_markup=await kb.answering(question.id, question.type))

async def send_question(callback: CallbackQuery, question_id: int):
    question = await rq.get_question(question_id)
    answers = await rq.get_answers(question_id)
    answer_texts = "\n".join([answer.answer_text for answer in answers])
    full_text = f"{question.text}\n\n{answer_texts}"
    await callback.message.edit_text(full_text, reply_markup=await kb.answering(question.id, question.type))