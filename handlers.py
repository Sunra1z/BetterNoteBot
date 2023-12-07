
import asyncio


from keyboards import main_kb
from aiogram import Router, F
from database.requests import get_notes
from datetime import datetime


from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from database.models import store_note

router = Router()  # Router for message handlers, used to create main functions in different files, and not in one big file


class CmdStates(StatesGroup):  # States for creating notes
    user_note_save = State()
    reminder_system = State()  # nvm I can't name things properly
    removing_note = State()

@router.message(CommandStart()) # Handler for /start command
async def cmd_start(message: Message):
    await message.answer('Добро пожаловать!')
    await message.answer('Я бот который поможет тебе делать заметки!', reply_markup=main_kb)

@router.message(F.text == '📝 Создать заметку', StateFilter(None)) # Handler for creating notes STEP 1 FOR STATES
async def start_note(message: Message, state: FSMContext):
    await message.answer('Введите текст заметки')
    await state.set_state(CmdStates.user_note_save) # Setting state as WAITING

@router.message(CmdStates.user_note_save, ~(F.text == '🚫 Отмена')) # Handler for creating notes STEP 2 FOR STATES
async def end_note(message: Message, state: FSMContext):
    await state.update_data(note_text=message.text)
    await message.answer('Заметка сохранена!')
    await message.answer('Введите время напоминания в формате ДД-ММ-ГГГГ ЧЧ:ММ') # TODO: Add a better date input system (like a calendar)
    await state.set_state(CmdStates.reminder_system) # Setting state as WAITING for reminder

@router.message(CmdStates.reminder_system, ~(F.text == '🚫 Отмена')) # Handler for remind time STEP 3 FOR STATES
async def gpt_think(message: Message, state: FSMContext):
    reminder_time_str = message.text
    note_text = await state.get_data()
    try:
        reminder_time = datetime.strptime(reminder_time_str, "%d-%m-%Y %H:%M") #TODO: Add timezone adaptation for reminder system (shit works only in KZ lmao)
    except ValueError: # Error handler for invalid date format
        await message.answer("Неверный формат даты! Введите дату в формате ДД-ММ-ГГГГ ЧЧ:ММ")
        return
    print(reminder_time)
    delay = (reminder_time - datetime.now()).total_seconds()
    if delay < 0: # Error handler for a past date input
        await message.answer("Время напоминания уже прошло! Введите другое!")
        await state.set_state(CmdStates.reminder_system)
    else:
        await message.answer("Будет сделано! Напомню вам в" + ' ' + reminder_time_str)
        user_id = message.from_user.id
        await store_note(user_id, note_text['note_text'], reminder_time) # Saving correct note data to a DB
        await state.clear() # Clearing state to let user use other commands
        rmndr = asyncio.create_task(delay_counter(delay)) # Creating asynchronous task for reminder system (Helps with multitasking!)
        await rmndr
        await message.answer("Напоминаю!" + ' ' + note_text['note_text'])
@router.message(F.text == '✉️ История заметок') # Handler for getting all notes sorted by user ID
async def notesShow(message: Message): # Func to retrieve and show all notes from DB by user ID (used only for debugging lol)
    notes = await get_notes(message.from_user.id)
    if notes:
        notes_text = ""
        for i, note in enumerate(notes):
            notes_text += f"{i+1}. {note.text} {note.reminder_time.strftime('%d-%m-%Y %H:%M')}\n"
        if notes_text:
            await message.answer(notes_text)
        else:
            await message.answer("У вас нет заметок!")


@router.message(F.text == '📆 Заметки на сегодня') # Func to retrieve and show all today notes from DB by user ID
async def todayNotesShow(message: Message):
    notes = await get_notes(message.from_user.id)
    if notes:
        notes_text = ""
        today_notes = [note for note in notes if note.reminder_time.date() == datetime.now().date()]
        for i, note in enumerate(today_notes):
            notes_text += f"{i+1}. {note.text} {note.reminder_time.strftime('%H:%M')}\n"
        if notes_text:
            await message.answer(notes_text)
        else:
            await message.answer("На сегодня нет заметок!")
    else:
        await message.answer("У вас нет заметок!")

async def delay_counter(delay): # That is a reminder system, it works by delaying a message for a certain amount of time (Works asynchronously tho!)
    if delay > 0:
        await asyncio.sleep(delay)

@router.message(Command(commands=["cancel"]))
@router.message(F.text == '🚫 Отмена') # Handler for cancelling a note creation
async def cmd_cancel(message: Message, state: FSMContext):
    await message.answer('Действие отменено!')
    await state.clear()
    await message.answer('Выберите действие', reply_markup=main_kb)

@router.message(F.content_type.in_({'photo', 'video', 'document', 'audio', 'voice', 'sticker', 'video_note', 'location', 'contact'})) # Handler for sending something other than text
async def wrong_input(message: Message):
    await message.answer_sticker(r'CAACAgIAAxkBAAEK6wZlcf_NDJDKNfz0YbNBSJOMxqRtfQACaxUAAm9nyUvmI8GFzuJ1dTME')
    await message.answer('Извините, я не понимаю вас! Выберите действие', reply_markup=main_kb)