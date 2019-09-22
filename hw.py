import requests as r
from bs4 import BeautifulSoup
import datetime

XML = open('settings.xml', 'r', encoding="utf-8").read()
SETTINGS = BeautifulSoup(XML, "lxml").find('settings')
LOGIN = SETTINGS.find('login').text
PASSWORD = SETTINGS.find('password').text


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


def get_day_timetable(day):
    timetable = BeautifulSoup(XML, "lxml").find('timetable')
    timetable_of_day_raw = ' '.join(timetable.findAll('day')[day].text.split()).split()
    timetable_of_day = tuple(zip(timetable_of_day_raw[::2], timetable_of_day_raw[1::2]))
    return timetable_of_day


class GetHomework:
    def __init__(self):
        self.session = get_session(LOGIN, PASSWORD)

        self.next_day = get_next_day()
        self.next_day_int = get_next_day().isoweekday()

        self.result = 'Домашнее задание на ' + str(self.next_day.strftime('%d.%m.%Y')) + '\n'\
                      + 'Также читайте сайт класса: loxxx.tk ' + '\n\n'

    def tomorrow(self):
        res = self.result
        for lesson in get_day_timetable(self.next_day_int-1):
            subj = lesson[0]
            link = lesson[1]

            subj_soup = BeautifulSoup(self.session.get(link).text, 'html.parser')
            homework = subj_soup.find('table', class_="subject-stat")

            if homework:
                homework = ' '.join(subj_soup.find('table', class_="subject-stat").find_all('td')[2].text.split())

            if homework == '' or not homework:
                homework = 'Нет дз / Учитель его не написал'

            res += subj + ' - ' + homework + '\n'
        return res


if __name__ == '__main__':
    print(GetHomework().tomorrow())
