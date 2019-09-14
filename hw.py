import requests as r
from bs4 import BeautifulSoup
import datetime

XML = open('settings.xml', 'r', encoding="utf-8").read()
SETTINGS = BeautifulSoup(XML, "lxml")
LOGIN = SETTINGS.find('login').text
PASSWORD = SETTINGS.find('password').text


def get_session(l, p):
    session = r.Session()
    session.get('https://dnevnik2.petersburgedu.ru/login')
    data = {
        'Login': l,
        'Password': p,
        'doLogin': 1,
        'authsubmit': 'Войти'
    }

    session.post('https://petersburgedu.ru/user/auth/login/n', data=data)
    return session


def get_next_day():
    day = datetime.datetime.now()
    delta = datetime.timedelta(1)
    day += delta

    if (day - delta).strftime('%A') == 'Saturday':
        day += delta

    return day


def get_homework():
    session = get_session(LOGIN, PASSWORD)
    url = 'https://petersburgedu.ru/dnevnik/timetable'
    timetable_html = session.get(url).text
    n_day = 'day-' + str(get_next_day().isoweekday())

    links = []
    lessons = []
    homework = []
    result = 'Домашнее задание на ' + str(get_next_day().strftime('%d.%m.%Y')) + '\n'\
             + 'Также читайте сайт класса: loxxx.tk ' + '\n\n'

    fut_timetable = BeautifulSoup(timetable_html, 'html.parser')
    fut_timetable = fut_timetable.findAll('td', class_=n_day)

    for i in range(len(fut_timetable)):
        if fut_timetable[i].find('a'):
            links.append('https://petersburgedu.ru' + fut_timetable[i].find('a')['href'])
            lessons.append(' '.join(fut_timetable[i].find('a').text.split()))

    for link in links:
        homework.append('')
        lesson_timetable = session.get(link).text
        l_soup = BeautifulSoup(lesson_timetable, 'html.parser')
        work = l_soup.find('table', class_="subject-stat")

        if work:
            work = l_soup.find('table', class_="subject-stat").find_all('td')[2].text
            homework[-1] = ' '.join(work.split())

        if homework[-1] == '':
            homework[-1] = 'Нет дз / Учитель его не написал'

    for i in range(len(lessons)):
        result += lessons[i] + ' - ' + homework[i] + '\n\n'

    return result


if __name__ == '__main__':
    print(get_homework())
