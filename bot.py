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

    message = "--->  Task # " + str(u.task_id+1) + '  <---\n\n'
    message += tasks[u.task_id].get('text')

    bot.sendMessage(tg_id, message)


def registration_user(tg_id):
    db.createUser(tg_id)
    u = db.getUser(tg_id)

    message = "Successful registration.\n\n"
    message += "Your ID: " + str(u.id)
    bot.sendMessage(tg_id, message)

    sleep(0.2)

    m = "New user.\nID: " + str(u.id)
    m += "\n#new"
    bot.sendMessageToMainChat(m)

    sleep(0.2)

    send_task(tg_id)


def start_c(data):
    tg_id = data['sender_id']
    u = db.getUser(tg_id)

    if u is None:
        registration_user(tg_id)
    else:
        if u.task_id < number_of_tasks:
            message = "We continue:"
            bot.sendMessageToChat(data, message)
            sleep(0.2)
            send_task(tg_id)
        else:
            me_c(data)



def help_c(data):
    message = "This is Help!\n\n"

    bot.sendMessageToChat(data, message)


def me_c(data):
    message = "This is Me!\n\n"

    u = db.getUser(data['sender_id'])
    if u is not None:
        if u.task_id == number_of_tasks:
            message += 'You have completed all the tasks.\n\n'
        message += "Your ID: " + str(u.id) + '\n\n'
        message += "Your Score: " + str(u.score)
        message += "\\" + str(max_score)

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
                bot.sendMessageToChat(data, 'Correct answer!\n:-)')
            else:
                bot.sendMessageToChat(data, 'Wrong answer!\n:-(')

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
            bot.sendMessageToChat(data, 'You have already solved all the tasks!')            
    else:
        bot.sendMessageToChat(data, 'I do not understand...')


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
