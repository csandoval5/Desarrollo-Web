from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Hola mundo, esta es mi tarea de la semana 9"

@app.route('/Cristian')
def usuario():
    return 'Bienvenido, Cristian Sandoval!'

if __name__ == '__main__':
    app.run(debug=True)
