import vk_api
import random
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.bot_longpoll import VkBotEventType
from commander import Commander
from command_enum import Command
from mode_enum import Mode
from calendar_vk import create_event
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

    def test(self):
        self.send_msg(255396611, "Привет-привет!")

    def start(self):
        for event in self.long_poll.listen():  # Слушаем сервер
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.object.from_id not in self.users:
                    self.users[event.object.from_id] = Commander()
                username = self.get_user_name(event.object.from_id)
                surname = self.get_user_surname(event.object.from_id)
                print("  Name: " + username + " " + surname)
                # print("From: " + self.get_user_city(event.object.from_id))
                print("  Text: " + event.object.text)
                # В данном случае self.users[event.object.from_id].now_mode - список, и нам необходимо
                # переделать его в строку, чтобы можно было с чем-либо сравнивать
                if event.object.from_id in self.users:
                    print("  Proc: " + str(self.users[event.object.from_id].now_mode))
                print(" ============================== ")
                # Как сделать переключение по режиму, а не по тексту?
                # Пришло новое сообщение
                self.users[event.object.from_id].update(event.object.text)

                """Описываются ситуации смены клавиатур"""
                if event.object.text in Command.sign.value:
                    self.send_msg(event.object.peer_id,
                                  self.users[event.object.from_id].input(event.object.text),
                                  "keyboard/procedures.json")
                    self.users[event.object.from_id].update(event.object.text)
                    if event.object.text in Command.procedures.value:
                        self.send_msg(event.object.peer_id,
                                      self.users[event.object.from_id].input(event.object.text),
                                      "keyboard/procedures.json")
                        self.users[event.object.from_id].update(event.object.text)
                # elif self.users[event.object.from_id].now_mode == "Mode.time_selection"
                # Присылается разная клавиатура в зависимости от длины месяца
                elif event.object.text in Command.save_and_choose.value:
                    self.send_msg(event.object.peer_id,
                                  self.users[event.object.from_id].input(event.object.text),
                                  "keyboard/months.json")
                    self.users[event.object.from_id].update(event.object.text)
                elif event.object.text in Command.procedures.value:
                    self.send_msg(event.object.peer_id,
                                  self.users[event.object.from_id].input(event.object.text),
                                  "keyboard/procedures.json")
                    self.users[event.object.from_id].update(event.object.text)

                #                     Клавиатура с днями месяца. Имеет вложенные клавиатуры с выбором часов

                elif event.object.text in Command.long_months.value:
                    self.users[event.object.from_id].update(event.object.text)
                    self.send_msg(event.object.peer_id,
                                  self.users[event.object.from_id].input(event.object.text),
                                  "keyboard/days31.json")
                elif event.object.text in Command.short_months.value:
                    self.users[event.object.from_id].update(event.object.text)
                    self.send_msg(event.object.peer_id,
                                  self.users[event.object.from_id].input(event.object.text),
                                  "keyboard/days30.json")
                elif event.object.text in Command.february.value:
                    self.users[event.object.from_id].update(event.object.text)
                    self.send_msg(event.object.peer_id,
                                  self.users[event.object.from_id].input(event.object.text),
                                  "keyboard/days28.json")
                elif str(self.users[event.object.from_id].now_mode) == "Mode.date_selection_number":
                    self.users[event.object.from_id].update(event.object.text)
                    self.send_msg(event.object.peer_id,
                                  self.users[event.object.from_id].input(event.object.text),
                                  "keyboard/time.json")
                elif str(self.users[event.object.from_id].now_mode) == "Mode.time_selection":
                    self.users[event.object.from_id].update(event.object.text)
                    self.send_msg(event.object.peer_id,
                                  self.users[event.object.from_id].input(event.object.text),
                                  "keyboard/confirmation.json")
                elif str(self.users[event.object.from_id].last_ans) == "Все верно, запишите меня":
                    self.users[event.object.from_id].update(event.object.text)
                    client_identity = username + surname
                    create_event(client_identity,
                                 self.users[event.object.from_id].procedures_list,
                                 self.users[event.object.from_id].start_time,
                                 self.users[event.object.from_id].end_time)
                else:
                    self.send_msg(event.object.peer_id,
                                  self.users[event.object.from_id].input(event.object.text),
                                  "keyboard/default.json")

    def get_user_name(self, user_id):
        """ Получаем имя пользователя"""
        return self.vk_api.users.get(user_id=user_id)[0]['first_name']

    def get_user_surname(self, user_id):
        """ Получаем фамилию пользователя"""
        return self.vk_api.users.get(user_id=user_id)[0]["last_name"]

    def get_user_city(self, user_id):
        """ Получаем город пользователя"""
        return self.vk_api.users.get(user_id=user_id, fields="city")[0]["city"]['title']

    def send_message(self, peer_id, message):
        self.vk_api.messages.send(peer_id=peer_id, message=message)

    def send_msg(self, send_id, message, keyboard_name):

        """
        Отправка сообщения через метод messages.send
        :param keyboard_name: Название клавиатуры
        :param send_id: vk id пользователя, который получит сообщение
        :param message: содержимое отправляемого письма
        :return: None
        """
        return self.vk_api.messages.send(peer_id=send_id,
                                         message=message,
                                         random_id=random.randint(0, 2048),
                                         keyboard=open(keyboard_name, "r", encoding="UTF-8").read())
