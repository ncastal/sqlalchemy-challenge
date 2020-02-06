import numpy as np

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

#returns json of temp max, min, and average from a start date to end of data
@app.route('/api/v1.0/<start>')
def start_avg(start):
    session=Session(engine)
    result=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    temps=list(np.ravel(result))
    return jsonify(temps)

#returns json of temp max, min, and average from a start date to an end date
@app.route('/api/v1.0/<start>/<end>')
def start_end_avg(start,end):
    session=Session(engine)
    result=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temps=list(np.ravel(result))
    return jsonify(temps)

if __name__ == "__main__":
    app.run(debug=True)
