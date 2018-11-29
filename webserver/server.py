#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
import numbers
import math
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



# XXX: The Database URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "cjd2177"
DB_PASSWORD = "nn01vpi3"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"


validUser = False
uid = None


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like

  #
  # example of a database query
  #
  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
 


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html")

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/another')
def another():
  cursor = g.conn.execute("SELECT location.name, location.cross_street from location")
  names = []
  names.extend(cursor)  # can also be accessed using result[0]

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)
  return render_template("anotherfile.html", **context)

@app.route('/review')
def review():
 cur = g.conn.execute( "select users.username, review_written.post_content, review_written.rating from users inner join review_written on users.userid = review_written.userid");
 revs = []
 revs.extend(cur)
 context = dict(data = revs)
 return render_template("review.html", **context) 

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  print name
  cmd = 'INSERT INTO location(name) VALUES (:name1)';
  g.conn.execute(text(cmd), name1 = name);
  return redirect('/')
@app.route('/exploreusers')
def userpage(): 
  return render_template("userpage.html")
@app.route('/checkuser', methods = ['POST'])
def checkuser(): 
  useridtocheck = request.form['uname']
  print(useridtocheck)
  print(isinstance(useridtocheck,int))
  query_to_check_if_user_exists = "SELECT count(*), users.userid from users where users.username = :useridtocheck"
  result_of_check_query = g.conn.execute(text(query_to_check_if_user_exists), useridtocheck = useridtocheck)
  for r in result_of_check_query: 
    if (r[0] == 0):
      return render_template("errorpage.html")
    else:
      useridtocheck = r[1]
      query_to_get_user_data = "SELECT users.username from users where users.userid = :useridtocheck"
      data = []
      result_of_query_for_userdata = g.conn.execute(text(query_to_get_user_data), useridtocheck = useridtocheck)
      for r in result_of_query_for_userdata: 
        data.append(r)
      qforcuisine = "SELECT user_likes_food.cuisine from user_likes_food where user_likes_food.userid = :useridtocheck"
      userlikesdata = []
      resultofqforcuisine = g.conn.execute(text(qforcuisine), useridtocheck = useridtocheck)
      for r in resultofqforcuisine:
        userlikesdata.append(r)
      qforvisit = "select location.name, user_visit.date, user_visit.time from user_visit natural join location where user_visit.userid = :useridtocheck"
      uservisited = []
      resultofqforvisit = g.conn.execute(text(qforvisit), useridtocheck = useridtocheck)
      for r in resultofqforvisit:
        uservisited.append(r)
      qforrec = "select location.name from recommendation_given natural join location where recommendation_given.userid = :useridtocheck"
      userrec = []
      resultofqforrec = g.conn.execute(text(qforrec), useridtocheck = useridtocheck)
      for r in resultofqforrec: 
        userrec.append(r)
      qforq = " select location.name from queue_placed natural join location where queue_placed.userid = :useridtocheck"
      uq = []
      resultofqforq = g.conn.execute(text(qforq), useridtocheck = useridtocheck)
      for r in resultofqforq: 
        uq.append(r) 
      context = dict(data = data, userlikesdata = userlikesdata, uservisited = uservisited, userrec = userrec, uq = uq)
      return render_template("displayuser.html", **context)
@app.route('/writereview', methods = ['POST'])
def writerev():
  global uid
  global validUser
  if not validUser:
    return redirect('/')
  text = request.form['thereview']
  name = request.form['locname']
  d= g.conn.execute("select location.name, location.lid from location where location.name = %1;", (locname,)):
  if d[0]:
    lid = d[1]
  else:
    return render_template('errorgen.html', error = 'No such location')
  max_postid = g.conn.execute('Select MAX(location.lid) from location')[0] + 1
  cmd = 'INSERT INTO review_written VALUES (:uid, :pn, :pc, :lat, :long, :lid,:rate);'
  g.conn.execute(text(cmd), uid = newlocation, pn = max_postid, pc=text, lat = request.form['lat'], long = request.form['long'], lid = lid, rate = request.form['rate'])
  return redirect('/login')
@app.route('/reviewsearch', methods = ['POST'])
def sreview():
  search = request.form['searchname']
  cmd = 'SELECT us.username, rw.post_content, lc.name, rw.rating'
  if request.form['type'] != 1:
   cmd +=', mg.entertainment_type'
  if request.form['type'] != 2:
   cmd += ', rt.cuisine'
  cmd +=' from users us left join review_written rw on us.userid = rw.userid left join location lc on rw.lid = lc.lid'
  if request.form['type'] != 1:
   cmd +=' left join museum_gallery mg on mg.lid = lc.lid'
  if request.form['type'] != 2:
   cmd += ' left join restaurant rt on rt.lid = lc.lid'
  if request.form['kind'] = 1:
   cmd += 'WHERE us.username like :search'
  else: cmd += 'WHERE lc.name like :search'

  cmd +=';'
  data = g.conn.execute(cmd, search = search)
  header = ['Username', 'Review', 'Location', 'Rating']
  if request.form['type'] != 1:
    header.extend['Type']
  if request.form['type'] !=2:
    header.extend['Cuisine']
  context = dict(header = header, data = data)
  return render_template('results.html', **context)
@app.route('/reviewsearch', methods = ['POST'])
def sreview():
  search = request.form['searchname']
  cmd = 'SELECT us.username, rw.post_content, lc.name, rw.rating'
  if int(request.form['type']) != 1:
   cmd +=', mg.entertainment_type'
  if int(request.form['type']) != 2:
   cmd += ', rt.cuisine'
  cmd +=' from users us left join review_written rw on us.userid = rw.userid left join location lc on rw.lid = lc.lid'
  if int(request.form['type']) != 1:
   cmd +=' left join museum_gallery mg on mg.lid = lc.lid'
  if int(request.form['type']) != 2:
   cmd += ' left join restaurant rt on rt.lid = lc.lid'
  if int(request.form['kind']) = 1:
   cmd += 'WHERE us.username like :search'
  else: cmd += 'WHERE lc.name like :search'

  cmd +=';'
  data = g.conn.execute(cmd, search = search)
  header = ['Username', 'Review', 'Location', 'Rating']
  if request.form['type'] != 1:
    header.extend['Type']
  if request.form['type'] !=2:
    header.extend['Cuisine']
  context = dict(header = header, data = data)
  return render_template('results.html', **context)
@app.route('/locationsearch', methods = ['POST'])
def locsearch():
  search = request.form['searchname']
  cmd = 'SELECT lc.latitude, lc.longitude, lc.cross_street, lc.name'
  if int(request.form['type']) != 1:
   cmd +=', mg.entertainment_type'
  if int(request.form['type']) != 2:
   cmd += ', rt.cuisine'
  cmd +=' from users us left join review_written rw on us.userid = rw.userid left join location lc on rw.lid = lc.lid'
  if int(request.form['type']) != 1:
   cmd +=' left join museum_gallery mg on mg.lid = lc.lid'
  if int(request.form['type']) != 2:
   cmd += ' left join restaurant rt on rt.lid = lc.lid'
  if search: cmd += 'WHERE lc.name like :search'
  cmd +=';'
  data = g.conn.execute(cmd, search = search)
  header = ['latitude', 'longitude', 'Street', 'Name']
  if int(request.form['type']) != 1:
    header.extend['Type']
  if int(request.form['type']) !=2:
    header.extend['Cuisine']
  context = dict(header = header, data = data)
  return render_template('results.html', **context)
@app.route('/submitlocation', methods = ['POST'])
def submitlocation():
  thelocation = request.form['nameoflocation']
  print(thelocation)
  if g.conn.execute("select location.name from location where location.name = %1;", (thelocation,)):
    return render_template('errorgen.html', error = 'Cannot have duplicate location name')
  max_location = g.conn.execute('Select MAX(location.lid) from location')
  for r in max_location: 
    themaxloc = r[0]
  newlocation = themaxloc+1
  print(newlocation)
  cmd = "INSERT into location values (:lat,:long,:index,:cross_street,:thelocation1)"
  g.conn.execute(text(cmd), index = newlocation, thelocation1 = thelocation, lat = request.form['lat'], long = request.form['long'], cross_street = request.form['street'])
  return redirect('/another')
@app.route('/adduser', methods = ['POST'])
def adduser(): 
  theusername = request.form['uname']
  print(theusername)
  if g.conn.execute("select users.username from users where users.username = %1;", (theusername,)):
    return render_template('errorgen.html', error = 'Cannot have duplicate username')
  result_max = g.conn.execute('SELECT MAX(users.userid) from users')
  for r in result_max: 
    the_max_id = r[0]
  new_id = the_max_id +1
  cmd = "INSERT INTO users VALUES (:new_id, :name1)"
  g.conn.execute(text(cmd), new_id = new_id, name1 = theusername)
  return redirect('/')
@app.route('/login', methods = ['POST'])
def login():
  global uid
  global validUser
  if not validUser:
    username = request.form['name']
    print(username)
    cmd = 'SELECT count(*), users.userid FROM users WHERE users.username = :name1'
    result = g.conn.execute(text(cmd), name1 = username)
    for r in result:
      print(r[0])
      if(r[0]== 0):
       return render_template("usererror.html")
      else: 
        uid = r[1]
      validUser = True
  query_to_get_user_data = "SELECT users.username from users where users.userid = :useridtocheck"
  data = []
  result_of_query_for_userdata = g.conn.execute(text(query_to_get_user_data), useridtocheck = uid)
    data.extend(result_of_query_for_userdata)
  qforcuisine = "SELECT user_likes_food.cuisine from user_likes_food where user_likes_food.userid = :useridtocheck"
  userlikesdata = []
  resultofqforcuisine = g.conn.execute(text(qforcuisine), useridtocheck = uid)
  userlikesdata.extend(resultofqforcuisine)
  userlikesdata = list(set(userlikesdata))
  qforattractions = "SELECT user_likes_food.cuisine from user_likes_food where user_likes_food.userid = :useridtocheck"
  qforvisit = "select location.name, user_visit.date, user_visit.time from user_visit natural join location where user_visit.userid = :useridtocheck"
  uservisited = []
  resultofqforvisit = g.conn.execute(text(qforvisit), useridtocheck = uid)
  uservisited.extend(resultofqforvisit)
  qforrec = "select location.name from recommendation_given natural join location where recommendation_given.userid = :useridtocheck"
  userrec = []
  resultofqforrec = g.conn.execute(text(qforrec), useridtocheck = uid)
  userrec.extend(resultofqforrec)
  qforq = " select location.name from queue_placed natural join location where queue_placed.userid = :useridtocheck"
  uq = []
  resultofqforq = g.conn.execute(text(qforq), useridtocheck = uid)
  uq.extend(resultofqforq)
  context = dict(data = data, userlikesdata = userlikesdata, uservisited = uservisited, userrec = userrec, uq = uq)
  return render_template("reviewpage.html", **context) 

@app.route('/logout', methods = ['POST'])
def logout():
  global uid
  uid = None
  global validUser
  validUser = False
  return redirect("/")

@app.route('/prefs', methods = ['POST'])
def editprefs():
    global uid
    global validUser
    if not validUser:
      return redirect("/") #login
    cmd = ''
    if not request.form['type']:
      return render_template('errorgen.html', error = 'must have type, and if a restaurant must have cuisine')
    if request.form['type'] = "restaurant" and request.form['cuisine']:
      cmd = 'INSERT INTO user_likes_food VALUES (:cuisine, :uid);'
    cmd += 'INSERT INTO user_likes_type VALUES (:uid, :type);'
    g.conn.execute(cmd, cuisine = request.form['cuisine'], uid = uid, type = request.form['type'])
    return redirect('/login')

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
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
