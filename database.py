# import sqlite3
from flask import Flask,url_for,render_template,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# from flaskweb import db




app= Flask(__name__)  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db=SQLAlchemy(app)





class Myvelocity_data(db.Model):
    id =db.Column(db.Integer,primary_key=True)
    timerecord = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    velocity_x = db.Column(db.Integer,nullable= False)
    velocity_z =db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"current {self.timerecord} : at speed Vx: {self.velocity_x} Vy: {self.velocity_z} "

class place (db.Model):
    id =db.Column(db.Integer,primary_key=True)
    Place = db.Column(db.String(30),nullable= False)
    x = db.Column(db.Integer,nullable= False)
    y = db.Column(db.Integer,nullable= False)
    z = db.Column(db.Integer,nullable= False)
    yaw = db.Column(db.Integer,nullable= False)
    pitch = db.Column(db.Integer,nullable= False)
    row = db.Column(db.Integer,nullable= False)

    def __repr__(self):
        return f"x:{self.x}  y:{self.y}  z:{self.z} yaw:{self.yaw} pitch:{self.pitch} row: {self.row}"

class Battery(db.Model):
    battery_state =  db.Column(db.Integer,primary_key=True)



if __name__ == "__main__":
    app.run(debug=True)
    

