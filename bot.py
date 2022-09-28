from Penger.penger import Penger

from time import sleep
import json
import db


MAIN_CHAT = None
bot = None
tasks = {}
number_of_tasks = 0
max_score = 0


def send_task(tg_id):
    u = db.getUser(tg_id)

    message = "---> Задачка # " + str(u.task_id+1) + '  <---\n\n'
    message += tasks[u.task_id].get('text')

    bot.sendMessage(tg_id, message)


def registration_user(tg_id):
    db.createUser(tg_id)
    u = db.getUser(tg_id)

    message = "Добро пожаловать на викторину!\n\n"
    message += "Ваш ID: " + str(u.id)
    bot.sendMessage(tg_id, message)

    sleep(0.2)

    m = "New user.\nID: " + str(u.id)
    m += "\n#new"
    bot.sendMessageToMainChat(m)


def start_c(data):
    tg_id = data['sender_id']
    u = db.getUser(tg_id)

    if u is None:
        registration_user(tg_id)
        sleep(0.1)
        help_c(data)
        sleep(0.1)
        me_c(data)
        sleep(0.2)
        send_task(tg_id)
    else:
        if u.task_id < number_of_tasks:
            message = "Продолжаем:"
            bot.sendMessageToChat(data, message)
            sleep(0.2)
            send_task(tg_id)
        else:
            me_c(data)



def help_c(data):
    message = "{ Справка }\n\n"
    message += 'Для начала участия в викторине надо нажать /start\n\n'
    message += 'Каждая задачка имеет несколько вариантов ответа. '
    message += 'Только один из них является верным.\n\n'
    message += 'Чтобы ответить, нужно отправить боту номер варианта ответа '
    message += '- цифру от 0 до 9.\n\n'
    message += 'На одну задачку ответить можно только один раз. \n\n'
    message += 'При ответе Вы увидите результат ответа,\n'
    message += 'а затем текст следующей задачки.\n\n'
    message += 'После прохождения викторины можете обратиться к организаторам '
    message += 'и получить приз, в зависимости от количества набранных баллов.\n\n'
    message += 'Чтобы повторно получить текст задачки, на которой Вы остановились:\n-> нажмите /start\n\n'
    message += 'Чтобы узнать свои результаты\n-> нажмите /me\n\n'
    message += 'Удачного прохождения и приятной игры! :-)'

    bot.sendMessageToChat(data, message)


def me_c(data):
    message = "{ Информация об игроке }\n\n"

    u = db.getUser(data['sender_id'])
    if u is not None:
        if u.task_id == number_of_tasks:
            message += 'Вы ответили на все задачки в викторине!\n'
            message += 'Можете сообщить результаты организаторам и получить приз :-)\n\n'
        elif u.task_id < number_of_tasks:
            message += 'На данный момент у Вас есть задачки без ответа.\n'
            message += 'Вы остановились на вопросе №' + str(u.task_id+1) + '.\n\n'
        message += "ID: " + str(u.id) + '\n'
        message += "Счёт: " + str(u.score)
        message += "\\" + str(max_score)
        message += '\n\n{ -------------------- }'
    else:
        message += 'Вы не зарегистированы.\n'
        message += 'Для начала прохождения викторины нажмите /start'

    bot.sendMessageToChat(data, message)


def empty(data):
    text = str(data['text'])
    tg_id = data['sender_id']

    u = db.getUser(tg_id)

    if (len(text) == 1) and \
        (text.isdigit()) and \
        (u is not None):
        if u.task_id < number_of_tasks:
            if str(tasks[u.task_id].get('answer')) == text:
                u.score += tasks[u.task_id].get('cost', 1)
                bot.sendMessageToChat(data, 'Ответ правильный!\n:-)')
            else:
                bot.sendMessageToChat(data, 'Ответ неправильный!\n:-(')

            sleep(0.2)

            u.task_id += 1
            db.update(u)
            u = db.getUser(tg_id)

            if u.task_id == number_of_tasks:
                m = "User has completed.\n"
                m += "ID: " + str(u.id)
                m += "\nScore:" + str(u.score)
                m += "\\" + str(max_score)
                m += "\n#end"
                bot.sendMessageToMainChat(m)
                sleep(0.2)
                me_c(data)
            else:
                send_task(tg_id)
        else:
            bot.sendMessageToChat(data, 'Вы уже ответили на все задачки.')
            sleep(0.2)
            me_c(data)            
    else:
        message = "Не понимаю... :-(\n"
        message += 'Ответом на задачку является цифра (0-9).\n'
        message += 'Для дополнительной справки:\n-> нажмите /help'
        bot.sendMessageToChat(data, message)


def main():
    global MAIN_CHAT
    global bot
    global tasks
    global number_of_tasks
    global max_score

    with open('token.txt') as f:
        BOT_TOKEN = f.read().rstrip()

    with open('main.txt') as f:
        MAIN_CHAT = f.read().rstrip()

    bot = Penger(token=BOT_TOKEN, mainChat=MAIN_CHAT)
    bot.accordance = {'/start': start_c, '/help': help_c, '/me': me_c}
    bot.emptyAccordance = empty

    with open("tasks.json", "r") as f:
        tasks = json.load(f)
    tasks = tasks['tasks']
    number_of_tasks = len(tasks)

    for x in tasks:
        max_score += x.get('cost', 1)

    print(tasks)
    print(max_score)

    bot.sendMessageToMainChat("Hello, world!")

    while True:
        bot.updateAndRespond()
        sleep(3)


if __name__ == '__main__':
    main()
