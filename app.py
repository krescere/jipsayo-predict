from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import pickle
import config
import json
from apscheduler.schedulers.background import BackgroundScheduler

# init app
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=config.SQLALCHEMY_DATABASE_URI
# init database
db=SQLAlchemy()
db.init_app(app)

# all houses
houses=[]

# scheduler
sched = BackgroundScheduler(daemon=True)

# open pre-trained model
with open("./model_20230111.pickle","rb") as file:
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
    response=[]
    predict_times=model.predict(input) # 의심가는 병목 부분 1순위
    for i in range(0,len(predict_times)):
        predict_time=int(predict_times[i])
        if predict_time<=time:
            house=houses[i]
            response.append(HouseResponse(house['id'],predict_time).__dict__)
    
    # return as JSON
    return json.dumps(response)

# 부동산 갱신
@app.route('/api/v1/houses/reload')
def house_reload():
    print("houses reloaded")
    resultproxy=db.session.execute(db.select(
        House.id,
        House.latitude,
        House.longitude
        ).limit(10))
    
    # initialize
    houses.clear()
    for row in resultproxy:
        row_as_dict=row._asdict()
        print(row_as_dict)
        houses.append(row_as_dict)
    return "houses reloaded : "+str(len(houses))+" houses"

################################################################### Service
def make_predict_input(start):
    input=[]
    # 4*10^4 pandas가 더 빠르다.
    for house in houses :
        input.append([start['longitude'],start['latitude'], house['longitude'],house['latitude']])
    return input

def predict(input):
    results=model.predict(input)
    return results

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

''' with app.app_context():
    # scheduler
    sched.add_job(house_reload,'interval',seconds=10)
    sched.start()
    print("sheduler started") '''

################################################################### main
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)