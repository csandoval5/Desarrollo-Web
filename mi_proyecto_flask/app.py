from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Configuración de la base de datos MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Web123456789@localhost/desarrollo_web'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Inicialización de Flask-Login y Flask-Bcrypt
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Ruta de la vista de inicio de sesión

# Modelo para la tabla de contactos
class Contacto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(500), nullable=False)

# Modelo para la tabla de usuarios
class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Crear las tablas en la base de datos
with app.app_context():
    db.create_all()

# Cargar usuario desde Flask-Login
@login_manager.user_loader
def cargar_usuario(user_id):
    return Usuario.query.get(int(user_id))

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

# Ruta del formulario de contacto
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

        # Guardar datos en MySQL
        nuevo_contacto = Contacto(name=name, email=email, message=message)
        db.session.add(nuevo_contacto)
        db.session.commit()

        return redirect(url_for('resultado', name=name, email=email, message=message))
    return render_template('formulario.html', form=form)

# Ruta para mostrar resultado del formulario
@app.route('/resultado')
def resultado():
    name = request.args.get('name')
    email = request.args.get('email')
    message = request.args.get('message')
    return render_template('resultado.html', name=name, email=email, message=message)

# Ruta de registro de usuarios
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        nuevo_usuario = Usuario(username=username, password=password)
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash('Usuario registrado exitosamente', 'success')
        return redirect(url_for('login'))
    return render_template('registro.html')

# Ruta de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        usuario = Usuario.query.filter_by(username=username).first()

        if usuario and bcrypt.check_password_hash(usuario.password, password):
            login_user(usuario)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('perfil'))
        else:
            flash('Credenciales incorrectas', 'danger')
    return render_template('login.html')

# Ruta protegida (perfil)
@app.route('/perfil')
@login_required
def perfil():
    return render_template('perfil.html', username=current_user.username)

# Ruta para cerrar sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('login'))

# Ruta para verificar la conexión a MySQL
@app.route('/test_db')
def test_db():
    try:
        conexion = db.engine.connect()
        return "¡Conexión exitosa a la base de datos!"
    except Exception as e:
        return f"Error al conectar con la base de datos: {e}"

if __name__ == '__main__':
    app.run(debug=True)
