
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.74.246.148/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.74.246.148/proj1part2"
#
DATABASEURI = "postgresql://asd2195:8308@34.74.246.148/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
@app.before_request
def before_request():
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback; traceback.print_exc()
        g.conn = None

@app.teardown_request
def teardown_request(exception):
    try:
        g.conn.close()
    except Exception as e:
        pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

    """
    """
    print(request.args)

    cursor = g.conn.execute("SELECT * FROM Airlines")
    names = [ res for res in cursor ]
    cursor.close()
    """
    """
    cursor2 = g.conn.execute("SELECT * FROM Wk_in_Airport_Employees A, Shops S WHERE S.sname = A.sname")
    pnames = [res for res in cursor2]
    cursor2.close()

    cursor3 = g.conn.execute("SELECT * FROM Wk_Flightcrew")
    shops = [res for res in cursor3]
    cursor3.close()
    """
    """
    context = dict(data = names)
    """
    return render_template("index.html")

@app.route('/another')
def another():
    return render_template("another.html")

@app.route('/home')
def home():
    return render_template("index.html")


@app.route('/allAirlines')
def allAirlines():
    cursor = g.conn.execute('SELECT * FROM Airlines')
    try:
        results = [ res for res in cursor ]
    except:
        print("couldn't get results")
        exit()
    if len(results) == 0: 
        print("no Airlines found") 
        return render_template('another.html', error="no Airlines found")
    else:
        context = {}
        context["allAirlines"]=results
        return render_template('another.html', **context)

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    num_planes = request.form['num_planes']
    try:
        g.conn.execute('INSERT INTO Airlines(aname, num_planes) VALUES (%s, %s)', name, num_planes)
        cursor = g.conn.execute('SELECT * FROM Airlines')
        results = [res for res in cursor ]
    except:
        print("couldn't get results")
        return render_template('another.html', error="airlines exists already")
    if len(results)==0:
        print("no airlines found")
        return render_template('another.html', error="no airlines found")
    else:
        context={}
        context["airlines"] = results
        return render_template('another.html', **context)

@app.route('/newPlane', methods=['POST'])
def newPlane():
    model=request.form['model']
    capacity=request.form['capacity']
    fuel_capacity=request.form['fuel_capacity']
    ran = request.form['ran']
    try:
        g.conn.execute('INSERT INTO Plane_Models(model, capacity, fuel_capacity, range) VALUES (%s, %s, %s, %s)', model, capacity, fuel_capacity, ran)
        cursor = g.conn.execute('SELECT * FROM Plane_Models')
    
        results = [res for res in cursor ]
    except:
        print("couldn't get results")
        return render_template('another.html', error="plane already exists")
    if len(results)==0:
        print("no plane models found")
        return render_template('another.html', error="no plane models found")
    else:
        context={}
        context["models"] = results
        return render_template('another.html', **context)

@app.route('/passenger', methods=['GET'])
def passenger():
    pname = request.args.get('pname')
    cursor = g.conn.execute('SELECT * FROM Passengers_En_Route P WHERE P.pname=%s',pname)
    try:
        results = [ res for res in cursor ]
    except:
        print("couldn't get results")
        exit()
    if len(results) == 0: 
        print("no passenger found") 
        return render_template('another.html', error="no passenger found")
    else:
        context = {}
        context["passenger"]=results[0]
        return render_template('another.html', **context)

@app.route('/terminal', methods=['GET'])
def terminal():
    ename= request.args.get('ename')
    cursor =g.conn.execute('SELECT A.ename, S.sname,  S.terminal FROM Wk_in_Airport_Employees A, Shops S WHERE S.sname = A.sname AND A.ename = %s', ename)
    try:
        results = [res for res in cursor ]
    except:
        print("couldn't get results")
        exit()
    if len(results)==0:
        print("no workers found")
        return render_template('another.html', error="no worker found")
    else:
        context={}
        context["terminal"] = results[0]
        return render_template('another.html', **context)

@app.route('/pilots', methods=['GET'])
def find_pilots():
    aname=request.args.get('aname')
    cursor = g.conn.execute('SELECT F.aname, F.ename FROM Wk_Flightcrew F WHERE F.aname=%s', aname)
    try:
        results = [res for res in cursor]
    except:
        print("couldn't get results")
        exit()
    if len(results)==0:
        print("no workers found")
        return render_template('another.html', error="no worker found")
    else:
        context={}
        context["pilot"] = results
        return render_template('another.html', **context)
@app.route('/updatePlanes', methods=['POST'])
def updatePlanes():
    aname = request.form['aname']
    model = request.form['model']
    quantity = request.form['quantity']
    g.conn.execute('UPDATE Owns_Planes SET quantity = %s  WHERE aname=%s AND model=%s',quantity, aname, model)
    cursor = g.conn.execute('SELECT * FROM Owns_planes')
    try:
        results = [res for res in cursor]
    except:
        print("couldn't update")
        exit()
    if len(results)==0:
        print("no update possible")
        return render_template('another.html', error="no routes found")
    else:
        context={}
        context["newOwns"] = results
        return render_template('another.html', **context)
@app.route('/routes', methods=['GET'])
def find_routes():
    depart=request.args.get('depart')
    cursor = g.conn.execute('SELECT * FROM Routes_Flown RF WHERE RF.departure_location=%s', depart)
    try:
        results = [res for res in cursor]
    except:
        print("couldn't get results")
        exit()
    if len(results)==0:
        print("no routes found")
        return render_template('another.html', error="no routes found")
    else:
        context={}
        context["routes"] = results
        return render_template('another.html', **context)
@app.route('/owns', methods=['GET'])
def owns():
    cursor=g.conn.execute('SELECT * FROM Owns_planes')
    try:
        results = [res for res in cursor]
    except:
        print("couldn't get results")
        exit()
    if len(results)==0:
        print("no ownership found")
        return render_template('index.html', error="no ownership found")
    else:
        context={}
        context["owns"] = results
        return render_template('index.html', **context)
@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
