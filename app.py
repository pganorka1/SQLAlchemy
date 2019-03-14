import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<h1>Available Routes:</h1><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YYYY-MM-DD<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """List precipitation for each day"""
    results = session.query(Measurement.date, Measurement.prcp).all()
    
    prcp_list = []
    for prcp in results:
        prcp_dict = {}
        prcp_dict[prcp.date] = prcp.prcp
        prcp_list.append(prcp_dict)
        
    return jsonify(prcp_list)


@app.route("/api/v1.0/stations")
def stations():
    """List all stations"""
    results = session.query(Station.station, Station.name).all()
    
    station_list = []
    for station in results:
        station_dict = {}
        station_dict["Station"] = station.station
        station_dict["Name"] = station.name
        station_list.append(station_dict)
        
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    """List daily temperature for last year"""
    latest = session.query(func.max(Measurement.date))
    latest_date = latest.one()[0]
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    year_back = latest_date - dt.timedelta(days = 365)

    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_back)

    tobs_list = []
    for tob in results:
        tob_dict = {}
        tob_dict[tob.date] = tob.tobs
        tobs_list.append(tob_dict)
        
    return jsonify(tobs_list)
        
@app.route("/api/v1.0/<start>")
def temp(start):
    """List minimum temperature, the average temperature, and the max temperature for a given start range"""
    results = session.query(func.min(Measurement.tobs).label('min'), func.avg(Measurement.tobs).label('avg'), func.max(Measurement.tobs).label('max')).\
        filter(Measurement.date >= start).all()
    
    temp_list = []
    for temp in results:
        temp_dict = {}
        temp_dict["TMIN"] = temp.min
        temp_dict["TAVG"] = temp.avg
        temp_dict["TMAX"] = temp.max
        temp_list.append(temp_dict)
        
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_range(start,end):
    """List minimum temperature, the average temperature, and the max temperature for a given start range"""
    results = session.query(func.min(Measurement.tobs).label('min'), func.avg(Measurement.tobs).label('avg'), func.max(Measurement.tobs).label('max')).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    temp_list = []
    for temp in results:
        temp_dict = {}
        temp_dict["TMIN"] = temp.min
        temp_dict["TAVG"] = temp.avg
        temp_dict["TMAX"] = temp.max
        temp_list.append(temp_dict)
        
    return jsonify(temp_list)
    
    
if __name__ == '__main__':
    app.run(debug=True)
