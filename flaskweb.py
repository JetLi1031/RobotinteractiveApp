from flask import Flask,request,url_for,render_template,jsonify
from database import *
import time 
import pyrebase
import roslibpy
import roslibpy.actionlib
import numpy as np

## The roslibjs client 
client = roslibpy.Ros(host='0.0.0.0', port=9090)

try:
    client.run()
    action_client = roslibpy.actionlib.ActionClient(client,
                                            '/move_base',
                                            'move_base_msgs/MoveBaseAction')
except Exception as err:
    print(f' The error : {err} \n please ensure Ros bridge_websockket turned on')

def movetoedstination(coordinate):
        coordinate = [float(i) for i in coordinate]
        listofquaternion = euler_to_quaternion(coordinate[3],coordinate[4],coordinate[5])
        goal = roslibpy.actionlib.Goal(action_client,roslibpy.Message({'target_pose': {'header': {'seq': 0, 'stamp': {'secs': 0, 'nsecs': 0}, 'frame_id': 'map'}, 'pose': {'position': {'x':float(coordinate[0]), 'y': float(coordinate[1]), 'z': 0.0}, 'orientation': {'x': listofquaternion[0], 'y': listofquaternion[1], 'z': listofquaternion[2], 'w': listofquaternion[3]}}}}))
        goal.on('feedback', lambda f: print(f['base_position']))
        goal.send()
        # result = goal.wait(10)
        # action_client.dispose()
        # print('Result: {}'.format(result))
  
def euler_to_quaternion(yaw, pitch, roll):
        yaw= yaw/180*np.pi
        pitch= pitch/180*np.pi
        roll= roll/180*np.pi
        qx = np.sin(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) - np.cos(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
        qy = np.cos(roll/2) * np.sin(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.cos(pitch/2) * np.sin(yaw/2)
        qz = np.cos(roll/2) * np.cos(pitch/2) * np.sin(yaw/2) - np.sin(roll/2) * np.sin(pitch/2) * np.cos(yaw/2)
        qw = np.cos(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)

        return [qx, qy, qz, qw]
        


#fire base initialization
config = {
  "apiKey": "ZP7Kj40OB47QGISM17xKYrsh2NJgd0i22uPSpx39",
  "authDomain": "mitappinventordiffrobot.firebaseapp.com",
  "databaseURL": "https://mitappinventordiffrobot-default-rtdb.firebaseio.com/",
  "storageBucket": "mitappinventordiffrobot.appspot.com"
}
firebase = pyrebase.initialize_app(config)
firedb = firebase.database()

#local function 
def find_deletebyvalue (listPost, deletevalue): #delete unwanted location in list of dictionary 
    for z in listPost:
        for x,y in z.items():
            if y == str(deletevalue):
                listPost.pop(listPost.index(z))

def check_key(dict,key):   # check the wanted key index to delete in Post List
    for x in dict:
        if x == key:
            # print(x)
            return True
    return False
        
row2dict = lambda r: {c.name: str(getattr(r, c.name))  for c in r.__table__.columns if c.name != "id"}





## Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db=SQLAlchemy(app)

listofPOST=[]
direction = {"Up":0,"Down":0,"Left":0,"Right":0}


@app.route('/_get_post_json/', methods=['POST']) #direct communicate with json to store direction when tounch down
def get_post_json():    
    data = request.get_json()
    # print(data)
    direction[list(data.values())[0]]= int(check_key(data,"tounchstart") or not(check_key(data,"tounchend"))) # a + !b to compute necessary 0 or 1 condition
    print(direction)
    return jsonify(status="success", data=direction)


        

# to add plance with name,x,y,z,yaw,pitch,row
@app.route("/",methods =['Post','Get'])
def index():
    if (request.method == "POST"):
        if request.form.get("action") == "submit":
            # print(request.form)
            dictpost =request.form.to_dict()
            dictpost.pop("action",None)
            print(dictpost)
            #the loacl database
            db.session.add(place(**dictpost))
            db.session.commit()   
            #the firebase database 
            mystring = f'({dictpost["x"]},{dictpost["y"]},{dictpost["yaw"]})'  
            firedb.child("Place").update({dictpost["Place"]:mystring})  
            global listofPOST
            listofPOST = [row2dict(component) for component in db.session.query(place).all()]
            print(listofPOST)
            
            # listofPOST.append(dictpost) #list of multiple dictionary
            return render_template("index.html",Listofpost =listofPOST)  
    # print(request.form)
    listofPOST = [row2dict(component) for component in db.session.query(place).all()]       
    return render_template("index.html",Listofpost =listofPOST)

# to reach and delete the subject unwanted with radio form button
@app.route("/reach",methods=['Post','Get'])
def reach():
    if request.method == "POST":
        print(request.form.get("action"))
        if request.form.get("action") == "reach":
            # print(request.form.to_dict())
            y = request.form["movePosition"].strip("[']").split("', '")[1:]
            print(y)
            movetoedstination(y)
            return render_template("index.html", Listofpost = listofPOST, movesucess= (request.form["movePosition"]))
            #call movebase function
        if request.form.get("action") == "delete":
                delete_value = request.form["movePosition"].strip("[']").split("', '")[0]       
                print(listofPOST)
                find_deletebyvalue(listofPOST,delete_value)
                print(delete_value)
                db.session.query(place).filter_by(Place = delete_value).delete()
                db.session.commit()
                #firebase delete
                firedb.child("Place").child(str(delete_value)).remove()
                return render_template("index.html", Listofpost = listofPOST)
        
@app.route("/control")
def control():
    return render_template("control.html")

@app.route("/nav2js")
def nav2js():
    return render_template("nav2.html")

@app.route("/chartjs/",methods=['GET'])
def chartjs():
    return render_template("chartjs.html")

number=0

@app.route("/chartjsrequest",methods=['GET'])
def request_chartdata():
    if request.query_string.decode('UTF-8') == "yes":   
        global number 
        z = {"label":[],"data":[]}
        number += 1
        z["label"].append(time.ctime(time.time()))
        z["data"].append(number) 
        print(z)
        return jsonify(z)
    return jsonify({"label":[],"data":[]})
    
@app.route("/firebase")
def firebase():
    return render_template("firebase.html")


if __name__ == "__main__": 
    app.run(debug=True,host='0.0.0.0')
