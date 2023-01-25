from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
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

# open pre-trained model
with open("./model_total_bus_1.pickle","rb") as file:
        model=pickle.load(file)

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
    # predict
    input["time"]=model.predict(input[["start_경도","start_위도","경도","위도"]])
    input["time"]=input["time"].astype(int)
    print(input.head(5))
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
    input['start_경도']=start['longitude']
    input['start_위도']=start['latitude']
    # rename
    input.rename(columns={'latitude':'위도','longitude':'경도'},inplace=True)
    return input


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