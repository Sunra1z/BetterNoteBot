from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Создать заметку')],
    [KeyboardButton(text='Посмотреть заметки')]
])


