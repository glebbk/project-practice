import telebot
from telebot import types
import datetime

bot = telebot.TeleBot('7852694693:AAFiVgktRJT935uTNxwJi2Lr6J8oNAYMDUs')

GROUPS = {
    "ИБ-21": ["Александров", "Борисова", "Васильев", "Григорьева"],
    "ИТ-22": ["Дмитриев", "Егоров", "Жукова"],
    "РПО-23": ["Зайцева", "Иванов", "Кузнецов"]
}

SCHEDULE = {
    "ИБ-21": {
        "Понедельник": [
            {"time": "9:00", "subject": "Криптография", "room": "101", "teacher": "Смирнов А.А."},
            {"time": "11:00", "subject": "Сетевые технологии", "room": "205", "teacher": "Петров П.П."}
        ],
        "Вторник": [
            {"time": "10:00", "subject": "Базы данных", "room": "310", "teacher": "Иванова И.И."}
        ]
    },
    "ИТ-22": {
        "Понедельник": [
            {"time": "13:00", "subject": "Программирование", "room": "412", "teacher": "Козлов К.К."}
        ]
    }
}

TEACHERS = {
    "Смирнов А.А.": {
        "subjects": ["Криптография", "Информационная безопасность"],
        "contacts": "smirnov@mospolytech.ru"
    },
    "Петров П.П.": {
        "subjects": ["Сетевые технологии"],
        "contacts": "petrov@mospolytech.ru"
    }
}

SESSION_REQUIREMENTS = {
    "Криптография": [
        "Защита лабораторных работ (все 10)",
        "Теоретический экзамен",
        "Допуск от преподавателя"
    ],
    "Программирование": [
        "Защита курсового проекта",
        "Практический экзамен"
    ]
}

# Переменная для хранения выбранной группы (в памяти)
user_data = {}


# Главное меню
def main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('👥 Моя группа')
    btn2 = types.KeyboardButton('📅 Расписание')
    btn3 = types.KeyboardButton('📚 Сессия')
    btn4 = types.KeyboardButton('👨‍🏫 Преподаватели')
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(chat_id, "Выберите раздел:", reply_markup=markup)


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for group in GROUPS.keys():
        markup.add(types.KeyboardButton(group))

    bot.send_message(message.chat.id,
                     "Привет! Я бот-помощник для студентов МосПолитеха.\n"
                     "Выбери свою учебную группу:",
                     reply_markup=markup)


# Обработчик выбора группы
@bot.message_handler(func=lambda message: message.text in GROUPS.keys())
def set_group(message):
    user_data[message.chat.id] = {"group": message.text}
    bot.send_message(message.chat.id, f"Группа {message.text} сохранена!")
    main_menu(message.chat.id)


# Обработчик кнопки "Моя группа"
@bot.message_handler(func=lambda message: message.text == '👥 Моя группа')
def show_group(message):
    if message.chat.id in user_data:
        group = user_data[message.chat.id]["group"]
        students = "\n".join(GROUPS[group])
        bot.send_message(message.chat.id,
                         f"Группа: {group}\n\nСтуденты:\n{students}")
    else:
        bot.send_message(message.chat.id, "Группа не выбрана! Нажмите /start")


# Обработчик кнопки "Расписание"
@bot.message_handler(func=lambda message: message.text == '📅 Расписание')
def schedule_menu(message):
    if message.chat.id not in user_data:
        bot.send_message(message.chat.id, "Сначала выберите группу!")
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("На сегодня", callback_data="schedule_today"))
    markup.add(types.InlineKeyboardButton("На неделю", callback_data="schedule_week"))
    markup.add(types.InlineKeyboardButton("На завтра", callback_data="schedule_tomorrow"))

    bot.send_message(message.chat.id, "Выберите период:", reply_markup=markup)


# Обработчик расписания
@bot.callback_query_handler(func=lambda call: call.data.startswith('schedule_'))
def handle_schedule(call):
    if call.message.chat.id not in user_data:
        bot.answer_callback_query(call.id, "Сначала выберите группу!")
        return

    group = user_data[call.message.chat.id]["group"]
    day = datetime.datetime.now().strftime("%A")

    if call.data == "schedule_today":
        schedule = SCHEDULE[group].get(day, [])
        text = f"📅 Расписание на сегодня ({day}):\n\n"
        for lesson in schedule:
            text += f"⏰ {lesson['time']} - {lesson['subject']}\n"
            text += f"🏫 Аудитория: {lesson['room']}\n"
            text += f"👨‍🏫 Преподаватель: {lesson['teacher']}\n\n"

        if not schedule:
            text = "Сегодня пар нет! Отдыхайте 😊"

    elif call.data == "schedule_week":
        text = f"📅 Расписание группы {group} на неделю:\n\n"
        for day, lessons in SCHEDULE[group].items():
            text += f"📌 {day}:\n"
            for lesson in lessons:
                text += f"⏰ {lesson['time']} - {lesson['subject']}\n"
            text += "\n"

    elif call.data == "schedule_tomorrow":
        text = "Функция 'На завтра' в разработке 🛠"

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id)


# Обработчик кнопки "Сессия"
@bot.message_handler(func=lambda message: message.text == '📚 Сессия')
def session_menu(message):
    markup = types.InlineKeyboardMarkup()
    for subject in SESSION_REQUIREMENTS.keys():
        markup.add(types.InlineKeyboardButton(subject, callback_data=f"session_{subject}"))

    bot.send_message(message.chat.id, "Выберите предмет:", reply_markup=markup)


# Обработчик требований сессии
@bot.callback_query_handler(func=lambda call: call.data.startswith('session_'))
def handle_session(call):
    subject = call.data.split('_')[1]
    requirements = SESSION_REQUIREMENTS[subject]

    text = f"📚 Требования по предмету {subject}:\n\n"
    for i, req in enumerate(requirements, 1):
        text += f"{i}. {req}\n"

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id)


# Обработчик кнопки "Преподаватели"
@bot.message_handler(func=lambda message: message.text == '👨‍🏫 Преподаватели')
def teachers_menu(message):
    markup = types.InlineKeyboardMarkup()
    for teacher in TEACHERS.keys():
        markup.add(types.InlineKeyboardButton(teacher, callback_data=f"teacher_{teacher}"))

    bot.send_message(message.chat.id, "Выберите преподавателя:", reply_markup=markup)


# Обработчик информации о преподавателе
@bot.callback_query_handler(func=lambda call: call.data.startswith('teacher_'))
def handle_teacher(call):
    teacher = call.data.split('_')[1]
    info = TEACHERS[teacher]

    text = f"👨‍🏫 Преподаватель: {teacher}\n"
    text += f"📧 Контакты: {info['contacts']}\n\n"
    text += "Ведёт предметы:\n"
    for subject in info['subjects']:
        text += f"- {subject}\n"

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id)


# Запуск бота
if __name__ == '__main__':
    print("Бот МосПолитеха запущен!")
    bot.polling(none_stop=True)
