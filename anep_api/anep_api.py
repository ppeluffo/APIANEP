#!/home/pablo/Spymovil/python/proyectos/APICOMMSV3/venv/bin/python3
# #!/home/pablo/Spymovil/python/proyectos/APIANEP/venv/bin/python3
"""
API para proveer datos del prototipo de ANEP a QLICK.
Generamos 2 entry point:
- Uno en el que vamos dando de a 5000 datos en forma consecutiva.
  Debo llevar una marca del ultimo registro que dí.
- Otro que me pide el ID, fecha_ini,fecha_fin y entrego solo esos
  datos si son menos de 5000.

Debemos tener autentificacion BASICA

https://stackoverflow.com/questions/9474397/formatting-sqlalchemy-code

"""

import os
import logging
from flask import Flask, request, jsonify,  Response
from flask_restful import Resource, Api, reqparse
from flask_httpauth import HTTPBasicAuth
from sqlalchemy import and_, or_, not_
import datetime as dt
import db
from dbmodels import Datos, ControlAcceso

MAX_LINES = os.environ.get('MAX_LINES','100')

API_VERSION = 'R001 @ 2023-11-27'

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()

USER_DATA = {
    "QLICK": "Pexco599",
    "PABLO": "Pexco123"
}

@auth.verify_password
def verify_password(username, password):
    if not (username and password):
        return False
    return USER_DATA.get(username) == password

class Ping(Resource):
    '''
    Prueba la conexion a la SQL
    '''
    @auth.login_required
    def get(self):
        ''' Retorna la versión. Solo a efectos de ver que la api responda
        '''
        return {'rsp':'OK','version':API_VERSION },200

class Help(Resource):
    '''
    Clase informativa
    '''
    @auth.login_required
    def get(self):
        ''' Retorna la descripcion de los metodos disponibles
        '''
        d_options = {
            'GET /apianep/ping':'Prueba la respuesta',
            'GET /apianep/help':'Esta pantalla de ayuda',
            'GET /apianep/download':'Devuelve todos los datos',
            'GET /apianep/filter':'Permite seleccionar dlgid,start,end',
        }
        return d_options, 200

class Download(Resource):
    ''' 
    Devuelve hasta 5000 registros en modo csv
    '''
    @auth.login_required
    def get(self):
        '''
        '''
        try:
            # Las consultas siempre devuelven un result_proxy
            access_rows = db.session.query(ControlAcceso).filter(ControlAcceso.access_token == auth.current_user()).limit(1).all()
        except Exception as e:
            print(f"ApiANEP Error: Download::get {e}")
            return {'Rsp':'ERROR'}, 404
        
        if not access_rows:
            return {'Rsp':'ERROR: usuario desconocido'}, 404
        #
        access_rcd = access_rows[0]
        last_row = access_rcd.last_row
        print(f"DEBUG: Last Row={last_row}")
        # Consulto la BD
        datos_rows = db.session.query(Datos).filter(Datos.id > last_row).limit(MAX_LINES).all()
        # Armo el CSV. Puede no tener lineas ( vacio )
        csv_data = ""
        nro_lines = 0
        for rcd in datos_rows:
            csv_data += f"{rcd}\n"
            nro_lines += 1
        #
        # Actualizo el ultimo registro
        if nro_lines > 0:
            print(f"DEBUG nro_lines={nro_lines}")
            print(f"DEBUG last_line={datos_rows[-1]}")
            last_read_row = datos_rows[-1].id
            print(f"DEBUG last_read_row={last_read_row}")
            access_rcd.last_row = last_read_row
        else:
            print('No lines for read')
        db.session.commit()
        #
        response = Response(csv_data, content_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=datos.csv"
        return response

class Filter(Resource):
    ''' 
    Devuelve hasta 5000 registros en modo csv
    '''
    @auth.login_required
    def get(self):
        '''
        Consulta con filtro de dlgid, fecha_inicio, fecha_fin.
        El limite maximo de registros es 5000
        '''
        parser = reqparse.RequestParser()
        parser.add_argument('dlgid',type=str, location='args')
        parser.add_argument('start',type=str, location='args')
        parser.add_argument('end',type=str, location='args')
        args = parser.parse_args()
        #
        # Genero la consulta
        query = db.session.query(Datos)
        if args['dlgid']:
            query = query.filter(Datos.equipo == args['dlgid'])
        #
        if args['start']:
            query = query.filter(Datos.fechadata >= args['start'])

        if args['end']:
            query = query.filter(Datos.fechadata <= args['end'])

        alldata = query.limit(MAX_LINES).all()
        csv_data = ""
        for rcd in alldata:
            csv_data += f"{rcd}\n"

        response = Response(csv_data, content_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=datos.csv"
        return response
    
api.add_resource( Ping, '/apianep/ping')
api.add_resource( Help, '/apianep/help')
api.add_resource( Download, '/apianep/download')
api.add_resource( Filter, '/apianep/filter')

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.logger.info( f'Starting API_ANEP' )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5022, debug=True)

