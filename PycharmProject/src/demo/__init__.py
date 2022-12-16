import os

import requests

from utility import get_project_folder

IP_MASTER = "http://127.0.0.1:8000"


def print_result(response):
    print("Status_code: " + str(response.status_code))
    print(response.text)


def get_resource(url, sent_json):
    if sent_json:
        response = requests.get(url, json=sent_json)
    else:
        response = requests.get(url)
    print_result(response)


def post_resource(ip_address, filename):
    with open(os.path.join(get_project_folder(), filename), 'rb') as file:
        response = requests.post(ip_address, files={'file': file})
        print_result(response)