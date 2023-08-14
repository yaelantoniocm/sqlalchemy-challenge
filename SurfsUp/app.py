# Import the necessary libraries
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
# from sqlalchemy.pool import StaticPool
# from sqlalchemy.orm import sessionmaker

from flask import Flask, jsonify

# Database configuration
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={"check_same_thread": False}, poolclass=StaticPool)

# Mirror an existing database in a new model
Base = automap_base()

# Mirror tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the database
session = Session(engine)

# Flask settings
app = Flask(__name__)

# Flask routes

# Define a function to log out at the end of each request


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.close()


@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available routes:<br/>"
        f"/precipitation - Precipitation data in the last 12 months<br/>"
        f"/stations - Station lList<br/>"
        f"/tobs - Temperature data for the most active season in the last 12 months<br/>"
        f"/start - Temperature data for the most active season in the last 12 months (Example: http://localhost:8080/2016-08-23) <br/>"
        f"/start/end - Temperature statistics in the given date range (Example: http://localhost:8080/2016-08-23/2016-08-27)"
    )

# Design a query to retrieve the last 12 months of precipitation data and plot the results


@app.route("/precipitation")
def precipitation():
    # Calculate the most recent date in the Measurement table
    latest_date = session.query(func.max(Measurement.date)).scalar()
    # Calculate the date one year back from the most recent date
    one_year_ago_date = (dt.datetime.strptime(
        latest_date, '%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')
    # Design the query to get the precipitation data in the last 12 months
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago_date).all()
    # Create a dictionary to store precipitation data by date
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

 # Design a query to get the list of stations


@app.route("/stations")
def stations():
    # Design the query to get the list of stations
    station_list = session.query(Station.station).all()
    # Convert the list of tuples to a flat list
    stations_flat = [station[0] for station in station_list]

    return jsonify(stations_flat)

# Design a query to retrieve the temperature data for the most active season in the last 12 months


@app.route("/tobs")
def tobs():
    # Calculate the most recent date in the Measurement table
    latest_date = session.query(func.max(Measurement.date)).scalar()
    # Calculate the date one year back from the most recent date
    one_year_ago_date = (dt.datetime.strptime(
        latest_date, '%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')
    # Design the query to find the most active stations
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
    # Find the most active station (the first in the list)
    most_active_station = active_stations[0][0]
    # Design the query to get the temperature data for the most active season in the last 12 months
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station,
               Measurement.date >= one_year_ago_date).all()
    # Create a dictionary to store temperature data by date

    temperature_dict = {date: tobs for date, tobs in temperature_data}

    return jsonify(temperature_dict)

# Design a query to calculate the temperature statistics from the given date to the last date in the database


@app.route("/<start>")
def temperature_stats_start(start):
    # Design the query to calculate the temperature statistics from the given date to the last date in the database
    temperature_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # Extract the values of the temperature statistics
    min_temp, max_temp, avg_temp = temperature_stats[0]

    # Create a dictionary to store temperature statistics
    temperature_stats_dict = {
        "Start Date": start,
        "Minimum temperature": min_temp,
        "maximum temperature": max_temp,
        "Average Temperature": avg_temp
    }

    return jsonify(temperature_stats_dict)

# Design a query to calculate the temperature statistics in the given date range


@app.route("/<start>/<end>")
def temperature_stats_start_end(start, end):
    # Design the query to calculate the temperature statistics in the given date range
    temperature_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start, Measurement.date <= end).all()

    # Extract the values of the temperature statistics
    min_temp, max_temp, avg_temp = temperature_stats[0]

    # Create a dictionary to store temperature statistics
    temperature_stats_dict = {
        "Start Date": start,
        "End Date": end,
        "Minimum temperature": min_temp,
        "maximum temperature": max_temp,
        "Average Temperature": avg_temp
    }

    return jsonify(temperature_stats_dict)


# Start flask aplication
if __name__ == '__main__':
    app.run(debug=True)
