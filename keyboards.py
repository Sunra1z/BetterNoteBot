from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='📝 Создать заметку')],
    [KeyboardButton(text='🗑️ Удалить заметку')],
    [KeyboardButton(text='✉️ История заметок')],
    [KeyboardButton(text='🔍 Поиск заметок')],
    [KeyboardButton(text='📆 Заметки на сегодня')],
    [KeyboardButton(text='🚫 Отмена')]
],
resize_keyboard=True,
one_time_keyboard=False,
input_field_placeholder='Выберите действие'
)


