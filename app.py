##################### IMPORTS #####################
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
#--------------------------------------------------

################### SQLITE QUERY ##################
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement
station = Base.classes.station
#--------------------------------------------------

################### FLASK SETUP ###################
app = Flask(__name__)

#------------------- HOME ROUTE -----------------
@app.route("/")
def homepage():
    return(
        f"<h2>Welcome to Climate API</h1>"
        f"<h3>Select from available routes: <br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs <br>"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end></h3>"
    )

#---------------- PRECIPITATION ROUTE -------------
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    year_start = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    pcp = session.query(measurement.date, measurement.prcp). filter(measurement.date >= year_start).all()
    session.close()
    precip = []
    for p in pcp:
        pcp_data = {}
        pcp_data['date'] = p[0]
        pcp_data['precipitation'] = p[1]
        precip.append(pcp_data)

    return jsonify(precip)


#------------------ STATIONS ROUTE ---------------
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations_query = session.query(station.name).all()
    session.close()
    stations= list(np.ravel(stations_query))
    return jsonify(stations)

#------------------- TOBS ROUTE ------------------
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    top_station_id =  'USC00519281'
    station_first_date = dt.date(2017,8,18)
    year_range = station_first_date - dt.timedelta(days=365)
    station_data = [measurement.date, measurement.tobs]
    tobs = session.query(*station_data).filter(measurement.station == top_station_id).filter(measurement.date >= year_range).all()
    session.close()
    tobs_data = []
    for t in tobs:
        tobs_dict = {}
        tobs_dict['date'] = t[0]
        tobs_dict['temp'] = t[1]
        tobs_data.append(tobs_dict)
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def start(start):
    #query
    session = Session(engine)
    
    TMIN =  session.query(measurement.date, func.min(measurement.tobs)).filter(measurement.date >= start).all()
    TMAX =  session.query(measurement.date, func.max(measurement.tobs)).filter(measurement.date >= start).all()
    TAVG =  session.query(measurement.date, func.avg(measurement.tobs)).filter(measurement.date >= start).all()
    
    strt = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start).all()
    session.close()

    #convert
    from_date_data = list(np.ravel(strt))
    return jsonify(from_date_data)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    
    TMIN =  session.query(measurement.date, func.min(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    TMAX =  session.query(measurement.date, func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    TAVG =  session.query(measurement.date, func.avg(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    
    end = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    session.close()

    #convert
    between_date_data = list(np.ravel(end))
    return jsonify(between_date_data)


if __name__ == "__main__":
    app.run(debug=True)
