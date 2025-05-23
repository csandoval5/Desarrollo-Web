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
login_manager.login_view = 'login'

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

# Modelo para la tabla de productos
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.String(300), nullable=True)

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

# Ruta principal redirigiendo al login si el usuario no está autenticado
@app.route('/')
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('index.html')

# Ruta index
@app.route('/index')
@login_required
def index():
    return render_template('index.html')

# Ruta about
@app.route('/about')
@login_required
def about():
    return render_template('about.html')

# Ruta personalizada
@app.route('/Cristian')
@login_required
def usuario():
    return 'Bienvenido, Cristian Sandoval!'

# Ruta del formulario de contacto
@app.route('/formulario', methods=['GET', 'POST'])
@login_required
def formulario():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data

        # Guardar datos en TXT, JSON y CSV
        with open('datos/datos.txt', 'a') as file:
            file.write(f'Nombre: {name}, Correo: {email}, Mensaje: {message}\n')

        data = {"Nombre": name, "Correo": email, "Mensaje": message}
        with open('datos/datos.json', 'a') as file:
            json.dump(data, file)
            file.write('\n')

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
@login_required
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
            return redirect(url_for('index'))
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
    flash('Sesión cerrada exitosamente.', 'info')
    return redirect(url_for('login'))

# Ruta para verificar la conexión a MySQL
@app.route('/test_db')
@login_required
def test_db():
    try:
        conexion = db.engine.connect()
        return "¡Conexión exitosa a la base de datos!"
    except Exception as e:
        return f"Error al conectar con la base de datos: {e}"

# CRUD de productos protegido
@app.route('/crear', methods=['GET', 'POST'])
@login_required
def crear_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        descripcion = request.form['descripcion']

        if not nombre or not precio:
            flash('El nombre y el precio son obligatorios.', 'danger')
        else:
            nuevo_producto = Producto(nombre=nombre, precio=float(precio), descripcion=descripcion)
            db.session.add(nuevo_producto)
            db.session.commit()
            flash('Producto creado exitosamente.', 'success')
            return redirect(url_for('ver_productos'))

    return render_template('crear.html')

@app.route('/productos')
@login_required
def ver_productos():
    productos = Producto.query.all()
    return render_template('productos.html', productos=productos)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.precio = request.form['precio']
        producto.descripcion = request.form['descripcion']
        db.session.commit()
        flash('Producto actualizado exitosamente.', 'success')
        return redirect(url_for('ver_productos'))
    return render_template('editar.html', producto=producto)

@app.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado exitosamente.', 'info')
    return redirect(url_for('ver_productos'))

if __name__ == '__main__':
    app.run(debug=True)
