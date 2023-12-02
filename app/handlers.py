import aiogram.types
import datetime
import asyncio

from aiogram import Router, F
from aiogram.client import bot
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from app.database.models import store_note

router = Router()

class WaitingForNoteText(StatesGroup): # States for creating notes
    typing_note = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Добро пожаловать!')
    await message.answer('Я бот который поможет тебе делать заметки!')
    await message.answer('Для того чтобы создать заметку введи /new_note')
    await message.answer('Автор ленивый и пока нихуя не работает но скоро будет работать!')

@router.message(F.text == '/new_note') # Handler for creating notes STEP 1 FOR STATES
async def start_note(message: Message, state: FSMContext):
    await message.answer('Введи текст заметки')
    await state.set_state(WaitingForNoteText.typing_note) # Setting state as WAITING

@router.message(WaitingForNoteText.typing_note) # Handler for creating notes STEP 2 FOR STATES
async def end_note(message: Message, state: FSMContext):
    note_text = message.text
    tg_id = message.from_user.id
    await store_note(tg_id, note_text)
    await message.answer('Заметка сохранена!')
    await state.clear() # Clearing state

async def reminder(tg_id, note_text, reminder_time):
    await asyncio.sleep((reminder_time - datetime.now()).total_seconds())
    await bot.send_message(tg_id, f'Напоминаю, что вы должны {note_text}!')