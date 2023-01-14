
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from datetime import datetime
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
#Base.prepare(autoload_with=engine)
Base.prepare(engine, reflect=True)

print(Base.classes.keys())
# Create our session (link) from Python to the DB, hawaii.sqlite
session = Session(engine)

# Save reference to the tables
Stations = Base.classes.station
measurement = Base.classes.measurement

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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB, hawaii.sqlite
    session = Session(engine)

    #Convert the query results from your precipitation analysis
    # (i.e. retrieve only the last 12 months of data) 
    # to a dictionary using date as the key and prcp as the value.
    # Starting from the most recent data point in the database. 
    most_recent = session.query(measurement.date).order_by(measurement.date.desc()).first()
    most_recent = datetime.strptime(most_recent[0], '%Y-%m-%d') #Result: datetime.datetime(2017, 8, 23, 0, 0)

    # Calculate the date one year from the last date in data set.
    year_ago = most_recent - dt.timedelta(days=365) #Result: datetime.datetime(2016, 8, 23, 0, 0)

    #Convert year_ago back to string in YYYY-MM-DD format
    year_ago = year_ago.strftime("%Y-%m-%d")

    # Perform a query to retrieve the data and precipitation scores and then close the session
    prcp_results = engine.execute('SELECT date, prcp FROM measurement WHERE date >= ?', year_ago).fetchall()
    session.close()

        # Create a dictionary from the row data and append to a list of prcp_data
    prcp_data = []
    for date, prcp in prcp_results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB, hawaii.sqlite
    session = Session(engine)

    #To return a JSON list of stations from the dataset
    # First, Perform a query to retrieve the list of stations and then close the session
    huts_results = engine.execute('SELECT DISTINCT station.station FROM station JOIN measurement ON station.station = measurement.station').fetchall()
    session.close()

    #convert to list and jsonify
    all_stations = list(np.ravel(huts_results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB, hawaii.sqlite
    session = Session(engine)

    #Query the dates and temperature observations of the 
    #most-active station for the previous year of data.
    
    ######GET THE LAST 12 MONTHS OF DATES#########
    # Starting from the most recent data point in the database. 
    most_recent = session.query(measurement.date).order_by(measurement.date.desc()).first()
    most_recent = datetime.strptime(most_recent[0], '%Y-%m-%d') #Result: datetime.datetime(2017, 8, 23, 0, 0)

    # Calculate the date one year from the last date in data set.
    year_ago = most_recent - dt.timedelta(days=365) #Result: datetime.datetime(2016, 8, 23, 0, 0)

    #Convert year_ago back to string in YYYY-MM-DD format
    year_ago = year_ago.strftime("%Y-%m-%d")


    ######GET THE MOST ACTIVE STATION OF THE LAST 12 MONTHS#########
    active_station_query = engine.execute('SELECT station \
                                            FROM measurement \
                                            WHERE date >= ? \
                                            GROUP BY station \
                                            ORDER BY count(*) DESC \
                                            LIMIT 1', year_ago).fetchall()

    active_station = active_station_query[0][0]
    
    # Perform a query to retrieve the data and precipitation scores and then close the session
    tobs_results = engine.execute('SELECT date, tobs FROM measurement WHERE station LIKE ? AND date >= ?', active_station, year_ago).fetchall()
    
    #Then close the session
    session.close()

    #convert to list and jsonify
    active_tobs = list(np.ravel(tobs_results))
    return jsonify(active_tobs)

#@app.route("/api/v1.0/<start>")
#def start_date(start):
#    # Create our session (link) from Python to the DB, hawaii.sqlite
#    session = Session(engine)
    
#    #run the query
    
    #Then close the session
#    session.close()
    
    
 #   return jsonify(active_tobs)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
