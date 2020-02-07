import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app=Flask(__name__)
#home page
@app.route("/")
def home():
    return(
        f'Welcome to the home page <br/>'
        f'Links<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/  enter date in yyyy-mm-dd format<br/>')


#returns json of precipition data
@app.route('/api/v1.0/precipitation')
def precipitation():
   session=Session(engine)
   result=session.query(Measurement.date,Measurement.prcp).all()
   session.close()

   precip=[]

   for date,prcp in result:
       precip_dict={}
       precip_dict['date']=date
       precip_dict['prcp']=prcp
       precip.append(precip_dict)
   return jsonify(precip)

#returns json of station names
@app.route('/api/v1.0/stations')
def station():
    session=Session(engine)
    result=session.query(Station.name).all()
    session.close()
    names=list(np.ravel(result))
    return jsonify(names)


#returns json of temp data from last year
@app.route('/api/v1.0/tobs')
def temperature():
   session=Session(engine)
   result=session.query(Measurement.date,Measurement.tobs).filter(Measurement.date>'2016-08-23').all()
   session.close()

   temp=[]

   for date,tobs in result:
       temp_dict={}
       temp_dict['date']=date
       temp_dict['tobs']=tobs
       temp.append(temp_dict)
   return jsonify(temp)

#returns json of temp max, min, and average from evry date between start date to end of data
@app.route('/api/v1.0/<start>')
def start_avg(start):
    #create datetime object from <start>
    start_date_str=start.split('-')
    start_year_int=int(start_date_str[0])
    start_month_int=int(start_date_str[1])
    start_day_int=int(start_date_str[2])
    start_date=dt.date(start_year_int,start_month_int,start_day_int)
    session=Session(engine)
    #create datetime object from last date in data
    last_date=session.query(func.strftime("%Y-%m-%d",Measurement.date)).order_by(Measurement.date.desc()).first()
    end_date=last_date[0].split('-')
    end_year_int=int(end_date[0])
    end_month_int=int(end_date[1])
    end_day_int=int(end_date[2])
    end_date=dt.date(end_year_int,end_month_int,end_day_int)
    #create list of date between start and last date
    date_list=[]
    date=start_date
    while date!=end_date:
        date_list.append(date)
        date=date+dt.timedelta(days=1)
    date_list.append(end_date)
    #formatted list for query
    formated_date_list=[]
    for date in date_list:
        date=date.strftime('%Y-%m-%d')
        formated_date_list.append(date)    
    temp_list=[]
    #loop through formatted date list to query for average, max, and min temps each date
    for date in formated_date_list:
        result= session.query(Measurement.date,func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date==date).all()
        temps=result[0]
        temp_list.append(temps)
    return jsonify(temp_list)

#returns json of temp max, min, and average of every date between a start date to an end date
@app.route('/api/v1.0/<start>/<end>')
def start_end_avg(start,end):
    #start date datetime object
    start_date_str=start.split('-')
    start_year_int=int(start_date_str[0])
    start_month_int=int(start_date_str[1])
    start_day_int=int(start_date_str[2])
    start_date=dt.date(start_year_int,start_month_int,start_day_int)
    #end date datetime object
    end_date_str=end.split('-')
    end_year_int=int(end_date_str[0])
    end_month_int=int(end_date_str[1])
    end_day_int=int(end_date_str[2])
    end_date=dt.date(end_year_int,end_month_int,end_day_int)
    session=Session(engine)
    #list of dates between start date and end date
    date_list=[]
    date=start_date
    while date!=end_date:
        date_list.append(date)
        date=date+dt.timedelta(days=1)
    date_list.append(end_date)
    formated_date_list=[]
    for date in date_list:
        date=date.strftime('%Y-%m-%d')
        formated_date_list.append(date)    
    temp_list=[]
    #loop through date list to query for avg, max, and min temps between start and end date
    for date in formated_date_list:
        result= session.query(Measurement.date,func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date==date).all()
        temps=result[0]
        temp_list.append(temps)
    return jsonify(temp_list)

if __name__ == "__main__":
    app.run(debug=True)
