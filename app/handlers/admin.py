from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart, Filter, Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from app.database import requests as rq
from app import keyboards as kb

admin = Router()

class Answer(StatesGroup):
    answer= State()

class Admin(Filter):
    def __init__(self):
        self.admins = [452091758, 479964432]
    
    async def __call__(self, message: Message):
        return message.from_user.id in self.admins
    
@admin.message(Admin(), Command('users'))
async def get_users(message: Message):
    await message.answer('Список зарегистрированных пользователей', reply_markup= await kb.all_users())


@admin.message(Admin(), Command('results'))
async def results(message: Message):
    await message.answer('Список всех результатов')
