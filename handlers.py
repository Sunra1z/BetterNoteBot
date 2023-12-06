

import asyncio

import pytz

from keyboards import main_kb
from aiogram import Router, F
from database.requests import get_notes
from datetime import datetime
from pytz import timezone as tz

from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from database.models import store_note

router = Router() # Router for message handlers, used to create main functions in different files, and not in one big file


class WaitingForNoteText(StatesGroup): # States for creating notes
    typing_note = State()
    type_reminder = State()
    gpt_thinker = State() # nvm I can't name things properly
    note_storage = State()


@router.message(CommandStart()) # Handler for /start command
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
    await message.answer('Введи время напоминания в формате ДД-ММ-ГГГГ ЧЧ:ММ')
    await state.set_state(WaitingForNoteText.gpt_thinker) # Setting state as WAITING for reminder
    await state.update_data(note_text=note_text) # Updating data for reminder

@router.message(WaitingForNoteText.gpt_thinker) # Handler for remind time STEP 3 FOR STATES
async def gpt_think(message: Message, state: FSMContext):
    reminder_time_str = message.text
    note_text = await state.get_data()
    try:
        reminder_time = datetime.strptime(reminder_time_str, "%d-%m-%Y %H:%M") #TODO: Add timezone adaptation for reminder system (shit works only in KZ lmao)
    except ValueError: # Error handler for invalid date format
        await message.answer("Неверный формат даты! Введите дату в формате ДД-ММ-ГГГГ ЧЧ:ММ")
        return
    reminder_time = reminder_time.astimezone(pytz.UTC)
    print(reminder_time)
    utcNow = datetime.now()
    utcNow = utcNow.astimezone(pytz.UTC)
    print(utcNow)
    utcNow = utcNow.replace(tzinfo=tz('UTC'))
    print(utcNow)
    delay = (reminder_time - utcNow).total_seconds()
    if delay < 0: # Error handler for a past date input
        await message.answer("Время напоминания уже прошло! Введите другое!")
        await state.set_state(WaitingForNoteText.gpt_thinker)
    else:
        await message.answer("Будет сделано! Напомню вам в" + ' ' + reminder_time_str)
        user_id = message.from_user.id
        await store_note(user_id, note_text['note_text'], reminder_time) # Saving correct note data to a DB
        await state.clear() # Clearing state to let user use other commands
        rmndr = asyncio.create_task(delay_counter(delay)) # Creating asynchronous task for reminder system (Helps with multitasking!)
        await rmndr
        await message.answer("Напоминаю!" + ' ' + note_text['note_text'])
@router.message(F.text.lower() == 'посмотреть заметки') # Handler for getting all notes sorted by user ID
async def notesShow(message: Message): # Func to retrieve and show all notes from DB by user ID (used only for debugging lol)
    notes = await get_notes(message.from_user.id)
    if notes:
        for note in notes:
            await message.answer(note.text)
    else:
        await message.answer("У вас нет заметок!")

@router.message(F.text.lower() == 'заметки на сегодня') # Func to retrieve and show all today notes from DB by user ID
async def todayNotesShow(message: Message):
    notes = await get_notes(message.from_user.id)
    if notes:
        for note in notes:
            if note.reminder_time.date() == datetime.utcnow().date(): # Sorting notes only by date, regardless of time
                await message.answer(note.text + ' ' + note.reminder_time.strftime('%H:%M')) # Showing only time and text of a note
    else:
        await message.answer("На сегодня нет заметок!")


async def delay_counter(delay): # That is a reminder system, it works by delaying a message for a certain amount of time (Works asynchronously tho!)
    if delay > 0:
        await asyncio.sleep(delay)
