from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import secrets
import os
import smtplib
import psycopg2



app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
# DATABASE_URL: postgres://nghpgwuxrbvibr:ab9d84ab9999bd0dc8647c1c371fe85578c0c22602006158c89d4a8fa3edaeee@ec2-107-21-67-46.compute-1.amazonaws.com:5432/df628bqel4gujm
db = SQLAlchemy(app)
app.secret_key = secrets.token_hex(16)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20))
    name1 = db.Column(db.String(50))
    name2 = db.Column(db.String(50))
    name3 = db.Column(db.String(50))
    name4 = db.Column(db.String(50))
    type = db.Column(db.String(30))
    floor = db.Column(db.String(10))
    room = db.Column(db.String(10))
    night = db.Column(db.String(10))

class Password(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password17 = db.Column(db.String(10))
    password21 = db.Column(db.String(10))
    checkintime = db.Column(db.String(4))



def send_email(sender, receiver, subject, body, password, name):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender, password)

    message = f"Subject: {subject}\n\n{body} {name}"
    server.sendmail(sender, receiver, message)

    server.quit()

@app.route('/admin')
def admin():
    checkin = Password.query.filter_by(id='1').first()
    checkintime = checkin.checkintime

    return render_template('admin.html', checkin= checkintime)



@app.route('/')
def index():

    sender = "mongkingguesthouse@gmail.com"
    receiver = ["ckkjanis@gmail.com", "jack_jack0130@hotmail.com"]
    subject = "Self Check in System is being used at 2105"
    body = "Some one is using the Self Check in System"
    password = os.environ.get('GOOGLE_APP_PASSWORD')
    name = " "

    send_email(sender, receiver, subject, body, password, name)


    checkin = Password.query.filter_by(id='1').first()
    checkintime = checkin.checkintime
    #nowtime=datetime.now().strftime('%H%M')
    now = datetime.now()
    nowtime = (now+timedelta(hours=8)).strftime('%H%M')
    # nowtime = datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%H%M')
    if nowtime >= '0300' and nowtime <= checkintime:
        return render_template('notyet.html')
    else:
        return render_template('index.html')

"""

@app.route('/switch', methods=['GET', 'POST'])
def switch():
    if request.method == 'POST':
        if 'switch' in request.form and request.form['switch'] == 'on':
            session['switch'] = 'on'
        else:
            session.pop('switch', None)
    return render_template('admin.html')
    
"""

@app.route('/', methods=['GET', 'POST'])
def search_bookings():

    if request.method == 'POST':

        guest_name = request.form['search_input'].lower().replace(" ", "")
        # guest_name = guest_name.lower().replace(" ", "")  # remove spaces and convert to lowercase
        now = datetime.now()
        working_date = (now + timedelta(hours=5)).strftime("%Y-%m-%d")  # get working date
        booking = Booking.query.filter(db.or_(Booking.name1 == guest_name, Booking.name2 == guest_name, Booking.name3 == guest_name, Booking.name4 == guest_name),
                                        Booking.date == working_date).first()
        if booking:
            sender = "mongkingguesthouse@gmail.com"
            receiver = ["ckkjanis@gmail.com", "jack_jack0130@hotmail.com"]
            subject = "Someone is checking in at 2105"
            body = "Customer:"
            password = os.environ.get('GOOGLE_APP_PASSWORD')
            name = guest_name

            send_email(sender, receiver, subject, body, password, name)

            return render_template('post.html', booking=booking)




        else:
            error=1
            return render_template('index.html', error=error)

            #return "No booking found for {} on {}".format(request.form['search_input'], working_date)
    else:
        return render_template('index.html')

@app.route('/checkin/<int:floor>/<int:room>')
def checkin(floor,room):
    if floor == 17:

        return render_template('17.html', floor=floor , room=room)
    if floor == 21:
        password = Password.query.filter_by(id='1').first()
        return render_template('21.html', floor=floor, room=room, password=password.password21)

@app.route('/checkin17/<int:floor>/<int:room>')
def checkin17(floor, room):
    if floor == 21:
        return render_template('21go.html', floor=floor, room=room)

    if floor == 17:
        password = Password.query.filter_by(id='1').first()
        return render_template('17door.html', floor=floor, room=room, password=password.password17)

@app.route('/checkin17_02/<int:room>')
def checkin17_02(room):
    if room == 2:
        return render_template('17inside02.html', room=room)
    elif room == 8:
        return render_template('17inside02.html', room=room)
    else:
        return render_template('17inside.html', room=room)

@app.route('/complete')
def complete():

        return render_template('complete.html')




@app.route('/display')
def display():
    b = Booking.query.all()
    booking = sorted(b, reverse=True, key=lambda x: x.date)
    return render_template('display.html', booking=booking)

@app.route('/edit', methods=['POST','GET'])
def edit_post():
    if request.form.get('delete') == 'del':
        del_name = request.form['name']
        post = Booking.query.filter_by(name1=del_name).first()
        if post:
            db.session.delete(post)
            db.session.commit()
        else:
            b = Booking.query.all()
            booking = sorted(b, reverse=True, key=lambda x: x.date)
            return render_template('display.html', booking=booking)

    b = Booking.query.all()
    booking = sorted(b, reverse=True, key=lambda x: x.date)
    return render_template('display.html', booking=booking)

@app.route('/add_booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        date = request.form['date']
        name1 = request.form['name1'].lower().replace(" ", "")
        name2 = request.form['name2'].lower().replace(" ", "")
        name3 = request.form['name3'].lower().replace(" ", "")
        name4 = request.form['name4'].lower().replace(" ", "")
        type = request.form['type_input'].lower().replace(" ", "")
        floor = request.form['floor']
        room = request.form['option']
        night = request.form['night_input']
        if request.form.get('password17')  :
            password = Password.query.filter_by(id='1').first()
            password.password17=request.form['password17']
            db.session.commit()
        if request.form.get('password21')  :
            password = Password.query.filter_by(id='1').first()
            password.password21 = request.form['password21']
            db.session.commit()
        if request.form.get('checkintime')  :
            checkintime = Password.query.filter_by(id='1').first()
            checkintime.checkintime = request.form['checkintime']
            db.session.commit()


        post = Booking(date=date, name1=name1, name2=name2, name3=name3, name4=name4, type=type, floor=floor, room=room, night=night)

        db.session.add(post)
        db.session.commit()

        return redirect(url_for('admin'))

    return render_template('admin.html')


@app.route('/1710')
def index17():

    sender = "mongkingguesthouse@gmail.com"
    receiver = ["ckkjanis@gmail.com", "jack_jack0130@hotmail.com"]
    subject = "Self Check in System is being used at 1710"
    body = "Some one is using the Self Check in System"
    password = os.environ.get('GOOGLE_APP_PASSWORD')
    name = " "

    send_email(sender, receiver, subject, body, password, name)


    checkin = Password.query.filter_by(id='1').first()
    checkintime = checkin.checkintime
    #nowtime=datetime.now().strftime('%H%M')
    now = datetime.now()
    nowtime = (now+timedelta(hours=8)).strftime('%H%M')
    # nowtime = datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%H%M')
    if nowtime >= '0300' and nowtime <= checkintime:
        return render_template('notyet.html')
    else:
        return render_template('index17.html')
@app.route('/1710', methods=['GET', 'POST'])
def search_bookings17():

    if request.method == 'POST':

        guest_name = request.form['search_input'].lower().replace(" ", "")
        # guest_name = guest_name.lower().replace(" ", "")  # remove spaces and convert to lowercase
        now = datetime.now()
        working_date = (now + timedelta(hours=5)).strftime("%Y-%m-%d")  # get working date
        booking = Booking.query.filter(db.or_(Booking.name1 == guest_name, Booking.name2 == guest_name, Booking.name3 == guest_name, Booking.name4 == guest_name),
                                        Booking.date == working_date).first()
        if booking:
            sender = "mongkingguesthouse@gmail.com"
            receiver = ["ckkjanis@gmail.com", "jack_jack0130@hotmail.com"]
            subject = "Someone is checking in at 1710"
            body = "Customer:"
            password = os.environ.get('GOOGLE_APP_PASSWORD')
            name = guest_name

            send_email(sender, receiver, subject, body, password, name)

            return render_template('post17.html', booking=booking)

        else:
            error=1
            return render_template('index17.html', error=error)

if __name__ == '__main__':
    app.run(debug=False)
