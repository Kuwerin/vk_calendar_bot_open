import vk_api
import random
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.bot_longpoll import VkBotEventType
from commander import Commander
from command_enum import Command
from mode_enum import Mode
from calendar_vk import create_event
from calendar_vk import check_time
import json


class Server:
    def __init__(self, api_token, group_id, server_name: str = "Empty"):
        # Даем серверу имя
        self.server_name = server_name

        # Для Long Poll
        self.vk = vk_api.VkApi(token=api_token, api_version=5.89)

        # Для использоания Long Poll API
        self.long_poll = VkBotLongPoll(self.vk, group_id, wait=20)

        # Для вызова методов vk_api
        self.vk_api = self.vk.get_api()
        # Словарь для каждого отдельного пользователя
        self.users = {}
        self.now_kbd = "default"

    def start(self):
        while True:
            try:
                for event in self.long_poll.listen():
                    if event.object.from_id not in self.users:
                        self.users[event.object.from_id] = Commander()
                    elif event.object.from_id in self.users:
                        self.users[event.object.from_id].last_ans = event.object.text
                    if event.type == VkBotEventType.GROUP_JOIN:
                        #                print(event.object.user_id)
                        #                print(type(event.object.user_id))
                        self.set_keyboard(event.object.user_id,
                                          "Привет, я - чат-бот сообщества \"Красивые люди\"!\n"
                                          "Я могу помочь тебе с выбором процедур, ответить на часто задаваемые вопросы, "
                                          "и даже записаться на процедуры!\n"
                                          "Для взаимодействия воспользуйся кнопками снизу.\n\n"
                                          "Прейскурант и приблизительная длительность процедур описана разделе \"Об услугах\"",
                                          "default")
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        self.users[event.object.from_id].username = self.get_user_name(event.object.from_id)
                        if event.object.text.startswith("!set"):
                            self.now_kbd = event.object.text[5:]
                            self.set_keyboard(event.object.peer_id, "OK", self.now_kbd)
                        elif event.object.text == "!reload":
                            self.set_keyboard(event.object.peer_id, "OK", "default")
                            self.users[event.object.from_id].reload()
                            self.now_kbd = "default"
                        if event.object.payload:
                            if event.object.payload[11:].startswith("1"):
                                self.set_keyboard(event.object.peer_id,
                                                  self.users[event.object.from_id].description_handler(
                                                      event.object.text),
                                                  event.object.payload[12:-2])
                                self.now_kbd = event.object.payload[12:-2]
                            elif event.object.payload[11:].startswith("0"):
                                self.send_message(event.object.peer_id,
                                                  self.users[event.object.from_id].input_handler(event.object.text))
                            elif event.object.payload[11:].startswith("2"):
                                self.set_keyboard(event.object.peer_id,
                                                  self.users[event.object.from_id].input_handler(event.object.text),
                                                  event.object.payload[12:-2])
                                self.now_kbd = event.object.payload[12:-2]
                            elif event.object.payload[11:].startswith("3"):
                                self.now_kbd = self.users[event.object.from_id].antiflood_kbd()
                                self.set_keyboard(event.object.peer_id,
                                                  self.users[event.object.from_id].antiflood_response(),
                                                  self.now_kbd)
                            elif event.object.payload[11:].startswith("4"):
                                self.now_kbd = self.users[event.object.from_id].sign_kbd()
                                self.set_kbd_photo(event.object.peer_id,
                                                   self.users[event.object.from_id].input_handler(event.object.text),
                                                   self.now_kbd,
                                                   "photo-191050296_457239017")
                            elif event.object.payload[11:].startswith("5"):
                                self.now_kbd = self.users[event.object.from_id].check_month(event.object.text)
                                self.set_keyboard(event.object.peer_id,
                                                  self.users[event.object.from_id].input_handler(event.object.text),
                                                  self.now_kbd)
                            elif event.object.payload[11:].startswith("6"):
                                self.set_keyboard(event.object.peer_id,
                                                  self.users[event.object.from_id].input_handler(event.object.text),
                                                  self.users[event.object.from_id].check_day(event.object.text))
                                self.now_kbd = self.users[event.object.from_id].check_day(event.object.text)
                            elif event.object.payload[11:].startswith("7"):
                                """
                                Сюда нужен какой-то if. Чтобы проверял, что введено, иначе все херня.
                                Иначе клавиатуру не сохранить
                                Либо можно задать две возможных клавиатуры ниже, и все
                                """
                                if self.users[event.object.from_id].final_kbd(event.object.text) == "time":
                                    response = (self.users[event.object.from_id].username + ", к сожалению,"
                                                                                            "вы выбрали занятое время, "
                                                                                            "попробуйте еще раз")
                                    self.set_keyboard(event.object.from_id,
                                                      response,
                                                      "time"
                                                      )
                                elif self.users[event.object.from_id].final_kbd(event.object.text) == "confirmation":
                                    self.set_keyboard(event.object.from_id,
                                                      self.users[event.object.from_id].input_handler(event.object.text),
                                                      "confirmation")
                            elif event.object.payload[11:].startswith("8"):
                                self.now_kbd = event.object.payload[12:-2]
                                self.set_keyboard(event.object.peer_id,
                                                  "Возвращаемся...",
                                                  self.now_kbd)
                                self.users[event.object.from_id].clear_input()
                            elif event.object.payload[11:].startswith("9"):
                                self.now_kbd = event.object.payload[12:-2]
                                self.users[event.object.from_id].antiflood_timer_start()
                                self.set_keyboard(event.object.peer_id, "Заявка оставлена, в ближайшее время "
                                                                        "Оксана свяжется с Вами для подтверждения",
                                                  self.now_kbd)
                                self.users[event.object.from_id].full_name = self.get_user_name(event.object.from_id) + \
                                                                             " " + self.get_user_surname(
                                    event.object.from_id)
                                self.users[event.object.from_id].client_id = event.object.from_id
                                create_event(self.users[event.object.from_id].summary,
                                             self.users[event.object.from_id].make_description(),
                                             self.users[event.object.from_id].procedure_date,
                                             self.users[event.object.from_id].end_time)
                                self.users[event.object.from_id].clear_input()

                        elif not event.object.payload:
                            response = (self.get_user_name(
                                event.object.from_id) + ", пожалуйста, воспользуйтесь кнопками для общения с ботом.")
                            self.set_keyboard(event.object.peer_id,
                                              response, self.now_kbd)
            except Exception:
                pass

    def send_message(self, peer_id, message):
        self.vk_api.messages.send(peer_id=peer_id, message=message)

    def set_kbd_photo(self, peer_id, message, keyboard_name, attachment):
        keyboard_name = ("keyboard/" + keyboard_name + ".json")
        self.vk_api.messages.send(peer_id=peer_id,
                                  message=message,
                                  keyboard=open(keyboard_name, "r", encoding="UTF-8").read(),
                                  attachment=attachment)

    def set_keyboard(self, peer_id, message, keyboard_name):
        keyboard_name = ("keyboard/" + keyboard_name + ".json")
        self.vk_api.messages.send(peer_id=peer_id,
                                  message=message,
                                  keyboard=open(keyboard_name, "r", encoding="UTF-8").read())

    def get_user_name(self, user_id):
        """ Получаем имя пользователя"""
        return self.vk_api.users.get(user_id=user_id)[0]['first_name']

    def get_user_surname(self, user_id):
        """ Получаем фамилию пользователя"""
        return self.vk_api.users.get(user_id=user_id)[0]["last_name"]
