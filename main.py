from flask import Flask
from models import db
import os
from flask_cors import CORS
from worker import celery,ContextTask

#celery=None

app=Flask(__name__,static_url_path="/static")

CORS(app)
current_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///"+os.path.join(current_dir,"kanban.db")
app.secret_key="Rishikaisgreathuehue"

db.init_app(app)
app.app_context().push()
from resources import api
api.init_app(app)


celery=celery

CELERY_BROKER_URL="redis://127.0.0.1:6379/1"
CELERY_RESULT_BACKEND="redis://127.0.0.1:6379/2"

celery.conf.update(
    broker_url="redis://127.0.0.1:6379/1",
    result_backend="redis://127.0.0.1:6379/2",
    timezone="Asia/Kolkata"
)

celery.Task=ContextTask


if __name__=="__main__":
    app.run(debug=True)