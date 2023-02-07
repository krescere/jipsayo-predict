from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from numpy import sin, cos, arccos, pi
import pandas as pd
import pickle
import config
import json

# init app
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=config.SQLALCHEMY_DATABASE_URI
# init database
db=SQLAlchemy()
db.init_app(app)

# all houses (dataframe)
houses=pd.DataFrame(columns=['id','latitude','longitude'])

# open pre-trained models
with open("./model_total_bus_4.pickle","rb") as file:
        public_transport_model=pickle.load(file)
with open("./model_total_walk_2.pickle","rb") as file:
        walk_model=pickle.load(file)

################################################################## Controller
# 필터링 기능
@app.route('/api/v1/houses/filter')
def house_filter():
    # houses 가 비어있으면 초기화
    if houses.__len__()==0:
        house_reload()
    
    # get filter info
    start={'latitude':request.args.get('latitude'),
           'longitude':request.args.get('longitude')}
    time=request.args.get('time')
    time=int(time)
    
    # predict input
    input=make_predict_input(start)
    # public transport predict
    public_transport_predict(input)
    # walk predict
    walk_predict(input)
    # filter
    response=input[input["time"]<=time][["id","time"]]
    # return as JSON
    return response.to_json(orient="records")

# 부동산 갱신
@app.route('/api/v1/houses/reload')
def house_reload():
    print("houses reloaded")
    resultproxy=db.session.execute(db.select(
        House.id,
        House.latitude,
        House.longitude
        ))

    # initialize
    global houses
    houses.drop(houses.index,inplace=True)
    houses=pd.DataFrame(resultproxy.fetchall(),columns=resultproxy.keys())
    return "houses reloaded : "+str(len(houses))+" houses"

################################################################### Service
def make_predict_input(start):
    input=pd.DataFrame.copy(houses)
    input['start_경도']=float(start['longitude'])
    input['start_위도']=float(start['latitude'])
    # rename
    input.rename(columns={'latitude':'위도','longitude':'경도'},inplace=True)
    # add distance
    add_distance(input)
    return input

def public_transport_predict(input):
    input["time"]=public_transport_model.predict(input[["start_경도","start_위도","경도","위도","거리"]])
    input["time"]=input["time"].astype(int)
    
def walk_predict(input):
    apt_under_one=input[input.거리<1]
    input["walk"]=9999
    input["walk"].iloc[apt_under_one.index]=walk_model.predict(apt_under_one[["start_경도","start_위도","경도","위도","거리"]])
    input["walk"]=input["walk"].round()
    input["walk"]=input["walk"].astype(int)
    input["time"]=input[["time","walk"]].min(axis=1)

# 곡률 계산
def rad2deg(radians):
    degrees = radians * 180 / pi
    return degrees

def deg2rad(degrees):
    radians = degrees * pi / 180
    return radians

def deg2rad_sin(degrees):
    radians = degrees * pi / 180
    return sin(radians)

def deg2rad_cos(degrees):
    radians = degrees * pi / 180
    return cos(radians)

def add_distance(input):
    theta = input.start_경도 - input.경도
    dist = (input.start_위도.apply(deg2rad_sin) * input.위도.apply(deg2rad_sin)) +\
    (input.start_위도.apply(deg2rad_cos) * input.위도.apply(deg2rad_cos) * theta.apply(deg2rad_cos))
    dist = dist.apply(arccos).apply(rad2deg) * 60 * 1.1515 * 1.609344
    input["거리"] = dist

################################################################### DTO
class HouseResponse(object):
    id=""
    time=""
    def __init__(self, id, time):
        self.id = id
        self.time = time
        
################################################################### Entity
class House(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    latitude=db.Column(db.Float)
    longitude=db.Column(db.Float)

################################################################### main
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)