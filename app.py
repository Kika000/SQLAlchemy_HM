import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


from flask import Flask, jsonify

# database set up
engine = create_engine('sqlite:///hawaii.sqlite', echo=False)

# reflect an existing database into a new model
Base = automap_base()

# Reflect Database into ORM classes
Base.prepare(engine, reflect=True)

# Save a reference to the measurenment table as 'Measurement'
Measurement = Base.classes.measurement
# Save a reference to the station table as 'Station'
Station = Base.classes.stations

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        "Hawaii Precipitation and Weather Data<br/><br/>"
        "Pick from the available routes below:<br/><br/>"
        "Precipiation from 2016-08-23 to 2017-08-23.<br/>"
        "/api/v1.0/precipitation<br/><br/>"
        "A list of all the weather stations in Hawaii.<br/>"
        "/api/v1.0/stations<br/><br/>"
        "The Temperature Observations (tobs) from 2016-08-23 to 2017-08-23.<br/>"
        "/api/v1.0/tobs<br/><br/>"
        "Type in a single date (i.e., 2015-01-01) to see the min, max and avg temperature since that date.<br/>"
        "/api/v1.0/temp/<start><br/><br/>"
        "Type in a date range (i.e., 2015-01-01/2015-01-10) to see the min, max and avg temperature for that range.<br/>"
        "/api/v1.0/temp/<start>/<end><br/>"
    )

year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Query for the dates and temperature observations from the last year.
    Convert the query results to a Dictionary using date as the 'key 'and 'tobs' as the value."""
    session=Session(engine)

    # Retrieve the last 12 months of precipitation data
    # results = session.query(Measurement.date, Measurement.prcp).\
    #                     filter(Measurement.date >= year_ago).\
    #                     order_by(Measurement.date).all()

    precipitation_1year = session.query(Measurement.date, Measurement.prcp).\
                      filter(Measurement.date >= year_ago ).\
                      order_by(Measurement.date)

    session.close()
    # Create a dictionary from the row data and append to a list of for the precipitation data
    precipitation_data = []
    for rain_data in precipitation_1year:
        rain_data_dict = {}
        rain_data_dict["Date"] = rain_data.date
        rain_data_dict["Precipitation"] = rain_data.prcp
        precipitation_data.append(rain_data_dict)
        

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a json list of stations from the dataset."""
    
    session=Session(engine)
    # Query all the stations
    results = session.query(Station).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_stations.
    all_stations = []
    for stations in results:
        stations_dict = {}
        stations_dict["Station"] = stations.station
        stations_dict["Station Name"] = stations.name
        stations_dict["Latitude"] = stations.latitude
        stations_dict["Longitude"] = stations.longitude
        stations_dict["Elevation"] = stations.elevation
        all_stations.append(stations_dict)
    
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a json list of Temperature Observations (tobs) for the previous year"""
    # Query all the stations and for the given date. 
    results = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
                    group_by(Measurement.date).\
                    filter(Measurement.date >= year_ago).\
                    order_by(Measurement.station).all()
                    
    # Create a dictionary from the row data and append to a list of for the temperature data.
    temp_data = []
    for tobs_data in results:
        tobs_data_dict = {}
        tobs_data_dict["Station"] = tobs_data.station
        tobs_data_dict["Date"] = tobs_data.date
        tobs_data_dict["Temperature"] = tobs_data.tobs
        temp_data.append(tobs_data_dict)
    
    return jsonify(temp_data)

@app.route("/api/v1.0/temp/<start>")
def start_stats(start=None):
    """Return a json list of the minimum temperature, the average temperature, and the
    max temperature for a given start date"""
    # Query all the stations and for the given date. 
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).all()

    # Create a dictionary from the row data and append to a list of for the temperature data.
    temp_stats = []
    
    for Tmin, Tmax, Tavg in results:
        temp_stats_dict = {}
        temp_stats_dict["Minimum Temp"] = Tmin
        temp_stats_dict["Maximum Temp"] = Tmax
        temp_stats_dict["Average Temp"] = Tavg
        temp_stats.append(temp_stats_dict)
    
    return jsonify(temp_stats)

@app.route("/api/v1.0/temp/<start>/<end>")
def calc_stats(start=None, end=None):
    """Return a json list of the minimum temperature, the average temperature, 
    and the max temperature for a given start-end date range."""
    
    # Query all the stations and for the given range of dates. 
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Create a dictionary from the row data and append to a list of for the temperature data.
    begin_end_stats = []
    
    for Tmin, Tmax, Tavg in results:
        begin_end_stats_dict = {}
        begin_end_stats_dict["Minimum Temp"] = Tmin
        begin_end_stats_dict["Maximum Temp"] = Tmax
        begin_end_stats_dict["Average Temp"] = Tavg
        begin_end_stats.append(begin_end_stats_dict)
    
    return jsonify(begin_end_stats)

if __name__ == '__main__':
    app.run(debug=True)
