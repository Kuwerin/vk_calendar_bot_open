from enum import Enum

# Моды подключаются через /


class Mode(Enum):
    default = ["Обо мне", "default"]
    sign = ["Запись", "sign"]
    get_ans = ["Режим ввода ответа", "getans"]
    date_selection = ["Режим выбора даты"]
    date_selection_number = ["Режим выбора числа для записи"]
    time_selection = ["Режим выбора времени"]
    write_mode = ["Режим записи процедур"]
