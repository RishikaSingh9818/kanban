from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid 
from  werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app as app
from models import USER

import jwt
from datetime import datetime, timedelta
from functools import wraps


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'access-token' in request.headers:
            token = request.headers['access-token']
        # return 401 if token is not passed
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
            
  
        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'],algorithms=["HS256"])
            current_user = USER.query\
                .filter_by(uid = data['uid'])\
                .first()
        except:
            return jsonify({'message' : 'Token is missing !!'}), 401
            # return {
            #     'message' : 'Token is invalid !!'
            # }, 401
        # returns the current logged in users contex to the routes
        # data = jwt.decode(token, app.config['SECRET_KEY'],algorithms=["HS256"])
        # print(data)
        return  f( *args, **kwargs)
  
    return decorated