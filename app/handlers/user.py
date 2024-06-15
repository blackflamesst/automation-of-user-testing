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

class Topic(StatesGroup):
    topic_id = State()
    
@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await rq.add_user(message.from_user.id)
    if not user:
        await message.answer('Добро пожаловать\n\nВведите ваше имя')
        await state.set_state(Process.name)
    else:
        await message.answer('Выберите какой тест хотите пройти', reply_markup=await all_topics())

@user.message(Process.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Process.group)
    await message.answer('Введите номер группы')
    
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
    await message.answer('Вам доступна команда "/theme" для выбора темы тестирования')
    await message.answer('Вам доступна команда "/res" для просмотра своих результатов')
    await message.answer('Вы успешно зарегистрированы')
    await message.answer('Выберите какой тест хотите пройти', reply_markup=await all_topics())
    await state.clear()
    
@user.callback_query(F.data.startswith('topic_'))
async def start_test(callback: CallbackQuery):
    await callback.answer('Вы выбрали тему')
    questions = await rq.get_questions(callback.data.split('_')[1])
    question = questions[0]
    if question:
        await rq.edit_user_topic(callback.from_user.id, callback.data.split('_')[1])
        await callback.message.edit_text(question.text, reply_markup=await kb.answering(question.id))

@user.callback_query(F.data.startswith('answer:'))
async def test(callback: CallbackQuery):
    action, question_id, user_answer = callback.data.split(':')

    question = await rq.get_question(question_id)
    correct_answer = question.true

    if user_answer == correct_answer:
        await callback.answer("Правильный ответ!")
    else:
        await callback.answer("Неправильный ответ.")

    next_question = await rq.get_next_question(question.topic, question_id)

    if next_question:
        await callback.message.edit_text(next_question.text, reply_markup=await kb.answering(next_question.id))
    else:
        await callback.message.delete()
        await callback.message.answer("Тестирование завершено.")