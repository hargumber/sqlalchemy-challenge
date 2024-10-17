import numpy as np
import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///challenge-10/surfups/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect = True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################d

@app.route("/")
def welcome():
    
    return (
        
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/<start_date><br/>"
        f"/api/v1.0/start/<start_date>/end/<end_date><br/>"
    )
###
#Landing page
#@app.route("/")
#def home():
 #   print("Server received request for 'Home' page...")
 #   return("Welcome to the 'Home' page!")
###

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

 #Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
    # Find the most recent date in the data set
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = dt.datetime.strptime(recent_date[0], "%Y-%m-%d").date()
    # Calculate the date one year from the last date in data set.
    date_last_one_year = recent_date - dt.timedelta(days=365)
    
    # Retrieve the last 12 months of precipitation data
    results_precipitaion = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23').order_by(Measurement.date).all()

    # close the session 
    session.close()

    # Create a dictionary
    date_precipitation = []
    for date, prcp in results_precipitaion:
        date_precipitaion_dict = {}
        date_precipitaion_dict["date"] = date
        date_precipitaion_dict["precipitaion"] = prcp
        date_precipitation.append(date_precipitaion_dict)

    # Jasonify the dictionary
    return jsonify(date_precipitation)

#################################################
# /api/v1.0/stations Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Return a JSON list of stations from the dataset.
    # Query station
    station_list = session.query(Station.station).all()

    # close the session 
    session.close()

    #Convert list of tuples into normal list
    station_list_normal = list(np.ravel(station_list))

    # Return the JSON list of stations.
    return jsonify(station_list_normal)

    

####################################################
#/api/v1.0/tobs Query the dates and temperature observations of the most-active station for the previous year of data.

# Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():


#Query the dates and temperature observations of the most-active station for the previous year of data. Return a JSON list of temperature observations for the previous year.

    # Create our session (link) from Python to the DB
    session = Session(engine)


    # Design a query to find the most active station
    sel = [Measurement.station,
        func.count(Measurement.station)]
    most_active_station = session.query(*sel).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()

    # Design the query to find the dates and temperature observations of the most-active station for the previous year of data
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = dt.datetime.strptime(recent_date[0], "%Y-%m-%d").date()
    # Calculate the date one year from the last date in data set.
    date_last_one_year = recent_date - dt.timedelta(days=365)
    prev_year_date_temp = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station.station,
    Measurement.date >= date_last_one_year).all()

    # close the session 
    session.close()

    #Convert list of tuples into normal list
    prev_year_date_temp_list = list(np.ravel(prev_year_date_temp))

    # Return a JSON list of temperature observations for the previous year
    return jsonify(prev_year_date_temp_list)

####################################################
#/api/v1.0/<start> and /api/v1.0/<start>/<end>

#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.

#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.

#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.


###########
### For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date."""

@app.route("/api/v1.0/start/<start_date>", methods = ['GET'])
def start(start_date):

    # Create our session (link) from Python to the DB
    session = Session(engine)
# Convert the string date to a datetime object
    start_date= dt.datetime.strptime(start_date, '%Y-%m-%d')


    sel = [func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)]
    start_temp = session.query(*sel).filter(Measurement.date>= start_date).all()
    # Flatten the results into a list        
    start_temp_list = list(np.ravel(start_temp))
 # close the session 
    session.close()

    return jsonify(start_temp_list)

   


###########
# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route('/api/v1.0/start/<start_date>/end/<end_date>', methods = ['GET'])
def start_end(start_date,end_date):

    # Create our session (link) from Python to the DB
    session = Session(engine)

  # Convert the string dates to datetime objects
    start_date = dt.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')
  
    # Query to get min, max, and avg temperatures
    sel = [func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)]
    start_end_temp = session.query(*sel).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

    # Flatten the results into a list    
    start_end_temp_list = list(np.ravel(start_end_temp))

# close the session 
    session.close()

    return jsonify(start_end_temp_list)




#############

if __name__ == "__main__":
    app.run(debug=True)