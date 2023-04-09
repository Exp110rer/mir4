import requests.auth
from requests import request
from requests.exceptions import ConnectionError
from requests.auth import HTTPBasicAuth
import os
import datetime

DRIVE = 'c:\\'
ROOT = 'RUTNT.apps'
APP = 'VALIDATION'
APP_VER = '1.0'
# URL = 'https://ihubzone.ru/hub_api/validation/'
URL = 'http://127.0.0.1:8000/hub_api/validation'
SPUTNIK_URL = 'https://sputnik.global.batgen.com/api/v1/Check/'
# SPUTNIK_URL = 'https://sputnikdev.global.batgen.com/api/v1/Check/'


def get_log_file():
    path = os.path.join(DRIVE, ROOT, APP)
    if os.path.exists(path):
        return os.path.join(path, f"{APP}_{str(datetime.datetime.now()).replace(':', '-').replace(' ', '_')}.log")
    else:
        os.makedirs(path)
        return os.path.join(path, f"{APP}_{str(datetime.datetime.now()).replace(':', '-').replace(' ', '_')}.log")


def write_log_file(log_file, message, status='OK'):
    with open(log_file, 'a') as file_obj:
        file_obj.write(f'{str(datetime.datetime.today())} ---> {status} <--- {message}\n')


AUTH = HTTPBasicAuth('sputnik', 'Spassword1')
LOG_FILE = get_log_file()


def get_order_list():
    try:
        write_log_file(LOG_FILE, 'LIST operation started', status='LIST:     OK')
        req = request(method='get', url=f'{URL}/list', auth=AUTH, verify=False)
    except Exception as error:
        write_log_file(LOG_FILE, error, 'LIST:     ERROR')
        return None
    else:
        if req.status_code == 200:
            write_log_file(LOG_FILE, 'LIST operation completed', status='LIST:     OK')
            return req.json()
        else:
            write_log_file(LOG_FILE, f"{req.status_code}: {req.text}", status='LIST:    WARNING')
            return None


def get_order_details(order_id):
    try:
        req = request(method='get', url=f'{URL}/retrieve/{order_id}', auth=AUTH, verify=False)
    except Exception as error:
        write_log_file(LOG_FILE, error, 'RETRIEVE: ERROR')
        return None
    else:
        if req.status_code == 200:
            return req.json()
        else:
            write_log_file(LOG_FILE, f"{req.status_code}: {req.text}", status='RETRIEVE: WARNING')
            return None


def update_order_uuid(order_id, validation_uuid):
    try:
        req = request(method='put', url=f'{URL}/uuidupdate/{order_id}/', auth=AUTH,
                      json={'validation_uuid': validation_uuid})
    except Exception as error:
        write_log_file(LOG_FILE, error, 'UUID_UPD: ERROR')
        return None
    else:
        if req.status_code == 200:
            write_log_file(LOG_FILE, f"UUID for order_id {order_id} has been updated", 'UUID_UPD: OK')
            return 1
        else:
            write_log_file(LOG_FILE, f"{req.status_code}: {req.text}", status='UUID_UPD: WARNING')
            return None


def validation_order_update(order_id, data):
    try:
        req = request(method='post', url=f'{URL}/valupdate/', auth=AUTH, json=data)
    except Exception as error:
        write_log_file(LOG_FILE, error, 'VAL_UPD:  ERROR')
        return None
    else:
        if req.status_code == 200:
            write_log_file(LOG_FILE, f"VALIDATION for order_id {order_id} has been updated", 'VAL_UPD:  OK')
            return req.text
        else:
            write_log_file(LOG_FILE, f"{req.status_code} - {req.text} - for order_id {order_id}", 'VAL_UPD:  WARNING')
            return None


def send_order_to_sputnik(data, order_id):
    try:
        req = request(method='post', url=SPUTNIK_URL, json=data, verify=False)
    except Exception as error:
        write_log_file(LOG_FILE, error, 'toCHECK:  ERROR')
        return None
    else:
        write_log_file(LOG_FILE, f"Request to Sputnik sent for order_id {order_id}", 'toCHECK:  OK')
        return req.text.replace('"', '')


def get_validation_from_sputnik(validation_uuid, order_id):
    try:
        write_log_file(LOG_FILE, f"Validation check to Sputnik sent for order_id {order_id}", 'frCHECK:  OK')
        req = request(method='get', url=f"{SPUTNIK_URL}{validation_uuid}", verify=False)
    except Exception as error:
        write_log_file(LOG_FILE, error, 'frCHECK:  ERROR')
        return None
    else:
        if req.status_code == 200:
            write_log_file(LOG_FILE, f"Validation check for order_id {order_id} has been received.", 'frCHECK:  OK')
            return req.json()
        else:
            write_log_file(LOG_FILE, f"Validation check for order_id {order_id} has not been received.",
                           'frCHECK:  WARNING')
            return None


def request_to_sputnik(orders_list):
    for order in orders_list:
        if order['validation_uuid'] is None:
            data = get_order_details(order['id'])
            uuid = send_order_to_sputnik(data, order['id'])
            if data and uuid:
                update_order_uuid(order['id'], uuid)
            else:
                write_log_file(LOG_FILE, 'Data for order or from Sputnik is Null', 'toSPUTN:  ERROR')


def response_from_sputnik(orders_list):
    for order in orders_list:
        if order['validation_uuid'] and order['status'] != 4:
            data = get_validation_from_sputnik(order['validation_uuid'], order['id'])
            if data:
                data['id'] = order['id']
                validation_order_update(order['id'], data)


def main():
    write_log_file(LOG_FILE, 'START processing .........', status='*********')

    orders_list = get_order_list()
    if orders_list:
        request_to_sputnik(orders_list)

    orders_list = get_order_list()
    if orders_list:
        response_from_sputnik(orders_list)


main()
