from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class USER(db.Model):
    __tablename__="user"
    uid = db.Column(db.Integer,autoincrement=True,primary_key=True)
    name = db.Column(db.String,nullable=False)
    id = db.Column(db.String,unique=True,nullable=False)
    password = db.Column(db.String,nullable=False)

class LIST(db.Model):
    __tablename__="list"
    uid = db.Column(db.String,db.ForeignKey("user.uid"),nullable=False)
    lid = db.Column(db.Integer,autoincrement=True,primary_key=True)
    lname = db.Column(db.String,nullable=False)
    description = db.Column(db.String)
    trend=db.Column(db.String)
    

class CARD(db.Model):
    __tablename__="card"
    lid = db.Column(db.String,db.ForeignKey("list.lid"),nullable=False)
    cid = db.Column(db.Integer,autoincrement=True,primary_key=True)
    title = db.Column(db.String,nullable=False)
    content = db.Column(db.String)
    deadline = db.Column(db.String,nullable=False)
    completed_flag = db.Column(db.String)
    deadline_passed = db.Column(db.String)
    timestamp = db.Column(db.String)
    #user=db.relationship("USER",secondary="tracker")
