import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# set up the database
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect the database into our classes
Base = automap_base()
Base.prepare(engine, reflect=True)

# create a variable for each class to be referenced later
Measurement = Base.classes.measurement
Station = Base.classes.station

# create a session link from python to our database
session = Session(engine)

# define flask app
app = Flask(__name__)

# define routes
@app.route('/')
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')

@app.route('/api/v1.0/precipitation')
def precipitation():
    # calculate the date one year ago from the most recent date in the db
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # write a query to get the date and precipitation for the previous year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    # use jsonify() to format results into a JSON structred file
    precip = {date: prcp for date, prcp in precipitation}
    
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    # write query to get all stations in db
    results = session.query(Station.station).all()

    # unravel results by converting them into a list (using np.ravel()), then into json
    stations = list(np.ravel(results))

    return jsonify(stations=stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # using the primary station, get all temp observations from just the prev year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

    # convert to list, then to json
    temps = list(np.ravel(results))

    return jsonify(temps=temps)


# statistics route
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

#add start and end paramters
def stats(start=None, end=None):
    #select min, max, and avg temps
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # asterisk indicates there will be multiple results for the query
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps=temps)
    
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    temps = list(np.ravel(results))
    return jsonify(temps)