WORKOUTS = {}

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def generate_workouts():
    for day in range(1, 121):
        WORKOUTS[day] = {}
        for level in ["Easy", "Medium", "Hard"]:
            WORKOUTS[day][level] = [f"Вправа {i+1} - рівень {level}" for i in range(6)]

def build_day_keyboard(page: int) -> InlineKeyboardMarkup:
    keyboard = []
    days_per_page = 25
    start_day = (page - 1) * days_per_page + 1
    end_day = min(page * days_per_page, 120)
    row = []
    for day_num in range(start_day, end_day + 1):
        row.append(InlineKeyboardButton(str(day_num), callback_data=f"day_{day_num}"))
        if len(row) == 5:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    navigation_row = []
    if page > 1:
        navigation_row.append(InlineKeyboardButton("⬅️ Попередня", callback_data=f"page_{page - 1}"))
    if page * days_per_page < 120:
        navigation_row.append(InlineKeyboardButton("Наступна ➡️", callback_data=f"page_{page + 1}"))
    if navigation_row:
        keyboard.append(navigation_row)
    return InlineKeyboardMarkup(keyboard)

def build_difficulty_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Легкий (Easy)", callback_data="difficulty_Easy")],
        [InlineKeyboardButton("Середній (Medium)", callback_data="difficulty_Medium")],
        [InlineKeyboardButton("Важкий (Hard)", callback_data="difficulty_Hard")]
    ])
