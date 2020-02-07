from bs4 import BeautifulSoup
import requests as r
import datetime
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll

XML = open('settings.xml', 'r', encoding="utf-8").read()
SETTINGS = BeautifulSoup(XML, "lxml").find('settings')

LOGIN_1 = SETTINGS.find('login-1').text
PASSWORD_1 = SETTINGS.find('password-1').text
LOGIN_2 = SETTINGS.find('login-2').text
PASSWORD_2 = SETTINGS.find('password-2').text

TOKEN = SETTINGS.find('token').text
TIMETABLE = BeautifulSoup(XML, "lxml").find('timetable')
LESSONS_TIMETABLE_RAW = TIMETABLE.findAll('day')
SPECIAL_ID = 391805157
GROUP_ID = SETTINGS.find('group-id').text


def get_dnevnik_ses(login, password):
    session = r.Session()
    data = {'Login': login, 'Password': password,
            'doLogin': 1, 'authsubmit': 'Войти'}
    session.get('https://dnevnik2.petersburgedu.ru/login')
    session.post('https://petersburgedu.ru/user/auth/login/n', data=data)
    return session


def get_day_map():
    res = []
    for i in range(0, 7):
        if LESSONS_TIMETABLE_RAW[i].find_all('lesson'):
            res.append(True)
        else:
            res.append(False)
    return res


def get_next_day():
    today_day = datetime.datetime.now()
    today_day_int = datetime.datetime.now().isoweekday()
    day_map_2_weeks = get_day_map() * 2
    next_day_int = None
    c_delta = None

    for i in range(1, 15):
        print(day_map_2_weeks[i-1], i)
        if day_map_2_weeks[i-1] and today_day_int < i:
            if i > 7:
                next_day_int = i - 7
                c_delta = 7
            else:
                next_day_int = i
                c_delta = 0
            break

    delta = next_day_int - today_day_int + c_delta
    next_day = today_day + datetime.timedelta(delta)

    return next_day_int, next_day


def get_day_timetable(day):
    timetable_of_day_raw = LESSONS_TIMETABLE_RAW[day].find_all('lesson')
    timetable_of_day = []
    for lesson in range(0, len(timetable_of_day_raw)):
        timetable_of_day.append(tuple(timetable_of_day_raw[lesson].text.split()))
    return tuple(timetable_of_day)


def get_lesson_homework(lsn, ses):
    subj = lsn[0]
    link = lsn[1]

    subj_soup = BeautifulSoup(ses.get(link).text, 'html.parser')
    hmwrk = subj_soup.find('table', class_="subject-stat")

    if hmwrk:
        hmwrk = ' '.join(subj_soup.find('table', class_="subject-stat").find_all('td')[2].text.split())

    if hmwrk == '' or not hmwrk:
        hmwrk = 'Нет дз / Учитель его не написал'

    return subj + ' - ' + hmwrk + '\n\n'


def get_homework(day_int, rslt, ses1, ses2, is_next_day=True):

    if is_next_day:
        for lsn in get_day_timetable(day_int):

            if len(lsn) == 2:
                rslt += get_lesson_homework(lsn, ses1)
            else:
                rslt += get_lesson_homework(lsn[:2:], ses1)
                rslt += get_lesson_homework(lsn[2::], ses2)
        return rslt.replace('_', ' ')
    else:
        return None


VK = vk_api.VkApi(token=TOKEN)
VK.get_api()
LONGPOLL = VkBotLongPoll(VK, GROUP_ID)


for event in LONGPOLL.listen():
    if str(event.type) == "VkBotEventType.MESSAGE_NEW":
        if event.object.text.lower() == 'ботдз':
            NEXT_DAY, NEXT_DAY_INT = get_next_day()

            SES_1 = get_dnevnik_ses(LOGIN_1, PASSWORD_1)
            SES_2 = get_dnevnik_ses(LOGIN_2, PASSWORD_2)

            RAW_RES = 'Домашнее задание на ' + str(NEXT_DAY.strftime('%d.%m.%Y')) + '\n' \
                      + 'Также читайте сайт класса: loxxx.tk ' + '\n\n'

            HOMEWORK = get_homework(NEXT_DAY_INT, RAW_RES, SES_1, SES_2)

            SES_1.close()
            SES_2.close()
            if event.object.from_id == SPECIAL_ID:
                VK.method("messages.send",
                          {"peer_id": event.object.peer_id,
                           "message": HOMEWORK + '\nХорошего дня, Данечка', "random_id": 0})
            else:
                VK.method("messages.send",
                          {"peer_id": event.object.peer_id,
                           "message": HOMEWORK, "random_id": 0})
