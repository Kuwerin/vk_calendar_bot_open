# Перечисления команд, режимов
from command_enum import Command
# from mode_enum import Mode
from command_enum import time_into_google
from command_enum import procedures_and_duration
from command_enum import procedures_and_prices
from command_enum import months_digits
from command_enum import month_days_into_int
from command_enum import faq_dict
from command_enum import procedures_describe
import datetime
from datetime import timedelta
from calendar_vk import check_date
from calendar_vk import check_time


class Commander:

    def __init__(self):
        """
        Переводим получение времени на datetime

        """
        # Текущий, предыдущий режимы
        self.username = ""
        self.full_name = ""
        self.client_id = 0
        self.procedures_list = []  # Вот тут!
        self.summary = ""  # Здесь хранится саммари для событий календаря, но в форме строки
        #        self.description = "" # Здесь хранится описание для событий календаря в форме строки
        self.procedure_date = 0
        self.month = 0
        self.day = 0
        self.procedure_time = 0
        self.start_time = 0
        self.end_time = 0
        self.duration = 0
        self.duration_dt = 0
        self.cost = 0
        self.expire_time = datetime.datetime(1970, 1, 1, 0, 0, 0)  # Время для сравнения. Присваивается новое значение
        # после записи. Сравнивается с дельтой времени = 24 часа, чтобы избежать флуд-атаки
        # Для запоминания ответов пользователя
        self.last_ans = None
        self.last_kbd = ""

    def input_handler(self, msg):
        while msg in Command.procedures.value:
            response = "Вы выбрали следующие процедуры:\n\n"
            counter = 1  # -  добавить для нумерации списка процедур
            self.last_ans = msg
            self.procedures_list.append(msg)
            for procedure in self.procedures_list:
                response += str(counter) + ")\t" + procedure + " \n"
                counter += 1
            if self.procedures_list.__len__() >= 6:
                self.procedures_list = []
                counter = 1
                return "Можно записаться не более чем на 5 процедур, попробуйте еще раз"
            return response
        if msg == "Сохранить и выбрать дату":
            if self.procedures_list.__len__() == 0:
                return "Вы не выбрали ни одной процедуры!"
            elif self.procedures_list.__len__() > 0:
                response = ("Вы выбрали " + str(
                    self.procedures_list.__len__()) + " процедур(ы). \n\nПерейдем к выбору даты. Для начала, пожалуйста, выберите месяц")
                return response

        if msg in Command.twelve_months.value:
            response = ""
            self.last_ans = msg
            self.month = months_digits[self.last_ans]
            if "days" in self.check_month(self.last_ans):
                self.procedure_date = datetime.datetime(2020, self.month, 1)
                response = ("Окей, вы выбрали " + self.last_ans)
            elif self.check_month(self.last_ans) == "months":
                response = "Извините, нельзя записаться на прошедшую дату.\n\n" \
                           "Пожалуйста, выберите дату"
            return response

        if msg in Command.month_days.value:
            """Здесь мы получаем self.day и проверяем его, выводим стоимость"""
            self.last_ans = msg
            self.day = month_days_into_int[self.last_ans]
            if "days" in self.check_day(self.day):
                return "Извините, нельзя выбрать день, который уже прошел"
            elif self.check_day(self.day) == "time":
                self.procedure_date = datetime.datetime(2020, self.month, self.day)
                for procedure in self.procedures_list:
                    self.duration += procedures_and_duration[procedure]
                    self.cost += procedures_and_prices[procedure]
                duration = timedelta(minutes=self.duration)
                response = ("На " + self.last_ans + " число у Оксаны " + check_date(self.procedure_date) +
                            "\nВаши процедуры займут " + str(duration)[:-6] + " час(а) "
                            + str(duration)[-5:-3] + " минут, \n"
                            + "Приблизительная стоимость: " + str(self.cost) + " рублей"
                            + "\nПожалуйста, выберите время")
                return response
        if msg in Command.time_vacant.value:
            self.last_ans = msg
            self.procedure_time = time_into_google[self.last_ans]
            self.procedure_date = datetime.datetime(2020, self.month, self.day, self.procedure_time)
            self.duration_dt = timedelta(minutes=self.duration)
            self.end_time = self.procedure_date + self.duration_dt
            self.summary = str(self.procedures_list)
            self.summary = "● " + self.summary.replace("', '", "\n●  ").replace("[", "").replace("]",
                                                                                                 "").replace(
                "'", "")
            text = str(self.procedures_list)
            response = (self.username +
                        ", подтвердите, пожалуйста:\n" +
                        "Вы выбрали процедуры:\n" +
                        "\n● " +
                        text.replace("', '", "\n● ").replace("[", "").replace("]", "").replace("'", "") +
                        "\n\nПриблизительная стоимость " +
                        str(self.cost) +
                        " рублей"
                        "\nПроцедуры займут " +
                        str(self.duration)[:-6] +
                        " час(а) " +
                        str(self.duration)[-5:-3] +
                        " минут, \n" +
                        "С " +
                        str(self.procedure_date)[-8:-3] +
                        " до " +
                        str(self.end_time)[-8:-3]
                        )
            return response

    def antiflood_response(self):
        if (datetime.datetime.now() - self.expire_time).days <= 1:
            response = (self.username + ", к сожалению, нельзя записываться чаще одного раза в сутки!")
            return response
        elif (datetime.datetime.now() - self.expire_time).days > 1:
            response = (self.username + ", пожалуйста, выберите сразу все процедуры, на которые хотите записаться.")
            return response

    def antiflood_kbd(self):
        if (datetime.datetime.now() - self.expire_time).days <= 1:
            return "default"
        elif (datetime.datetime.now() - self.expire_time).days > 1:
            return "procedures"

    def sign_kbd(self):
        """
        Если количество процедур == 0,
        то клавиатура не переключается,
        иначе - переключается на клавиатуру с месяцами

        """
        if self.procedures_list.__len__() == 0:
            return "procedures"
        elif self.procedures_list.__len__() > 0:
            return "months"

    def check_month(self, msg):
        """
        Проверяет, прошел ли уже названный месяц
        Исходим из теории, что записаться на уже прошедшее время нельзя
        """
        now = datetime.date.today()
        if msg in Command.long_months.value:
            if months_digits[msg] >= now.month:
                self.last_kbd = "days31"
                return "days31"
            elif months_digits[msg] < now.month:
                return "months"
        elif msg in Command.short_months.value:
            if months_digits[msg] >= now.month:
                self.last_kbd = "days30"
                return "days30"
            elif months_digits[msg] < now.month:
                return "months"
        elif msg == "Февраль":
            if months_digits[msg] >= now.month:
                self.last_kbd = "days28"
                return "days28"
            elif months_digits[msg] < now.month:
                return "months"

    def check_day(self, msg):

        now = datetime.date.today()
        if self.month > now.month:
            return "time"
        elif self.day >= now.day:
            return "time"
        elif self.day < now.day:
            return self.last_kbd
        elif self.month < now.month:
            return self.last_kbd

    def final_kbd(self, msg):
        """
        Последняя клавиатура посылается в зависимости от свободности времени
        """
        self.last_ans = msg
        self.procedure_time = time_into_google[self.last_ans]
        self.procedure_date = datetime.datetime(2020, self.month, self.day, self.procedure_time)
        self.duration_dt = timedelta(minutes=self.duration)
        self.end_time = self.procedure_date + self.duration_dt
        response = check_time(self.procedure_date, self.end_time)
        #        if response == "time":
        # self.start_time = 0
        # self.end_time = 0
        # self.duration = 0
        # for procedure in self.procedures_list:
        # self.duration += procedures_and_duration[procedure]
        return response

    def antiflood_timer_start(self):
        self.expire_time = datetime.datetime.now()

    def make_description(self):
        response = "Имя: " + self.full_name + \
                   "\nСсылка на профиль: http://vk.com/id" + str(self.client_id) + \
                   "\nНаписать человеку: http://vk.com/im?sel=" + str(self.client_id)
        return response

    def clear_input(self):
        self.client_id = 0
        self.procedures_list = []  # Вот тут!
        self.summary = ""  # Здесь хранится саммари для событий календаря, но в форме строки
        self.procedure_date = 0
        self.month = 0
        self.day = 0
        self.procedure_time = 0
        self.start_time = 0
        self.end_time = 0
        self.duration = 0
        self.duration_dt = 0
        self.cost = 0
        # после записи. Сравнивается с дельтой времени = 24 часа, чтобы избежать флуд-атаки
        # Для запоминания ответов пользователя
        self.last_ans = None
        self.last_kbd = ""

    def description_handler(self, msg):
        if msg == "Об услугах":
            response = (self.username + ", пожалуйста, нажмите на интересующую Вас процедуру, "
                                        "чтобы узнать о ней подробнее.")
            return response
        if msg == "Частые вопросы":
            response = (self.username + ", выберите вопрос из числа популярных")
            return response

        if msg in procedures_describe:
            response = self.open_about(procedures_describe[msg])
            return response
        if msg in faq_dict:
            response = self.open_faq(faq_dict[msg])
            return response

    def open_about(self, name):
        file_name = ("procedures/" + name)
        file = open(file_name, "r", encoding="UTF-8").read()
        return file

    def open_faq(self, name):
        file_name = ("faq/" + name)
        file = open(file_name, "r", encoding="UTF-8").read()
        return file


