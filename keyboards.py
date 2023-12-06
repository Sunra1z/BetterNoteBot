from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Создать заметку')],
    [KeyboardButton(text='Посмотреть заметки')],
    [KeyboardButton(text='Заметки на сегодня')],
],
resize_keyboard=True,
one_time_keyboard=False,
input_field_placeholder='Выберите действие'
)


