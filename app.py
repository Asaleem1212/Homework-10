# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
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
def home():
    """List all available api routes."""
    return (
        f"Welcome to the Hawaii Climate API! You'll get all the available Routes here: <br/>"
        f"<br/>"
        f"Precipitation Data for One Year:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"List of Stations:<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"Temperature Observations for One Year:<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"Temperature Statistics from the Start Date (YYYY-MM-DD):<br/>"
        f"/api/v1.0/<start><br/>"
        f"<br/>"
        f"Temperature Statistics from the Start Date to the End Date (YYYY-MM-DD):<br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")

def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query to retrieve the last 12 months of precipitation data
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    
    # Close the session
    session.close()
    
    # Create a dictionary from the row data and append to a list of all_precipitation
    precip_data = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict[date] = prcp
        precip_data.append(precip_dict)
        
    # Return the JSON representation of the dictionary
    return jsonify(precip_data)

@app.route("/api/v1.0/stations")

def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query to retrieve data for all stations
    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    
    # Close the session
    session.close()
    
    # Create a dictionary from the row data and append to a list of all_stations
    stations = []
    for station, name, latitude, longitude, elevation in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        stations.append(station_dict)

    # Return a JSON list of stations from the dataset
    return jsonify(stations)

@app.route("/api/v1.0/tobs")

def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query to retrieve the last 12 months of temperature observation data
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Query to retrieve the most active station, its date and temperature observations  
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= one_year_ago).all()
        
    # Close the session    
    session.close()
    
    # Convert to list of dictionaries to jsonify
    tobs_list = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_list.append(tobs_dict)
    
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query to retrieve TMIN, TAVG, TMAX for all dates
    Results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
        
    # Close the session
    session.close()
    
    # Convert to list of dictionaries to jsonify
    start_list = []
    for min, avg, max in Results:
        start_dict = {}
        start_dict["TMIN"] = min
        start_dict["TAVG"] = avg
        start_dict["TMAX"] = max
        start_list.append(start_dict)
        
    return jsonify(start_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query to retrieve TMIN, TAVG, TMAX from a specific start date to a specific end date
    Results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
        
    # Close the session
    session.close()
    
    # Convert to list of dictionaries to jsonify
    start_end_list = []
    for min, avg, max in Results:
        start_end_dict = {}
        start_end_dict["TMIN"] = min
        start_end_dict["TAVG"] = avg
        start_end_dict["TMAX"] = max
        start_end_list.append(start_end_dict)
        
    return jsonify(start_end_list)

if __name__ == '__main__':
    app.run(debug=True)