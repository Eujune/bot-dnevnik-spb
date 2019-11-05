from vk_api.bot_longpoll import VkBotLongPoll
import vk_api
from bs4 import BeautifulSoup
from hw import Homework

XML = open('settings.xml', 'r', encoding="utf-8").read()
SETTINGS = BeautifulSoup(XML, "lxml")
TOKEN = SETTINGS.find('token').text
ID = SETTINGS.find('groupid').text

vk = vk_api.VkApi(token=TOKEN)
vk.get_api()
longpoll = VkBotLongPoll(vk, ID)
doc = open('doc.txt', 'r', encoding='UTF-8').read()

for event in longpoll.listen():
    if event.object.text:
        print(event.object)

        if event.object.text.lower() == 'помощь':
            vk.method("messages.send",
                      {"peer_id": event.object.peer_id,
                       "message": doc, "random_id": 0})

        else:
            homework = Homework()
            if event.object.text.lower() == 'ботдз':
                vk.method("messages.send",
                          {"peer_id": event.object.peer_id,
                           "message": homework.get_tomorrow(), "random_id": 0})
