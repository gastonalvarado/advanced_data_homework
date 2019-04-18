###################################################################################################

# import dependencies 
import datetime as dt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Hawaii.sqlite?check_same_thread=False")
#engine = create_engine('sqlite:////var/www/homepage/blog.db?check_same_thread=False')
# reflect the database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

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
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )
#########################################################################################
#    * Query for the dates and precipitation observations from the last year.
#           * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
#           * Return the json representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of rain fall for prior year"""
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    rain = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > last_year).\
        order_by(Measurement.date).all()

# Create a list of dicts with `date` and `prcp` as the keys and values
    rain_totals = []
    for result in rain:
        row = {}
        row["date"] = result.date
        row["prcp"] = result.prcp
        rain_totals.append(row)

    return jsonify(rain_totals)

#########################################################################################
#Return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    return jsonify(stations.to_dict())
#########################################################################################
#    * Query for the dates and temperature observations from the last year.
#           * Convert the query results to a Dictionary using `date` as the key and `tobs` as the value.
#           * Return the json representation of your dictionary.

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperatures for prior year"""
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temperature = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > last_year).\
        order_by(Measurement.date).all()

# Create a list of dicts with `date` and `tobs` as the keys and values
    temperature_totals = []
    for result in temperature:
        row = {}
        row["date"] = result.date
        row["tobs"] = result.tobs
        temperature_totals.append(row)

    return jsonify(temperature_totals)
#########################################################################################
 # go back one year from start date and go to end of data for Min/Avg/Max temp   

@app.route("/api/v1.0/<start>/<end>")
def trip1(start,end):

    end =  dt.date(2017, 8, 23)
    last_year = dt.timedelta(days=365)
    start = end-last_year
    
    trip_data_min= session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip_data_avg= session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip_data_max= session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    keydict={}
    keydict["TMIN"] = trip_data_min[0]
    keydict["TAVG"] = trip_data_avg[0]
    keydict["TMAX"] = trip_data_max[0]
   
   
    return jsonify(keydict)

#########################################################################################
 # go back one year from start date and get Min/Avg/Max temp     
    
@app.route("/api/v1.0/<start>")
def trip2(start):

    start_date= dt.date(2016, 3, 12)
    
    trip_data_min= session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    trip_data_avg= session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    trip_data_max= session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    
    keydict={}
    keydict["TMIN"] = trip_data_min[0]
    keydict["TAVG"] = trip_data_avg[0]
    keydict["TMAX"] = trip_data_max[0]
    
    return jsonify(keydict)

#########################################################################################

if __name__ == "__main__":
    app.run(debug=True)
