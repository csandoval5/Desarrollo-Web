from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import json
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo para la base de datos
class Contacto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(500), nullable=False)

# Crear las tablas en la base de datos
with app.app_context():
    db.create_all()

# Formulario de contacto
class ContactForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    email = StringField('Correo Electrónico', validators=[DataRequired()])
    message = StringField('Mensaje', validators=[DataRequired()])
    submit = SubmitField('Enviar')

# Ruta principal
@app.route('/')
def home():
    return "Hola mundo, esta es mi tarea de la semana 12"

# Ruta index
@app.route('/index')
def index():
    return render_template('index.html')

# Ruta about
@app.route('/about')
def about():
    return render_template('about.html')

# Ruta personalizada
@app.route('/Cristian')
def usuario():
    return 'Bienvenido, Cristian Sandoval!'

# Ruta del formulario
@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data

        # Guardar datos en TXT
        with open('datos/datos.txt', 'a') as file:
            file.write(f'Nombre: {name}, Correo: {email}, Mensaje: {message}\n')

        # Guardar datos en JSON
        data = {"Nombre": name, "Correo": email, "Mensaje": message}
        with open('datos/datos.json', 'a') as file:
            json.dump(data, file)
            file.write('\n')

        # Guardar datos en CSV
        with open('datos/datos.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([name, email, message])

        # Guardar datos en SQLite
        nuevo_contacto = Contacto(name=name, email=email, message=message)
        db.session.add(nuevo_contacto)
        db.session.commit()

        return redirect(url_for('resultado', name=name, email=email, message=message))
    return render_template('formulario.html', form=form)

# Ruta para mostrar resultado
@app.route('/resultado')
def resultado():
    name = request.args.get('name')
    email = request.args.get('email')
    message = request.args.get('message')
    return render_template('resultado.html', name=name, email=email, message=message)

# Ruta para leer datos desde un archivo TXT
@app.route('/leer_txt')
def leer_txt():
    with open('datos/datos.txt', 'r') as file:
        data = file.readlines()
    return render_template('mostrar.html', data=data)

# Ruta para leer datos desde un archivo JSON
@app.route('/leer_json')
def leer_json():
    data_list = []
    with open('datos/datos.json', 'r') as file:
        for line in file:
            data_list.append(json.loads(line))
    return render_template('mostrar.html', data=data_list)

# Ruta para leer datos desde un archivo CSV
@app.route('/leer_csv')
def leer_csv():
    data_list = []
    with open('datos/datos.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            data_list.append(row)
    return render_template('mostrar.html', data=data_list)

# Ruta para leer datos desde SQLite
@app.route('/leer_sqlite')
def leer_sqlite():
    contactos = Contacto.query.all()  # Obtener todos los registros
    return render_template('mostrar_sqlite.html', contactos=contactos)

if __name__ == '__main__':
    app.run(debug=True)

