from vk_api.bot_longpoll import VkBotLongPoll
import vk_api
from bs4 import BeautifulSoup
from hw import GetHomework

XML = open('settings.xml', 'r', encoding="utf-8").read()
SETTINGS = BeautifulSoup(XML, "lxml")
TOKEN = SETTINGS.find('token').text
ID = SETTINGS.find('groupid').text

vk = vk_api.VkApi(token=TOKEN)
vk.get_api()
longpoll = VkBotLongPoll(vk, ID)

for event in longpoll.listen():
    print(event.object.peer_id)
    if event.object.text.lower() and event.object.text.lower() == "ботдз":
        vk.method("messages.send", {"peer_id": event.object.peer_id,
                                    "message": GetHomework().tomorrow(), "random_id": 0})
