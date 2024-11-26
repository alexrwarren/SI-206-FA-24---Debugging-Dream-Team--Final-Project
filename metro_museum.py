import re
import os
import json
import requests
import sqlite3
import random

# get 25 (or however many) paintings from API
def get_paintings(limit=100):
    url = "https://collectionapi.metmuseum.org/public/collection/v1/search"
    
    # Set parameters to search for paintings only
    params = {
        'medium': 'Paintings',  # Filter for paintings
        'q': '*'
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        total_paintings = data['total']
        object_ids = data['objectIDs']
        
        if total_paintings > limit:
            return random.sample(object_ids, limit)
        else:
            return object_ids[:limit]
    else:
        return None
    

# set up the database
def set_up_database(database_name):
    # set path, create conn and cur and return them
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + database_name)
    cur = conn.cursor()
    return cur, conn

# set up the MET table (rename function to match museum name)
def create_MET_table(cur, conn):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS MET (
        id_key INTEGER PRIMARY KEY,
        title TEXT UNIQUE,
        creation_year INTEGER,
        gender_id INTEGER
    )
    """)
    conn.commit()


# insert API data into the database
def insert_paintings_into_MET(paintings, cur, conn):
    new_paintings = []
    
    for painting_id in paintings:
        # Fetch individual painting data
        url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{painting_id}"
        response = requests.get(url)
        
        if response.status_code == 200:
            painting = response.json()

            acceptable_classifications = ['Paintings', 'Paintings-Decorative', 'Bark-Paintings']

            if painting.get('classification') not in acceptable_classifications:
                continue
            
            if painting['objectEndDate'] < 1800 or not painting['objectEndDate']:
                continue
            
            # Extract title
            if painting['title']:
                title = re.findall(r"[^(]+", painting['title'])[0].strip()
                #print(title)
            else:
                title = None
            
            # Extract creation year
            creation_year = painting['objectEndDate']
            
            # Extract artist gender (1 = female)
            if painting["artistGender"]:
                gender_id = 1
                #print(gender_id)
            else:
                gender_id = 0
            
            # Insert data into the MET table
            cur.execute("INSERT OR IGNORE INTO Met (title, creation_year, gender_id) VALUES (?, ?, ?)", 
                        (title, creation_year, gender_id))
            
            if cur.rowcount > 0:
                new_paintings.append(painting_id)
                print(f"Added painting: '{title}' to database")
            else:
                print(f"Painting: '{title}' already in database")
            
            if len(new_paintings) == 25:
                break
    
    print(f'Added {len(new_paintings)} new paintings to database')
    conn.commit()
    
    return new_paintings

def main():
    cur, conn = set_up_database("Museums.db")
    create_MET_table(cur, conn)


    # print total number of paintings in db right now
    cur.execute("SELECT COUNT(*) FROM Met")
    paintings_inserted = cur.fetchone()[0]
    print("current painting count: " + str(paintings_inserted))
    
    # call API to get new paintings and insert them into the db
    insert_paintings_into_MET(get_paintings(), cur, conn)
    
    # print total number of paintings in db after calling API
    cur.execute("SELECT COUNT(*) FROM Met")
    paintings_inserted = cur.fetchone()[0]
    print("new painting count: " + str(paintings_inserted))
    conn.close()
    

main()
