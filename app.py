#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from ast        import Return
from tabnanny   import check
from flask      import Flask, render_template, request, redirect, url_for, session, flash
from functools  import wraps
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging    import Formatter, FileHandler
from forms      import *
import os

import json
from sportevents    import SportEvents
from db_functions   import *
from location       import *
from send_sms       import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
#db = SQLAlchemy(app)

# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if session['loggedIn']:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


session = {
    "loggedIn": False,
    "events": SportEvents,
    "eventsJSON": json.dumps(SportEvents, default=vars)
}


@app.route('/')
@login_required
def home():
    return redirect(url_for('calendar'))


@app.route('/calendar')
@login_required
def calendar():

    user                = log_in(session['user']["_id" ], session['user']['password'])
    session['user']     = user
    session['userJSON'] = json.dumps(user, default=vars)

    return render_template('pages/home.html', session=session)


@app.route('/profile', methods = ['GET', 'POST'])
@login_required
def profile():
    
    user                = log_in(session['user']['_id'], session['user']['password'])
    session['user']     = user

    return render_template('pages/profile.html', session=session)


@app.route('/login', methods = ['GET', 'POST'])
def login():

    form = LoginForm(request.form)
    if request.method == 'POST':

        user     = log_in(form.email.data, form.password.data)

        print(user)

        if not isinstance(user, str):
            session['user']     = user
            session['loggedIn'] = True
            return redirect(url_for('calendar'))
        
        form.msg = user

    return render_template('forms/login.html', form=form)


@app.route('/register', methods = ['GET', 'POST'])
def register():

    form = RegisterForm(request.form)
    if request.method == 'POST':

        name        = form.name.data
        email       = form.email.data
        year        = form.year.data
        number      = form.number.data
        password    = form.password.data

        sign_up(name, email, year, number, password)

        form.msg = "Successfully registered as " + name
        return redirect(url_for('login'))

    return render_template('forms/register.html', form=form)


@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)


@app.route('/buy', methods = ['GET', 'POST'])
@app.route('/buy/<eventID>', methods = ['GET', 'POST'])
@login_required
def buy(eventID = ""):

    if not eventID:
        return redirect(url_for('calendar'))

    email = session['user']['_id']
    date  = sport = location = ""

    for event in session['events']:

        if event.id == eventID:
            date     = event.date
            sport    = event.sport
            location = event.loc
            break

    ticket = Ticket(email, eventID, date, sport, location, False)

    if request.method=='POST':

        add_ticket(email, ticket)
        return redirect(url_for('profile'))

    data = ticket.__dict__
    return render_template('forms/buy.html', data=data)


@app.route('/ticket/<ticketID>', methods = ['GET'])
@login_required
def ticket(ticketID = ""):

    data = ticketID
    if not ticketID:
        return redirect(url_for('profile'))

    for ticket in session['user']['tickets']:
        if ticket['tid'] == ticketID:
            data = ticket
            break

    if data == ticketID:
        return redirect(url_for('calendar'))
    return render_template('forms/details.html', data=data)


@app.route('/removeticket/<ticketID>', methods = ['POST'])
@login_required
def removeticket(ticketID = ""):

    if not ticketID:
        return redirect(url_for('calendar'))

    email  = session['user']['_id']
    ticket = Ticket("", "", "", "", "")
    ticket.tid = ticketID
    remove_ticket(email, ticket)

    return redirect(url_for('profile'))

@app.route('/locationcheck', methods = ['GET', 'POST'])
@app.route('/locationcheck/<ticketID>', methods = ['GET', 'POST'])
@app.route('/locationcheck/<ticketID>/<ans>', methods = ['GET', 'POST'])
@login_required
def locationcheck(ticketID = "", ans = ""):

    if not ticketID:
        return redirect(url_for('calendar'))

    if request.method == 'POST' and ans:
        distance = location_check_prompt(True, "Davis, CA", "kanye@ucdavis.edu", ticketID)
        flash("You are "+str(int(distance))+" miles away from the location.")
        return redirect(url_for('checkin', ticketID=ticketID))
    return render_template('forms/locationcheck.html', ticketID=ticketID)


@app.route('/checkin/<ticketID>', methods = ['GET', 'POST'])
@login_required
def checkin(ticketID = ""):

    if not ticketID:
        return redirect(url_for('calendar'))

    email  = session['user']['_id']
    ticket = Ticket("", "", "", "", "")
    ticket.tid = ticketID
    update_check_in(email, ticket)

    ticket_notification(email, ticketID, '+13233361526')

    return redirect(url_for('profile'))

# Error handlers.

@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
'''
if __name__ == '__main__':
    app.run()
'''

# Or specify port manually:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5023))
    app.run(host='0.0.0.0', port=port)