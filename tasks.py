from worker import celery
from flask import current_app as app
from models import USER,LIST,CARD
from mail import send_email
from jinja2 import Template

from celery import Celery
from celery.schedules import crontab


@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(crontab(hour=21, minute=00), daily_reminder.s(), name='everyday 9PM')
    sender.add_periodic_task(crontab(0, 0, day_of_month='1'), monthly_reminder.s(), name='everyday month')

    # Calls test('world') every 30 seconds
    #sender.add_periodic_task(30.0, test.s('world'), expires=10)

    # Executes every Monday morning at 7:30 a.m.
    # sender.add_periodic_task(
    #     crontab(hour=7, minute=30, day_of_week=1),
    #     test.s('Happy Mondays!'),
    # )

@celery.task()
def just_say_hello():
    print("HEHEHEHHEHE")

@celery.task()
def daily_reminder():
    users=USER.query.all()
    for user in users:
        lists=LIST.query.filter(LIST.uid==user.uid).all()
        for list in lists:
            cards=CARD.query.filter(CARD.lid==list.lid).all()
            for i in cards:
                if i.completed_flag!="True" or i.completed_flag!="1":
                    with open("project/public/mail.html","r") as b:
                        html=Template(b.read())
                        send_email(user.id, subject="daily reminder", message=html.render(user=user,list=list,i=i))

@celery.task()
def monthly_reminder():
    users=USER.query.all()
    for user in users:
        d={}
        lists=LIST.query.filter(LIST.uid==user.uid).all()
        for list in lists:
            d[list.lname]=[]
            cards=CARD.query.filter(CARD.lid==list.lid).all()
            for card in cards:
                d[list.lname].append([card.title,card.content,card.deadline,card.completed_flag,card.deadline_passed])

        with open("project/public/monthly.html","r") as b:
            html=Template(b.read())
            send_email(user.id, subject="monthly progress", message=html.render(d=d,user=user))
        
