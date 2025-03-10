import pymysql

def obtener_conexion():
    conexion = pymysql.connect(
        host='localhost',
        user='root',
        password='Web123456789',
        database='desarrollo_web'
    )
    return conexion
