import aiogram.types
import datetime
import asyncio
import pprint
import json

from aiogram.client import bot

import app.handlers
import openai

from app.keyboards import main_kb
from config import OpenAiKey
from aiogram import Router, F, Bot
from app.database.requests import get_notes

from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from app.database.models import store_note

openai.api_key = OpenAiKey
router = Router()


class WaitingForNoteText(StatesGroup): # States for creating notes
    typing_note = State()
    type_reminder = State()
    gpt_thinker = State()
    note_storage = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Добро пожаловать!')
    await message.answer('Я бот который поможет тебе делать заметки!', reply_markup=main_kb)

@router.message(F.text.lower() == 'создать заметку') # Handler for creating notes STEP 1 FOR STATES
async def start_note(message: Message, state: FSMContext):
    await message.answer('Введите текст заметки')
    await state.set_state(WaitingForNoteText.typing_note) # Setting state as WAITING

@router.message(WaitingForNoteText.typing_note) # Handler for creating notes STEP 2 FOR STATES
async def end_note(message: Message, state: FSMContext):
    note_text = message.text
    await message.answer('Заметка сохранена!')
    await message.answer('Введи время напоминания в формате ДД/ММ/ГГГГ ЧЧ:ММ')
    await state.set_state(WaitingForNoteText.gpt_thinker) # Setting state as WAITING for reminder
    await state.update_data(note_text=note_text) # Updating data for reminder

@router.message(WaitingForNoteText.gpt_thinker)
async def gpt_think(message: Message, state: FSMContext):
    reminder_time_str = message.text
    try:
        reminder_time = datetime.datetime.strptime(reminder_time_str, "%d/%m/%Y %H:%M") #TODO: Add timezone adaptation for reminder system (shit works only in KZ lmao)
    except ValueError:
        await message.answer("Неверный формат даты! Введите дату в формате ДД/ММ/ГГГГ ЧЧ:ММ")
        return
    await message.answer("Будет сделано! Напомню вам в" + ' ' + reminder_time_str)
    await state.update_data(reminder_time=reminder_time) # Passing reminder time
    await state.set_state(WaitingForNoteText.type_reminder)


@router.message(WaitingForNoteText.type_reminder) #TODO: Fix a bug: can't use commands like today notes or show notes when delay is set
async def delay_counter(message: Message, state: FSMContext):
    note_text = await state.get_data()
    reminder_time = await state.get_data()
    user_id = message.from_user.id
    await store_note(user_id, note_text['note_text'], reminder_time['reminder_time'])
    delay = (reminder_time['reminder_time'] - datetime.datetime.now()).total_seconds()
    print(note_text['note_text'])
    if delay > 0:
        await asyncio.sleep(delay)
        await message.answer("Напоминаю!" + ' ' + note_text['note_text'])
    else:
        await message.answer("Время напоминания уже прошло! Введите другое время напоминания!")
        await state.set_state(WaitingForNoteText.gpt_thinker)
@router.message(F.text.lower() == 'посмотреть заметки') # Handler for getting all notes sorted by user ID
async def notesShow(message: Message):
    notes = await get_notes(message.from_user.id)
    if notes:
        for note in notes:
            await message.answer(note.text)
    else:
        await message.answer("У вас нет заметок!")

@router.message(F.text.lower() == 'сегодняшние заметки') # Handler for getting all notes sorted by time
async def today_notes(message: Message, state: FSMContext):
    notes = await get_notes(message.from_user.id)
    if notes:
        for note in notes:
            if note.reminder_time.date() == datetime.datetime.now().date():
                await message.answer(note.text)
    else:
        await message.answer("У вас нет заметок на сегодня!")

# @router.message(F.text.lower() == 'отмена') # TODO: Cancel any operation with bot and return to the start
# async def cancel(message: Message, state: FSMContext):
#     await message.answer('Отменено!')
#     await state.clear() # Clearing state



