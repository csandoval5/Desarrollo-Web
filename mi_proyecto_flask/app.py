from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

class ContactForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    email = StringField('Correo Electrónico', validators=[DataRequired()])
    message = StringField('Mensaje', validators=[DataRequired()])
    submit = SubmitField('Enviar')

@app.route('/')
def home():
    return "Hola mundo, esta es mi tarea de la semana 11"

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/Cristian')
def usuario():
    return 'Bienvenido, Cristian Sandoval!'

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data
        return redirect(url_for('resultado', name=name, email=email, message=message))
    return render_template('formulario.html', form=form)

@app.route('/resultado')
def resultado():
    name = request.args.get('name')
    email = request.args.get('email')
    message = request.args.get('message')
    return render_template('resultado.html', name=name, email=email, message=message)

if __name__ == '__main__':
    app.run(debug=True)
