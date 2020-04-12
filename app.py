from flask import Flask
from flask import render_template, redirect, request, flash, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import pymysql
#import secrets
import os

dbuser = os.environ.get('DBUSER')
dbpass = os.environ.get('DBPASS')
dbhost = os.environ.get('DBHOST')
dbname = os.environ.get('DBNAME')

#conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.dbuser, secrets.dbpass, secrets.dbhost, secrets.dbname)
conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(dbuser, dbpass, dbhost, dbname)



app = Flask(__name__)
app.config['SECRET_KEY']='Ab4536hfhf'
app.config['SQLALCHEMY_DATABASE_URI'] = conn
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
db = SQLAlchemy(app)


class ajatnieks(db.Model):
    #__tablename__ = 'results'
    champ_id = db.Column(db.Integer, primary_key=True)
    champ_name = db.Column(db.String(255))
    champ_difficulty = db.Column(db.Integer)
    champ_affiliation = db.Column(db.String(255))
    champ_Damage = db.Column(db.String(255))

    def __repr__(self):
        return "id: {0} | Champion name: {1} | Champion Difficulty: {2} | Champion Affiliation: {3} | Champion Damage Type: {4}".format(self.champ_id, self.champ_name, self.champ_difficulty, self.champ_affiliation, self.champ_Damage)


class ChampForm(FlaskForm):
    champ_id = IntegerField('Champion ID:')
    champ_name = StringField('Champion Name:', validators=[DataRequired()])
    champ_difficulty = StringField('Champion Difficulty:')
    champ_affiliation = StringField('Champion Affiliation:')
    champ_Damage = StringField('Champion Damage Type:')


@app.route('/')
def index():
    all_champs = ajatnieks.query.all()
    return render_template('index.html', champs=all_champs, pageTitle='Andrew\'s Champs')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        form = request.form
        search_value = form['search_string']
        search = "%{0}%".format(search_value)
        results = ajatnieks.query.filter(or_(ajatnieks.champ_name.like(search),
                                                    ajatnieks.champ_difficulty.like(search),
                                                    ajatnieks.champ_affiliation.like(search),
                                                    ajatnieks.champ_Damage.like(search))).all()
        return render_template('index.html', champs=results, pageTitle='Andrew\'s Champs', legend="Search Results")
    else:
        return redirect('/')


@app.route('/add_champ', methods=['GET', 'POST'])
def add_champ():
    form = ChampForm()
    if form.validate_on_submit():
        champ = ajatnieks(champ_name=form.champ_name.data, 
        champ_difficulty = form.champ_difficulty.data, 
        champ_affiliation = form.champ_affiliation.data,
        champ_Damage = form.champ_Damage.data)
        db.session.add(champ)
        db.session.commit()
        return redirect('/') 

     
    return render_template('add_champ.html', form=form, pageTitle='Add A New champion',
                            legend="Add A New champion")


@app.route('/delete_champ/<int:champ_id>', methods=['GET', 'POST'])
def delete_champ(champ_id):
    if request.method == 'POST': 
        champ = ajatnieks.query.get_or_404(champ_id)
        db.session.delete(champ)
        db.session.commit()
        return redirect("/")
    else: 
        return redirect("/")


@app.route('/champion/<int:champ_id>', methods=['GET','POST'])
def get_champ(champ_id):
    champ = ajatnieks.query.get_or_404(champ_id)
    return render_template('champ.html', form=champ, pageTitle='Champion Details', legend="Champion Details")

@app.route('/champion/<int:champ_id>/update', methods=['GET','POST'])
def update_champ(champ_id):
    champ = ajatnieks.query.get_or_404(champ_id) 
    form = ChampForm()

    if form.validate_on_submit():
        champ.champ_name = form.champ_name.data
        champ.champ_difficulty = form.champ_difficulty.data
        champ.champ_affiliation = form.champ_affiliation.data
        champ.champ_Damage = form.champ_Damage.data
        db.session.commit()
        return redirect(url_for('get_champ', champ_id = champ.champ_id))

    form.champ_id.data = champ.champ_id
    form.champ_name.data = champ.champ_name
    form.champ_difficulty.data = champ.champ_difficulty
    form.champ_affiliation.data = champ.champ_affiliation
    form.champ_Damage.data = champ.champ_Damage
    return render_template('update_champ.html', form=form, pageTitle='Update Champion', legend="Update A Champion")

if __name__ == '__main__':
    app.run(debug=True)