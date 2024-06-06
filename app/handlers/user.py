from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from app.database import requests as rq
from app import keyboards as kb
from app.keyboards import all_topics, answer
from app.database.requests import get_topic, get_question, get_questions

user = Router()

class Process(StatesGroup):
    name = State()
    group = State()
    age = State()
    topic_id = State()
    testing = State()
    
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
    await message.answer('Выберите какой тест хотите пройти', reply_markup=await all_topics())
    await state.clear()
    
@user.callback_query(F.data.startswith('topic_'))
async def start_test(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Process.topic_id)
    await callback.answer('Вы выбрали тему')
    topic = await get_topic(callback.data.split('_')[1])
    await state.update_data(topic_id=topic)
    questions = await get_questions(callback.data.split('_')[1])
    for question in questions:
        await callback.message.answer(f'{question.text}', reply_markup=await kb.answer())