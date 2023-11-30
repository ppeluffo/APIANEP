#!/home/pablo/Spymovil/python/proyectos/APIANEP/venv/bin/python3
'''
Loop infinito en que lee datos a travez de la API datos y los inserta en
la base pgsql local, en la tabla 'historicos'.
De este modo recrea la BD de Spymovil.
Otro proceso, 1 vez por hora lee la tabla de configuraciones y actualiza la local.
Mientras hallan datos, los lee cada 10 segundos, para no apretar al sistema.
'''

import os
import time
import signal
from multiprocessing import Process
import sys
import datetime as dt
import requests
import db
from dbmodels import Datos

SLEEP_TIME = int(os.environ.get('SLEEP_TIME',60))
APIDATOS_HOST = os.environ.get('APIDATOS_HOST','192.168.0.8')
APIDATOS_PORT = os.environ.get('APIDATOS_PORT','5300')
APIDATOS_USERKEY = "BIP55C97EKB1FCOGHBQQ"

VERSION = 'R001 @ 2023-11-21'

VALID_IDS = ['ANEP001','ANEP002']

def clt_C_handler(signum, frame):
    sys.exit(0)

def read_data_chunk():
    '''
    Lee de la API DATOS un paquete de datos. Obtengo una lista de listas, donde estas ultimas
    son: [fechaData, fechaSys, unit_id, medida, valor]
    [
        ['06/23/2023, 04:47:29', '06/23/2023, 04:49:02', 'ARROZUR01', 'q0', 38.46],
        ['06/23/2023, 04:47:29', '06/23/2023, 04:49:02', 'ARROZUR01', 'bt', 0.36],
        ['06/23/2023, 04:48:11', '06/23/2023, 04:49:02', 'SPY003', 'pA', -2.5],
        ['06/23/2023, 04:48:11', '06/23/2023, 04:49:02', 'SPY003', 'pB', -2.5],
        ['06/23/2023, 04:48:11', '06/23/2023, 04:49:02', 'SPY003', 'bt', 12.168]
    ]

    Esta lista es la que retorno.
    '''
    url = f'http://{APIDATOS_HOST}:{APIDATOS_PORT}/apidatos/datos'
    params={'user':APIDATOS_USERKEY}
    try:
        req=requests.get(url=url,params=params,timeout=10)
    except Exception as e:
        print(f"read_data_chunk exception {e}. Exit")
        return []
    
    if req.status_code != 200:
        print('(30x) BKPROCESS_ERR010: bkprocess_read_data_chunk ERR: !!!')
        return []
    #
    # Retorno la lista de datos recibida. Cada datos es un dict
    jd_rsp = req.json()
    l_datos = jd_rsp['l_datos']
    return l_datos

def filter_lines( l_datos ):
    '''
    Recibimos una lista de lista de datos. Filtramos por los id de ANEP y
    devolvemos una lista de lista con solo los datos seleccionados
    '''
    l_filter_data = []
    for line in l_datos:
        if line[2] in VALID_IDS:
            l_filter_data.append(line)
    return l_filter_data

def insert_data( boundle_list ):
    '''
    Esta funcion recibe una lista [fechaData, fechaSys, unit_id, medida, valor] con 
    datos a insertar y hace las inserciones en la BD usando el ORM de SQLalchemy.
    [
        ['06/23/2023, 04:47:29', '06/23/2023, 04:49:02', 'ARROZUR01', 'q0', 38.46],
        ['06/23/2023, 04:47:29', '06/23/2023, 04:49:02', 'ARROZUR01', 'bt', 0.36],
        ['06/23/2023, 04:48:11', '06/23/2023, 04:49:02', 'SPY003', 'pA', -2.5],
        ['06/23/2023, 04:48:11', '06/23/2023, 04:49:02', 'SPY003', 'pB', -2.5],
        ['06/23/2023, 04:48:11', '06/23/2023, 04:49:02', 'SPY003', 'bt', 12.168]
    ]
    '''
    start_time = time.time()
    nro_items = len(boundle_list)
    print(f"ANEP DATALOADER: ITEMS={nro_items}")

    session = db.Session()
    for line in boundle_list:
        #print(line)
        fechadata,fechasys,dlgid,tag,value = line
        try:
            py_fechadata = datetime.datetime.strptime(fechadata,'%m/%d/%Y, %H:%M:%S')
            py_fechasys = datetime.datetime.strptime(fechasys,'%m/%d/%Y, %H:%M:%S')
        except ValueError as err:
            print(f"ERROR de conversion de fecha: {err}")
            continue
        #
        dataline = Datos(fechadata=py_fechadata, fechasys=py_fechasys, equipo=dlgid, tag=tag, valor=value)
        session.add(dataline)
    session.commit()

    elapsed = (time.time() - start_time)
    print(f"(310) ANEP DATALOADER: END. (elapsed={elapsed})")
    sys.stdout.flush()

def backup_data():
    '''
    Funcion que lee datos desde la API y los inserta en 
    la tb_historico.
    '''
    l_datos = read_data_chunk()
    l_datos = filter_lines(l_datos)

    if len(l_datos) > 0:
        p1 = Process(target = insert_data, args = (l_datos,))
        p1.start()
    #

if __name__ == '__main__':

    signal.signal(signal.SIGINT, clt_C_handler)

    print("ANEP_DATALOADER Starting...")
    print(f'-SLEEP_TIME={SLEEP_TIME}')
    print(f'-APIDATOS={APIDATOS_HOST}/{APIDATOS_PORT}')

    # Espero para siempre
    while True:
        print('Running...')
        backup_data()
        time.sleep(SLEEP_TIME)