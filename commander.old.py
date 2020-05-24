# Всякие бесполезные методы из класса коммандер
#

def change_mode(self, to_mode):
    """
    Меняет режим приема команд
    :param to_mode: Измененный мод
    """
    # self.last_ans = msg
    self.last_mode = self.now_mode
    self.now_mode = to_mode


#   self.last_ans = None

def input(self, msg):
    """
    Функция принимающая сообщения пользователя
    :param msg: Сообщение
    :return: Ответ пользователю, отправившему сообщение
    """

    # Режим получения ответа
    if self.now_mode == Mode.get_ans:
        self.last_ans = msg
        self.now_mode = self.last_mode
        return "Ok!"

    if self.now_mode == Mode.default:
        """
        Запись
        Обо мне Вопрос-ответ
        """
        if msg in Command.sign.value:
            self.last_ans = msg
            self.last_mode = self.now_mode
            self.now_mode = Mode.write_mode
            return "Выберите процедуру:"
        if msg in Command.description.value:
            return "Место для описания процедур и фотографии"
        if msg in Command.questions.value:
            return "Раздел Вопрос-Ответ"
        else:
            return "Мимо"
    """
    Перечислены процедуры
    """

    if msg in Command.save_and_choose.value:
        self.last_ans = msg
        self.now_mode = Mode.date_selection
    """
    Выбор процедур
    """

    while msg in Command.procedures.value:
        self.now_mode = Mode.write_mode
        self.last_ans = msg
        self.procedures_list.append(msg)
        return self.procedures_list
    """
    Выбор даты
    """
    if self.now_mode == Mode.date_selection:
        if msg in Command.twelve_months.value:
            self.last_ans = msg
            self.procedure_date += months_digits[self.last_ans]
            self.now_mode = Mode.date_selection_number
            return "Окей, вы выбрали", self.last_ans
        else:
            return "Пожалуйста, выберите месяц"

    if self.now_mode == Mode.date_selection_number:
        if msg in Command.month_days.value:
            self.last_ans = msg
            self.procedure_date += self.last_ans
            self.last_mode = self.now_mode
            self.now_mode = Mode.time_selection
            return "Вы выбрали число:", self.last_ans
        else:
            return "Хуйню порешь"

    if self.now_mode == Mode.time_selection:
        """
        Подсчет длительности процедуры
        """
        self.last_ans = msg
        for procedure in self.procedures_list:
            self.duration += procedures_and_duration[procedure]
        if msg in Command.time_vacant.value:
            self.last_ans = msg
            self.procedure_time = time_into_google[self.last_ans]
            self.now_mode = Mode.default
            self.procedure_date += self.procedure_time
            self.start_time = datetime.datetime.strptime(self.procedure_date, "%Y-%m-%dT%H:%M:%S")
            self.duration = timedelta(minutes=self.duration)
            self.end_time = self.start_time + self.duration
            self.start_time.isoformat()  # попробовать! Вроде бы это как раз тот формат, что нам нужен!
            print(self.start_time)
            print(self.end_time)
            return "Вы выбрали время ", self.last_ans
        else:
            return "Хуйню написал"
