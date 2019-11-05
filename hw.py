import requests as r
from bs4 import BeautifulSoup
import datetime

XML = open('settings.xml', 'r', encoding="utf-8").read()
SETTINGS = BeautifulSoup(XML, "lxml").find('settings')
LOGIN_1 = SETTINGS.find('login-1').text
PASSWORD_1 = SETTINGS.find('password-1').text
LOGIN_2 = SETTINGS.find('login-2').text
PASSWORD_2 = SETTINGS.find('password-2').text


def get_session(l, p):
    session = r.Session()
    data = {'Login': l, 'Password': p, 'doLogin': 1, 'authsubmit': 'Войти'}
    session.get('https://dnevnik2.petersburgedu.ru/login')
    session.post('https://petersburgedu.ru/user/auth/login/n', data=data)
    return session


def get_next_day():
    day = datetime.datetime.now()
    delta = datetime.timedelta(1)
    day += delta

    if (day - delta).strftime('%A') == 'Saturday':
        day += delta

    return day


SESSION_1 = get_session(LOGIN_1, PASSWORD_1)
SESSION_2 = get_session(LOGIN_2, PASSWORD_2)
NEXT_DAY = get_next_day()
NEXT_DAY_INT = get_next_day().isoweekday()



def get_day_timetable(day):
    timetable = BeautifulSoup(XML, "lxml").find('timetable')
    timetable_of_day_raw = timetable.findAll('day')[day].find_all('lesson')
    timetable_of_day = []
    for lesson in range(0, len(timetable_of_day_raw)):
        timetable_of_day.append(tuple(timetable_of_day_raw[lesson].text.split()))
    return tuple(timetable_of_day)


def get_lesson_homework(lsn, ses):
    subj = lsn[0]
    link = lsn[1]

    subj_soup = BeautifulSoup(ses.get(link).text, 'html.parser')
    homework = subj_soup.find('table', class_="subject-stat")

    if homework:
        homework = ' '.join(subj_soup.find('table', class_="subject-stat").find_all('td')[2].text.split())

    if homework == '' or not homework:
        homework = 'Нет дз / Учитель его не написал'

    return subj + ' - ' + homework + '\n\n'


def get_res(day_int, is_next_day, rslt, ses1, ses2):
    if is_next_day:
        for lsn in get_day_timetable(day_int-1):
            if len(lsn) == 2:
                rslt += get_lesson_homework(lsn, ses1)
            else:
                rslt += get_lesson_homework(lsn[:2:], ses1)
                rslt += get_lesson_homework(lsn[2::], ses2)
        return rslt.replace('_', ' ')
    else:
        return None


class Homework:
    def __init__(self):
        self.result = 'Домашнее задание на ' + str(NEXT_DAY.strftime('%d.%m.%Y')) + '\n' \
             + 'Также читайте сайт класса: loxxx.tk ' + '\n\n'

    def get_tomorrow(self):
        return get_res(NEXT_DAY_INT, True, self.result, SESSION_1, SESSION_2)


if __name__ == '__main__':
    print(Homework().get_tomorrow())
