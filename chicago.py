import re
import os
import json
import requests
import sqlite3
import random

#25 paintings
def get_paintings():

    #limit = 25
    #page = random.randint(0, 100)
    #url =  f"https://api.artic.edu/api/v1/artworks?page={page}&limit={limit}"

    url =  "https://api.artic.edu/api/v1/artworks"
    params = {'artwork_type_title': 'Painting', 'page': random.randint(0, 100), 'limit': 25}

    paintings = []

    response = requests.get(url, params = params)

    if response.status_code == 200:
        data = response.json()
        paintings.extend(data['data'])
    else:
        return 'Fail'
    
    return paintings