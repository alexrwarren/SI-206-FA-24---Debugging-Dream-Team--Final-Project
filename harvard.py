import re
import os
import json
import requests
import sqlite3
import random

#25 paintings
def get_paintings():

    page = random.randint(0,100)

    key = 'c3ba3791-48c2-42a6-b592-6b8b7b26aebd'
    url =  f"https://api.harvardartmuseums.org/object?apikey={key}"

    params = {'size': 25, 'classification': 'Paintings', 'page': page}

    paintings = []

    response = requests.get(url, params=params)

    if response.status_code == 200:
        print('yes')
        data = response.json()
        paintings.extend(data['records'])
    else:
        return 'Fail'
    
    return paintings

def create_database(databasename):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/' + databasename)
    cur = conn.cursor()
    return cur, conn

def create_harvard_table(cur, conn):
    cur.execute('''
                CREATE TABLE IF NOT EXISTS Harvard 
                (id_key INTEGER PRIMARY KEY, 
                title TEXT UNIQUE, 
                creation_year INTEGER,
                height_cm FLOAT)
                ''')
    return None
    
def insert_paintings_into_harvard(paintings, cur, conn):
    
    # keeps track of paintings inserted into the table
    new_paintings = []
    
    # go through each painting
    for painting in paintings:
        #print(f'this work is in classiciation: {painting['classification']}')
        if painting['title']:
            title = re.findall(r"[^(]+", painting['title'])[0]
        else:
            title = None
            
        if painting['dateend']:
            if painting['dateend'] >= 1800:
                creation_year = painting['dateend'] 
            else:
                continue
        else:
            continue
        
        if painting['dimensions']:
            #print(painting['dimensions'])
            height_cm = re.findall(r'\d+[.]?\d+', painting['dimensions'])[0]
            #print(height_cm)
            height_cm = float(height_cm)
        else:
            height_cm = None
            
        cur.execute('''
                        INSERT OR IGNORE INTO Harvard
                        (title, creation_year, height_cm)
                        VALUES (?,?,?)
                        ''',
                        (title, creation_year, height_cm)
                        )
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
    cur, conn = create_database("Museums.db")
    create_harvard_table(cur, conn)

    # print total number of paintings in db right now
    cur.execute("SELECT COUNT(*) FROM Harvard")
    paintings_inserted = cur.fetchone()[0]
    print("current painting count: " + str(paintings_inserted))
    
    # call API to get new paintings and insert them into the db
    insert_paintings_into_harvard(get_paintings(), cur, conn)
    
    # print total number of paintings in db after calling API
    cur.execute("SELECT COUNT(*) FROM Harvard")
    paintings_inserted = cur.fetchone()[0]
    print("new painting count: " + str(paintings_inserted))
    conn.close()
    
main()