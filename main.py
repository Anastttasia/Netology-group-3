import gspread
from google.oauth2.service_account import Credentials
from db.schedule_db import ScheduleDB
import telebot
import sqlite3
from datetime import datetime, timedelta, date
import time
import re

table_name = "Netology"
schedule = ScheduleDB()
schedule.createNewGroup(table_name)
schedule.clearData(table_name)
def authenticate_sheets():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets"
    ]
    creds = Credentials.from_service_account_file("mypython-414513-94cec7c6b257.json", scopes=scopes)
    client = gspread.authorize(creds)
    return client


def read_sheet(client, sheet_id, sheet_name):
    sheet = client.open_by_key(sheet_id)
    worksheet = sheet.worksheet(sheet_name)
    data = worksheet.get_all_values()  # Получает весь лист целиком, игнорируя пустые строки и столбцы
    return data


def get_sheets(client, sheet_id):
    sheet = client.open_by_key(sheet_id)
    worksheets = sheet.worksheets()
    return worksheets


def fill_dates(schedule, start_date):
    current_date = datetime.strptime(start_date, "%d-%m-%Y")
    previous_date = current_date.strftime("%d-%m-%Y")

    for entry in schedule:
        if len(entry) > 0 and entry[0]:  # Если первая ячейка не пустая, это новый день
            current_date = current_date + timedelta(days=1)
            entry[0] = current_date.strftime("%d-%m-%Y")
            previous_date = entry[0]
        elif len(entry) > 0:  # Если первая ячейка пустая, используем предыдущую дату
            entry[0] = previous_date

    return schedule


def process_sheets(sheet_id):
    client = authenticate_sheets()
    worksheets = get_sheets(client, sheet_id)

    date_pattern = re.compile(r'\d{2}-\d{2}-\d{4}')
    monday_sheets = []

    for worksheet in worksheets:
        sheet_name = worksheet.title
        if date_pattern.match(sheet_name):
            sheet_date = datetime.strptime(sheet_name, '%d-%m-%Y')
            if sheet_date.weekday() == 0:  # Проверка на понедельник
                monday_sheets.append((sheet_date, sheet_name))

    monday_sheets.sort()

    for sheet_date, sheet_name in monday_sheets:
        data = read_sheet(client, sheet_id, sheet_name)
        if data:
            print(f"Data from sheet {sheet_name}:")
            filtered_data = [row for row in data[1:] if any(cell.strip() for cell in row)]  # Пропускаем первую строку

            start_date = sheet_name  # Используем название листа как стартовую дату
            filled_data = fill_dates(filtered_data, start_date)
            for row in filled_data:
                schedule.insertData(table_name, row[0], row[1], row[2], row[3], int(row[4]), row[5], row[6])

        '''if current_date.weekday() == 6:  #если текущая дата = воскресенью (6 - воскресенье)
            next_monday_date = current_date + timedelta(days=(7 - current_date.weekday())) #мы вычисляем сколько дней до следующего понедельника, 7 - номер текущей даты и определяем следующую дату понедельника
            if sheet_date == next_monday_date: #если дата листа равна дате понедельника то добавляем условие
                data = read_sheet(client, sheet_id, sheet_name)
                print(data)

                #переместить
                if data:
                    pass'''


'''scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]


creds = Credentials.from_service_account_file("mypython-414513-94cec7c6b257.json", scopes=scopes)
client = gspread.authorize(creds)

sheet_id = "1MRXzlw20uGOOkX-0zNXOS9zuWvuORoSVk5ouAq05Tls" #ссылка на гугл таблицу
sheet = client.open_by_key(sheet_id)'''


'''print("Before exec")
print(schedule.getDataByDate(table_name, '15-04-2024'))'''
'''while True:
    values_list = sheet.sheet1.row_values(counter)
    if (values_list == []):
        break
    # self, tableName, date, timeLesson, subjectName, subgroupNumber, teacherName, linkLesson
    schedule.insertData(table_name, values_list[0], values_list[1], values_list[2], int(values_list[3]), values_list[4], values_list[5])
    #print(values_list)
    counter += 1'''

'''print("After exec")
print(schedule.getDataByDate(table_name, '15-04-2024'))'''


# Токен вашего бота
BOT_TOKEN = "6324418773:AAGqLSzRvKJzSbO721xM2CS9O0TL1t5BrBc"

# Название базы данных
DATABASE_NAME = "message.db"
DATABASE_SCHEDULE = "schedule.db"

bot = telebot.TeleBot(BOT_TOKEN)

def get_all_user_ids():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT id FROM message")
    user_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return user_ids

def get_schedule_scheduleDb(day_of_week):
    conn = sqlite3.connect(DATABASE_SCHEDULE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Netology WHERE date = ?", (day_of_week,))
    schedule_data = cursor.fetchall()
    conn.close()
    return schedule_data

def send_schedule_to_users():
    days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    today = days_of_week[datetime.today().weekday()]

    schedule_data = get_schedule_scheduleDb(today)

    if schedule_data:
        schedule_text = "Привет, твое расписание на сегодня:\n"
        for row in schedule_data:
            schedule_text += f"Day: {row[1]}\nTime: {row[2]}\nSubject: {row[3]}\nSubgroup: {row[4]}\nTeacher: {row[5]}\nLink: {row[6]}\n\n"
        for user_id in get_all_user_ids():
            try:
                bot.send_message(user_id, schedule_text)
                print(f"Расписание отправлено пользователю {user_id}")
            except telebot.apihelper.ApiException as e:
                print(f"Ошибка при отправке расписания пользователю {user_id}: {e}")
    else:
        print("На сегодня расписание отсутствует.")

# Обработка команды /start
@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, "Привет! 👋  Я бот, который может отправлять вам расписание.", reply_markup=generate_menu())

# Обработка команды /subscribe
@bot.message_handler(func=lambda message: message.text == "Подписаться на рассылку")
def subscribe_handler(message):
    bot.send_message(message.chat.id, "К какой группе вы относитесь?", reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, handle_group_response)

def handle_group_response(msg):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    user_id = msg.chat.id
    group_name = msg.text
    cursor.execute("INSERT INTO message (id, name) VALUES (?, ?)", (user_id, group_name))
    conn.commit()
    conn.close()
    bot.send_message(msg.chat.id, "Вы успешно подписались на рассылку! 🎉", reply_markup=generate_menu())

# Обработка команды /show_schedule
@bot.message_handler(func=lambda message: message.text == "Показать расписание")
def show_schedule_handler(message):
    days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    today = days_of_week[datetime.today().weekday()]

    schedule_data = get_schedule_scheduleDb(today)

    if schedule_data:
        schedule_text = "Привет, твое расписание на сегодня:\n"
        for row in schedule_data:
            schedule_text += f"День: {row[1]}\nВремя: {row[2]}\nПредмет: {row[3]}\nОписание: {row[4]}\nГруппа: {row[5]}\nПреподаватель: {row[6]}\nСсылка: {row[7]}\n\n"
        m = schedule_text
        if len(m) > 4095:
            for x in range(0, len(m), 4095):
                bot.reply_to(message, text=m[x:x + 4095])
        else:
            bot.reply_to(message, text=m)
    else:
        bot.send_message(message.chat.id, "На сегодня расписание отсутствует. 🤔", reply_markup=generate_menu())

# Обработка команды /help
@bot.message_handler(func=lambda message: message.text == "Помощь")
def help_handler(message):
    bot.send_message(message.chat.id, "Я могу отправлять вам расписание каждый день в 9:00 утра.\n\nВы можете подписаться на рассылку, чтобы получать расписание, или просто посмотреть его прямо сейчас.\n\nИспользуйте кнопки ниже для взаимодействия со мной.", reply_markup=generate_menu())

def generate_menu():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Подписаться на рассылку", "Показать расписание")
    keyboard.row("Помощь")
    return keyboard

def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(1)


conn = sqlite3.connect("message.db")

# Создаем курсор
cursor = conn.cursor()

# Создаем таблицу

cursor.execute("CREATE TABLE IF NOT EXISTS message (id INTEGER PRIMARY KEY, name TEXT)")

# Сохраняем изменения
conn.commit()

# Закрываем соединение
conn.close()


# Запускаем функцию рассылки
if __name__ == "__main__":
    generate_menu()
    bot.polling()
    sheet_id = "1MRXzlw20uGOOkX-0zNXOS9zuWvuORoSVk5ouAq05Tls"
    process_sheets(sheet_id)


