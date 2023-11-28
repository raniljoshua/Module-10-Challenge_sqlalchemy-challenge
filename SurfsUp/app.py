# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
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
        f"<b>Available Routes:</b><br/><br/>"
        f"<b>Precipitation:</b> <i>/api/v1.0/precipitation</i><br/>"
        f"<b>Stations</b>: <i>/api/v1.0/stations</i><br/>"
        f"<b>Temperatures for most-active station for past one year:</b> <i>/api/v1.0/tobs</i><br/>"
        f"<b>Temperature stats from start date to end of data (/start_date):</b> <i>/api/v1.0/yyyy-mm-dd</i><br/>"
        f"<b>Temperature stats from start date to end-date (/start_date/end_date):</b> <i>/api/v1.0/yyyy-mm-dd/yyyy-mm-dd</i><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value."""
    # Calculate date of 1 year ago
    year_ago = str(dt.date(2017,8,23) - dt.timedelta(days = 365))

    # Query to retrieve the date and precipitation scores
    query_result = session.query(Measurement.date,Measurement.prcp).\
        filter(Measurement.date >= year_ago).\
        order_by(Measurement.date)
    
    session.close()

    precipitation = []
    for date,prcp in query_result:
        precipitation_dict = {}
        precipitation_dict["Date"] = date
        precipitation_dict["Precipitation"] = prcp
        precipitation.append(precipitation_dict)

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query to list the stations from the dataset
    query_result = session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()
    
    session.close()

    stations = []
    for station,name,latitude,longitude,elevation in query_result:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Latitude"] = latitude
        station_dict["Longitude"] = longitude
        station_dict["Elevation"] = elevation
        stations.append(station_dict)

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query to list most-active stations
    active_stations = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    # Calculate date of 1 year ago
    year_ago = str(dt.date(2017,8,23) - dt.timedelta(days = 365))

    # Query to find date and temp observations of most-active station
    query_result = session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.station == active_stations[0][0]).\
        filter(Measurement.date >= year_ago).all()
    
    session.close()

    temperatures = []
    for date,tobs in query_result:
        temperature_dict = {}
        temperature_dict["Date"] = date
        temperature_dict["Temperature"] = tobs
        temperatures.append(temperature_dict)

    return jsonify(temperatures)


@app.route("/api/v1.0/<start>")
def temp_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query to find minimum, average, and maximum temps from start_date to end of data
    query_result = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    session.close()

    temp_stats = []
    for min,avg,max in query_result:
        temp_stat_dict = {}
        temp_stat_dict["Minimum"] = min
        temp_stat_dict["Average"] = avg
        temp_stat_dict["Maximum"] = max
        temp_stats.append(temp_stat_dict)

    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query to find minimum, average, and maximum temps from start_date to end_date
    query_result = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    session.close()

    temp_stats = []
    for min,avg,max in query_result:
        temp_stat_dict = {}
        temp_stat_dict["Minimum"] = min
        temp_stat_dict["Average"] = avg
        temp_stat_dict["Maximum"] = max
        temp_stats.append(temp_stat_dict)

    return jsonify(temp_stats)


if __name__ == '__main__':
    app.run(debug=True)