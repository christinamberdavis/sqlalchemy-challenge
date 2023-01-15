
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
#print(Base.classes.keys())

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
        f"Available Routes:<br/><br/>"
        f"Return precipitation data for the last 12 months:<br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"Return a list of stations:<br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"Return date and temperature for the most active station of the last 12 months:<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"Return temp max, temp min, and temp average starting from a given date:<br/>"
        f"/api/v1.0/YYYY-MM-DD<br/><br/>"
        f"Return temp max, temp min, and temp average for a given date range:<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD<br/>"
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

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_date(start, end=None):  
    #validate that the supplied start date is in the correct format; if not, print an error
    try:
        user_format = datetime.strptime(start, '%Y-%m-%d') 
    except ValueError:
        return jsonify({"error":"Invalid start format! Use YYYY-MM-DD."})  
    
    #validate that the supplied end date (if provided) is in the correct format; if not, print an error
    if end!=None:
        try:
            user_format = datetime.strptime(end, '%Y-%m-%d') 
        except ValueError:
            return jsonify({"error":"Invalid end format! Use YYYY-MM-DD."})  

    # Create our session (link) from Python to the DB, hawaii.sqlite
    session = Session(engine)

    # query for max temp based on start date
    if end==None:
        tmax_results = engine.execute('SELECT date, tobs \
                                    FROM measurement \
                                    WHERE date > ? \
                                    ORDER BY tobs desc \
                                    LIMIT 1', start).fetchall()

        if len(tmax_results) == 0:
            return jsonify({"error":"Start date is out of range of what is available in the dataset. Try an earlier date."}) 
    
    # query for max temp based on date range
    else:
        tmax_results = engine.execute('SELECT date, tobs \
                                    FROM measurement \
                                    WHERE date > ? \
                                    AND date < ? \
                                    ORDER BY tobs desc \
                                    LIMIT 1', start, end).fetchall()

    # if the dates are out of range and do not return any data, print an error message
        if len(tmax_results) == 0:
            return jsonify({"error":"Start date is out of range of what is available in the dataset. Try an earlier date."}) 
    #put results into a dictionary in a list so that it can be jsonified
    tmax_dict =  {}
    for date,tmax in tmax_results:
        tmax_dict['date'] = date
        tmax_dict['tmax'] = tmax


    # query for minimum temp based on start date
    if end==None:
        tmin_results = engine.execute('SELECT date, tobs \
                                    FROM measurement \
                                    WHERE date > ? \
                                    ORDER BY tobs asc \
                                    LIMIT 1', start).fetchall()
    
    # query for minimum temp based on date range
    else:
        tmin_results = engine.execute('SELECT date, tobs \
                                    FROM measurement \
                                    WHERE date > ? \
                                    AND date < ? \
                                    ORDER BY tobs asc \
                                    LIMIT 1', start, end).fetchall()
    
    #put results into a dictionary in a list so that it can be jsonified
    tmin_dict = {}
    for date,tmin in tmin_results:
        tmin_dict['date'] = date
        tmin_dict['tmin'] = tmin

    
    # query for avg temp based on start date
    if end==None:
        tavg_results = engine.execute('SELECT AVG(tobs) AS "avg_temp"\
                                    FROM measurement \
                                    WHERE date > ? ', start).fetchall()
    # query for avg temp based on date range
    else:
        tavg_results = engine.execute('SELECT AVG(tobs) AS "avg_temp"\
                                    FROM measurement \
                                    WHERE date > ? AND date < ?', start, end).fetchall()
    #put results into a list 
    tavg_list =list(np.ravel(tavg_results))
    #put the list into a dictionary so that it can be jsonified
    avg_temp = {}
    for temp in tavg_list:
        avg_temp['tavg'] = temp
    
    #jsonify all 3 lists
    return jsonify(tmax_dict,tmin_dict, avg_temp)

#Because I'm on a mac, I am setting the port to 8000 to avoid access errors
if __name__ == '__main__':
    app.run(port=8000, debug=True)

