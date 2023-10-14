import jwt
#from jwt import auth_required
from jwt_trial import auth_required
from datetime import datetime, timedelta
from flask import current_app as app
from flask_caching import Cache
import time
import pandas as pd
import csv 

from flask_restful import Resource,Api,reqparse,fields,marshal_with,abort
from models import db
from models import USER,LIST,CARD
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

from tasks import *

app.config["CACHE_TYPE"] = "RedisCache"
app.config['CACHE_REDIS_HOST'] = "localhost"
app.config['CACHE_REDIS_PORT'] = 6379
app.config["CACHE_REDIS_URL"] = "redis://localhost:6379"  
app.config['CACHE_DEFAULT_TIMEOUT'] = 200

cache = Cache(app)
api=Api(app)


@app.route("/hello",methods=["GET","POST"])
def hello():
    job=just_say_hello.delay()
    print("gbjkfdg")
    return str(job),200

user_req = reqparse.RequestParser()
user_req.add_argument('name',type=str,help="Username is a string")
user_req.add_argument('id',type=str,help="email is a string")
user_req.add_argument('uid',type=str,help="id is an integer")
user_req.add_argument('password',type=str,help="password is a string")

user_field={
    'uid': fields.Integer,
    'name': fields.String,
    'id': fields.String,
    'password': fields.String,
}

list_req = reqparse.RequestParser()
list_req.add_argument('lname',type=str,help="list name is a string")
list_req.add_argument('lid',type=str,help="lid is a string")
list_req.add_argument('uid',type=str,help="uid is an integer")
list_req.add_argument('description',type=str,help="description is a string")
list_req.add_argument('total_tasks',type=str,help="description is a string")
list_req.add_argument('deadline_passed_count',type=str,help="description is a string")
list_req.add_argument('completed_count',type=str,help="description is a string")



card_req = reqparse.RequestParser()
card_req.add_argument('list',type=str,help="List is a integer")
card_req.add_argument('title',type=str,help="Title is a string")
card_req.add_argument('cid',type=str,help="lid is a integer")
card_req.add_argument('lid',type=str,help="lid is an integer")
card_req.add_argument('content',type=str,help="Content is a string")
card_req.add_argument('deadline',type=str,help="Deadline is a string")
card_req.add_argument('completed_flag',type=str,help="Completed Flag is a string")
card_req.add_argument('timestamp',type=str,help="Timestamp is a string")



card_field={
    'list':fields.Integer,
    'lid': fields.Integer,
    'cid': fields.Integer,
    'title': fields.String,
    'content': fields.String,
    'deadline': fields.String,
    'completed_flag': fields.String,
    'deadline_passed': fields.String,
    'timestamp':fields.String
}

list_field={
    'uid': fields.Integer,
    'lid': fields.Integer,
    'lname': fields.String,
    'description': fields.String,
    'card_list':fields.List(fields.Nested(card_field)),
    'user':fields.List(fields.Nested(user_field)),
    'completed_count': fields.Integer,
    'deadline_passed_count': fields.Integer,
    'total_tasks': fields.Integer,
    'trend': fields.String
}

#################################################################################################################

class Login(Resource):
    #@marshal_with(user_field)
    def post(self):
        d={}
        data=user_req.parse_args()
        email=data.get("id",None)
        password=data.get("password",None)
        if email:
            if password:
                user=USER.query.filter(USER.id==email).first()
                if user:
                    if user.password==password:
                        d["user"]=[user.uid,user.name,user.id,user.password]
                        d["token"]=jwt.encode({
            'uid': user.uid,
            'exp' : datetime.utcnow() + timedelta(minutes = 30)
        }, app.config['SECRET_KEY'])
                        return d
                    else:
                        abort(404,message="Wrong password")
                else:
                    abort(404,message="User does not exists! Please signup")
            else:
                abort(404,message="Please enter password")
        else:
            abort(404,message="Please enter email ID")


api.add_resource(Login,"/api/login")

class Signup(Resource):
    #@marshal_with(user_field)

    def post(self):
        d={}
        data=user_req.parse_args()
        name=data.get("name",None)
        id=data.get("id",None)
        password=data.get("password",None)
        if name:
            if id:
                if password:
                    dup_user=USER.query.filter(USER.id==id).first()
                    if dup_user:
                        abort(404,message="User already exists")
                    else:
                        user=USER(name=name,id=id,password=password)
                        db.session.add(user)
                        db.session.commit()
                        d["user"]=data
                        d["token"]=jwt.encode({'uid': user.uid,'exp' : datetime.utcnow() + timedelta(minutes = 30)}, app.config['SECRET_KEY'])
                        return d
                else:
                    abort(404,message="Password missing")
            else:
                abort(404,message="Email ID missing")
        else:
            abort(404,message="Username missing")


api.add_resource(Signup,"/api/signup")

#####################################################################################################


class Dashboard(Resource):
    @auth_required
    #getting list and respective cards
    @marshal_with(list_field)
    @cache.cached(timeout=2)
    def get(self,uid=None):
        d={}
        if uid:
            user=USER.query.filter(USER.uid==uid).first()
            if user:
                list=LIST.query.filter(LIST.uid==uid).all()
                if list:
                    for i in list:
                        card=CARD.query.filter(CARD.lid==i.lid).all()
                        i.card_list=card
                        i.user=user
                    return list
                else:
                    abort(404,message="no list found")
            else:
                abort(404,message="Invalid user id")
        else:
            abort(404,message="Enter user id")
        

api.add_resource(Dashboard,"/api/dashboard/<int:uid>")


##################################################################################################################

class List(Resource):
    @auth_required
    #getting list and its details
    @marshal_with(list_field)
    @cache.cached(timeout=2)
    def get(self,uid=None,lid=None):
        if uid:
            user=USER.query.filter(USER.uid==uid).first()
            if user:
                list=LIST.query.filter(LIST.uid==uid).all()
                if list:
                    for i in list:
                        card=CARD.query.filter(CARD.lid==lid).all()
                        i.card_list=card
                    return list
                else:
                    abort(404,message="no list found")
            else:
                abort(404,message="Invalid user id")
        else:
            abort(404,message="Enter user id")

    # adding a list
    @auth_required
    @marshal_with(list_field)
    def post(self,uid=None):
        data=list_req.parse_args()
        lname=data.get("lname",None)
        description=data.get("description",None)
        if lname:
            if description:
                dup_list=LIST.query.filter(LIST.lname==lname).first()
                if dup_list:
                    abort(404,message="List already exists")
                else:
                    list=LIST(uid=uid,lname=lname,description=description)
                    db.session.add(list)
                    db.session.commit()
                    return list
            else:
                abort(404,message="Description missing")
        else:
            abort(404,message="List name missing")


#editing a list
    @auth_required
    @marshal_with(list_field)
    def put(self,uid=None,lid=None):
        data=list_req.parse_args()
        lname=data.get("lname",None)
        description=data.get("description",None)

        if lname and description:
            list=LIST.query.filter(LIST.lid==lid).first()
            if list:
                list.lname=lname
                list.description=description
                db.session.commit()
                return data
            else:
                abort(404,message="invalid list")

        if lname:
            list=LIST.query.filter(LIST.lid==lid).first()
            if list:
                list.lname=lname
                db.session.commit()
                return data
            else:
                abort(404,message="invalid list")

        if description:
            list=LIST.query.filter(LIST.lid==lid).first()
            if list:
                list.description=description
                db.session.commit()
                return data
            else:
                abort(404,message="invalid list")

        
        list=LIST.query.filter(LIST.lid==lid).first()
        if list:
            return data
        else:
            abort(404,message="invalid list")


#deleting a list and respective cards
    @auth_required
    @marshal_with(user_field)
    def delete(self,uid=None,lid=None):
        list=LIST.query.filter(LIST.lid==lid).first()
        if list:
            card=CARD.query.filter(CARD.lid==lid).all()
            for i in card:
                db.session.delete(i)
                db.session.commit()
            db.session.delete(list)
            db.session.commit()
            return 'user deleted',200
        else:
            abort(404,message="List does not exists")

api.add_resource(List,"/api/list/<int:uid>","/api/list/<int:uid>/<int:lid>")

###############################################################################################################


class Card(Resource):
    @auth_required
    #getting list and its details
    @marshal_with(card_field)
    def get(self,uid=None,lid=None,cid=None):
        if uid:
            user=USER.query.filter(USER.uid==uid).first()
            if user:
                list=LIST.query.filter(LIST.lid==lid).first()
                if list:
                    card=CARD.query.filter(CARD.cid==cid).first()
                    return card
                else:
                    abort(404,message="no card found")
            else:
                abort(404,message="Invalid list id")
        else:
            abort(404,message="Enter user id")


    #adding a card
    @auth_required
    @marshal_with(card_field)
    def post(self,uid=None,lid=None):
        data=card_req.parse_args()
        title=data.get("title",None)
        content=data.get("content",None)
        completed_flag=False
        today = datetime.today().date()
        deadline = datetime.strptime(data.get("deadline",None), '%Y-%m-%d').date()

        if lid:
            if title:
                if content:
                    if deadline:
                        if today>deadline:
                            deadline_passed=True
                        else:
                            deadline_passed=False
                        dup_card=CARD.query.filter(CARD.title==title).first()
                        if dup_card:
                            abort(404,message="Card already exists")
                        else:
                            card=CARD(lid=lid,title=title,content=content,deadline=deadline,completed_flag=completed_flag,deadline_passed=deadline_passed,timestamp=today)
                            db.session.add(card)
                            db.session.commit()
                            return card
                    else:
                        abort(404,message="deadline missing")
                else:
                    abort(404,message="Content missing")
            else:
                abort(404,message="Title missing")
        else:
            abort(404,message="inValid list ID")


#editing a card
    @auth_required
    @marshal_with(card_field)
    def put(self,uid=None,lid=None,cid=None):
        data=card_req.parse_args()
        list=data.get("list",None)
        title=data.get("title",None)
        content=data.get("content",None)
        completed_flag=data.get("completed_flag",None)
        today = datetime.today().date()

        card=CARD.query.filter(CARD.cid==cid).first()
        if card:
            if lid!=list:
                card.lid=list
            card.completed_flag=completed_flag
            card.timestamp=today
            if title and content:
                card.title=title
                card.content=content
            if title:
                card.title=title
            if content:
                card.content=content
            db.session.commit()
            return data
        else:
            abort(404,"invalid card")



#deleting a card 
    @auth_required
    @marshal_with(card_field)
    def delete(self,uid=None,lid=None,cid=None):
        card=CARD.query.filter(CARD.cid==cid).first()
        if card:
            db.session.delete(card)
            db.session.commit()
            return 'card deleted',200
        else:
            abort(404,message="card does not exists")

api.add_resource(Card,"/api/card/<int:uid>/<int:lid>/<int:cid>","/api/card/<int:uid>/<int:lid>")


#################################################################################################################


class Logout(Resource):
    @auth_required
    @marshal_with(user_field)
    def get(self,uid=None):
        if uid:
            user=USER.query.filter(USER.uid==uid).first()
            if user:
                return user
            else:
                abort(404,message="invalid user id")
        else:
            abort(404,message="enter user id")

api.add_resource(Logout,"/api/logout/<int:uid>")


################################################################################################################


class Summary(Resource):
    #getting list and respective cards
    @auth_required
    @marshal_with(list_field)
    def get(self,uid=None):
        if uid:
            user=USER.query.filter(USER.uid==uid).first()
            if user:
                list=LIST.query.filter(LIST.uid==uid).all()
                if list:
                    for i in list:
                        y = []
                        incomplete=0
                        i.completed_count=0
                        i.deadline_passed_count=0
                        card=CARD.query.filter(CARD.lid==i.lid).all()
                        i.total_tasks=len(card)
                        i.card_list=card
                        i.user=user
                        for j in card:
                            if j.deadline_passed=='1':
                                i.deadline_passed_count+=1
                            if (j.completed_flag=='True' or j.completed_flag=='1') and j.deadline_passed=='0':
                                i.completed_count+=1
                        incomplete=i.total_tasks-i.completed_count-i.deadline_passed_count
                        bar = plt.figure()
                        y=[i.completed_count,incomplete,i.deadline_passed_count]
                        x = ['Complete', 'Incomplete', 'Deadline']
                        plt.bar(x, y, width = 0.4)
                        bar.savefig('project/src/assets/bargraph'+str(i.lid)+'.png')
                        if len(card)==0:
                            i.trend="nocard.png"
                        else:
                            i.trend='bargraph'+str(i.lid)+'.png'
                    return list
                else:
                    abort(404,message="no list found")
            else:
                abort(404,message="Invalid user id")
        else:
            abort(404,message="Enter user id")
        

api.add_resource(Summary,"/api/summary/<int:uid>")


##################################################################################################################


class Export_Dashboard(Resource):
    #exporting dashboard
    @auth_required
    @marshal_with(user_field)
    def get(self,uid=None):
        lname=[]
        ldescription=[]
        ctitle=[]
        ccontent=[]
        cdeadline=[]
        if uid:
            user=USER.query.filter(USER.uid==uid).first()
            if user:
                data=np.array([user.name])
                username=pd.Series(data)
                lists=LIST.query.filter(LIST.uid==uid).all()
                for i in lists:
                    lname.append(i.lname)
                    ldescription.append(i.description)

                    cards=CARD.query.filter(CARD.lid==i.lid).all()
                    for j in cards:
                        ctitle.append(j.title)
                        ccontent.append(j.content)
                        cdeadline.append(j.deadline)
                lnamedata=np.array(lname)
                Lname=pd.Series(lnamedata)
                ldescriptiondata=np.array(ldescription)
                Ldescription=pd.Series(ldescriptiondata)
                ctitledata=np.array(ctitle)
                Ctitle=pd.Series(ctitledata)
                ccontentdata=np.array(ccontent)
                Ccontent=pd.Series(ccontentdata)
                cdeadlinedata=np.array(cdeadline)
                Cdeadline=pd.Series(cdeadlinedata)
                df = pd.DataFrame({'username': username,'list name': Lname,'list description': Ldescription,'card name': Ctitle,'Card description': Ccontent,'card deadline': Cdeadline}) 
                df.to_csv('file_dashboard.csv')
                return user
            else:
                abort(404,message="Invalid User")
        else:
            abort(404,message="Invalid UID")

api.add_resource(Export_Dashboard,"/api/export_dashboard/<int:uid>")



class Export_List(Resource):
    #exporting list
    @auth_required
    @marshal_with(user_field)
    def get(self,uid=None,lid=None):
        d={}
        if uid:
            user=USER.query.filter(USER.uid==uid).first()
            if user:
                list=LIST.query.filter(LIST.lid==lid).first()
                if list:
                    d = {
                            "list name": [list.lname],
                            "list deascription": [list.description],
                        }
                    df = pd.DataFrame(d) 
                    df.to_csv('file_list.csv')
                    print(d)
                    return list
                else:
                    abort(404,message="Invalid List")
            else:
                abort(404,message="Invalid User")
        else:
            abort(404,message="Invalid UID")
        

api.add_resource(Export_List,"/api/export_list/<int:uid>/<int:lid>")


class Export_Card(Resource):

    #exporting card
    @auth_required
    @marshal_with(card_field)
    def get(self,uid=None,lid=None,cid=None):
        if uid:
            user=USER.query.filter(USER.uid==uid).first()
            if user:
                list=LIST.query.filter(LIST.lid==lid).first()
                if list:
                    card=CARD.query.filter(CARD.cid==cid).first()
                    if card:
                        d = {
                            "card title": [card.title],
                            "card content": [card.content],
                            "card deadline": [card.deadline],
                            "card timestamp": [card.timestamp]
                        }
                        df = pd.DataFrame(d) 
                        df.to_csv('file_card.csv')
                        return card
                    else:
                        abort(404,message="Invalid Card")
                else:
                    abort(404,message="Invalid List")
            else:
                abort(404,message="Invalid User")
        else:
            abort(404,message="Invalid UID")
        

api.add_resource(Export_Card,"/api/export_card/<int:uid>/<int:lid>/<int:cid>")





@app.route('/huehue')
@cache.cached(timeout=50)
def testingcache():
    time.sleep(10)
    return "done"