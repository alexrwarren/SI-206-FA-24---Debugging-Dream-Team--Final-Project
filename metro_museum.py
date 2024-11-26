import re
import os
import json
import requests
import sqlite3
import random

# get 25 (or however many) paintings from API
def get_paintings(limit=25):
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
        country TEXT,
        country_culture TEXT,
        artist_nationality TEXT,
        creation_year INTEGER,
        artist_name TEXT,
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
            
            # Extract title
            title = painting.get('title', None)
            
            # Extract creation year
            object_date = painting.get('objectDate', '')
            creation_year = None
            if object_date:
                year_match = re.search(r'\d{4}', object_date)
                if year_match:
                    creation_year = int(year_match.group())
            
            # Extract artist name
            artist_name = painting.get('artistDisplayName', None)
            
            # Extract country
            country = painting.get('country', None)

            #Extract country_culture
            country_culture = painting.get('culture', None)
            

            #Extract country_culture
            artist_nationality = painting.get('artistNationality', None)

            # Determine gender (this is a simplification, as the API doesn't provide gender directly)
            gender_id = ''
            if painting.get('artistGender') == 'female':
                gender_id = 1
            elif painting.get('artistGender') == 'male':
                gender_id = 0
            
            # Insert data into the MET table
            cur.execute("INSERT OR IGNORE INTO MET (id_key, title, country, country_culture, artist_nationality, creation_year, artist_name, gender_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                        (painting_id, title, country, country_culture, artist_nationality, creation_year, artist_name, gender_id))
            
            if cur.rowcount > 0:
                new_paintings.append(painting_id)
                print(f"Added painting: '{title}' to database")
            else:
                print(f"Painting: '{title}' already in database")
            
            if len(new_paintings) == 120:
                break
    
    print(f'Added {len(new_paintings)} new paintings to database')
    conn.commit()
    return new_paintings

def main():
    cur, conn = set_up_database("MET.db")
    cur.execute("DROP TABLE IF EXISTS MET")
    create_MET_table(cur, conn)


    # print total number of paintings in db right now
    cur.execute("SELECT COUNT(*) FROM MET")
    paintings_inserted = cur.fetchone()[0]
    print("current painting count: " + str(paintings_inserted))
    
    # call API to get new paintings and insert them into the db
    insert_paintings_into_MET(get_paintings(), cur, conn)
    
    # print total number of paintings in db after calling API
    cur.execute("SELECT COUNT(*) FROM MET")
    paintings_inserted = cur.fetchone()[0]
    print("new painting count: " + str(paintings_inserted))
    conn.close()
    

main()
