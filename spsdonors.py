import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing

# configuration
DATABASE = '/home/jherr/projects/spsdonors/spsdonors.db'
DEBUG = True
SECRET_KEY = 'development key xxx'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
# app.config.from_envvar('SPSDONORS_SETTINGS', silent=True)

def init_db():
    with closing(connect_db()) as myconn:
        with app.open_resource('spsdonors_schema.sql', mode='r') as f:
            myconn.cursor().executescript(f.read())
        myconn.commit()

@app.before_request
def before_request():
    g.conn = connect_db()

@app.teardown_request
def teardown_request(exception):
    conn = getattr(g, 'conn', None)
    if conn is not None:
        conn.close()

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.route('/', methods=['POST','GET'])
def show_entries():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    orderby=" order by donorname"
    filter=" where donorname like ? "
    thesql="select donorname, donorclassification, solicitorname, solicitoremail, solicitorphone from spsdonors"

    filterDonorName = request.values.get('searchName')
    searchButtonPressed = request.values.get('search_button')
    showAllButtonPressed = request.values.get('showall_button')

    if searchButtonPressed and filterDonorName is not None and len(filterDonorName) > 0:
      thesql += filter
      thesql += orderby

      cur = g.conn.cursor()
      cur.execute(thesql, ("%"+filterDonorName+"%",))
      entries = [ [row[0], row[1], row[2], row[3], row[4]] for row in cur.fetchall()]
      g.conn.commit()
    else:
      filterDonorName=None  # Clear search field on "Show All"
      thesql += orderby

      cur = g.conn.cursor()
      cur.execute(thesql)
      entries = [ [row[0], row[1], row[2], row[3], row[4]] for row in cur.fetchall()]
    return render_template('show_entries.html', numentries=len(entries), entries=entries, searchdefault=filterDonorName if filterDonorName else "")

@app.route('/add-entry')
def add_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return render_template('add_entries.html')

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    saveButtonPressed = request.values.get('save_button')
    if not saveButtonPressed: 
    	flash('New record entry was cancelled.')
    else:
        g.conn.execute('insert into spsdonors (donorname, donorclassification, solicitorname, solicitoremail, solicitorphone) values (?, ?, ?, ?, ?)',
	[
		request.form['donorname'],
		request.form['donorclass'],
		request.form['solicname'],
		request.form['solicemail'],
		request.form['solicphone']
	])
    	g.conn.commit()
	flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        #if request.form['username'] != app.config['USERNAME']:
        #    error = 'Invalid username'
        #elif request.form['password'] != app.config['PASSWORD']:
        #    error = 'Invalid password'
        #else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='192.168.2.127',debug='TRUE')

