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

def create_database(databasename):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/' + databasename)
    cur = conn.cursor()
    return cur, conn

def create_chicago_table(cur, conn):
    cur.execute('''
                CREATE TABLE IF NOT EXISTS Chicago 
                (id_key INTEGER PRIMARY KEY, 
                title TEXT UNIQUE, 
                creation_year INTEGER,
                width_cm INTEGER)
                ''')
    
def insert_paintings_into_chicago(paintings, cur, conn):
    
    # keeps track of paintings inserted into the table
    new_paintings = []
    
    # go through each painting
    for painting in paintings:
        
        #title
        if painting['title']:
            title = painting['title']
        else:
            title = None
        
        #date end
        if painting['date_end']:
            creation_date = painting['date_end']
        else:
            creation_date = None
        
        #width
        if painting['dimensions_detail'][0]['width']:
            width_cm = painting['dimensions_detail'][0]['width']
        else:
            width_cm = None

        #add data into columns in database
        cur.execute('''
                    INSERT OR IGNORE INTO Chicago
                    (title, creation_year, width_cm)
                    VALUES (?,?,?)
                    ''',
                    (title, creation_date, width_cm)
                    )
        
        # add painting to list to keep track of new paintings added, but only if inserted
        if cur.rowcount > 0:
                new_paintings.append(painting)
                print(f"added painting title: '{title}' to database")
        else:
            print(f"painting '{title}' is already in database")

        #ensuring only 25 are added at a time
        if len(new_paintings) == 25:
            break

    print(f"Added {len(new_paintings)} new paintings to database")

    conn.commit()
    return new_paintings

def main():
    # make the db, make the table
    cur, conn = create_database("Chicago.db")
    create_chicago_table(cur, conn)
    

    # print total number of paintings in db right now
    cur.execute("SELECT COUNT(*) FROM Chicago")
    paintings_inserted = cur.fetchone()[0]
    print("current painting count: " + str(paintings_inserted))
    
    # call API to get new paintings and insert them into the db
    insert_paintings_into_chicago(get_paintings(), cur, conn)
    
    # print total number of paintings in db after calling API
    cur.execute("SELECT COUNT(*) FROM Chicago")
    paintings_inserted = cur.fetchone()[0]
    print("new painting count: " + str(paintings_inserted))
    conn.close()
    

#run this code multiple times to gather > 100 paintings
main()