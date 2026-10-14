from flask import Flask, jsonify
import importlib

app = Flask(__name__)


@app.route('/')
def inicio():
  return jsonify({
      'proyecto': 'Unidad II - Preparación de los Datos',
      'servidor': 'AWS EC2 WebserverM4',
      'rutas_disponibles': {
          '/practica1': (
              'Perfilamiento e Ingesta Multi-Fuente en AWS S3 con Python'
          ),
          '/practica2': 'Generación y Estructuración de Esquema Estrella',
          '/practica3': 'Limpieza de Datos Avanzada (KNN & IQR)',
          '/practica4': 'Generación Sintética (Faker) y Partición Estratificada',
          '/practica5': 'Pipeline ETL Automatizado a AWS S3',
      },
  })


@app.route('/practica1')
def run_p1():
  p1 = importlib.import_module('practica1')
  res = p1.ejecutar_practica1()
  return jsonify({'practica': 1, 'resultado': res})


@app.route('/practica2')
def run_p2():
  p2 = importlib.import_module('practica2')
  res = p2.ejecutar_practica2()
  return jsonify({'practica': 2, 'resultado': res})


@app.route('/practica3')
def run_p3():
  p3 = importlib.import_module('practica3')
  res = p3.ejecutar_practica3()
  return jsonify({'practica': 3, 'resultado': res})


@app.route('/practica4')
def run_p4():
  p4 = importlib.import_module('practica4')
  res = p4.ejecutar_practica4()
  return jsonify({'practica': 4, 'resultado': res})


@app.route('/practica5')
def run_p5():
  p5 = importlib.import_module('practica5')
  res = p5.ejecutar_practica5()
  return jsonify({'practica': 5, 'resultado': res})


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)