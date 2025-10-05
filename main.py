import pandas as pd 
import requests
import json 
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
print(API_KEY)

url = "https://www.thesportsdb.com/api/v1/json/123/lookuptable.php?l=4328&s=2024-2025"
headers = {
    "X-Auth-Token": API_KEY
}
querystring = {
   "season": 2024
}

response = requests.get(url= url, headers=headers, params=querystring)

payload = response.json()

standingslist = payload["table"]

formattet_standingslist = json.dumps(standingslist, indent=4)
print(f"\n\n\n{formattet_standingslist}")

rows = []
collum_name = ['season','position', 'team_id', 'team', 'played', 'won', 'lost', 'draw', 'goals_for', 'goals_against', 'goal_difference', 'points', 'form']
 
for club in standingslist:
    season = 2024
    position = club['intRank']
    team_id = club['idTeam']
    team = club['strTeam']
    played = club['intPlayed']
    won = club['intWin']
    lost = club['intLoss']
    draw = club['intDraw']
    goals_for = club['intGoalsFor']
    goals_against = club['intGoalsAgainst']
    goal_difference = club['intGoalDifference']
    points = club['intPoints']
    form = club['strForm']


    tuple_of_club_record = (season, position, team_id, team, played, won, lost, draw, goals_for, goals_against, goal_difference, points, form)

    rows.append(tuple_of_club_record)


print(rows)

df = pd.DataFrame(rows, columns=collum_name)

df.head(13)

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_Port = os.getenv("MYSQL_Port")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")


server_conn = mysql.connector.connect(
    host=MYSQL_HOST,
    port=MYSQL_Port,
    user="pl_app_writer",
    password="asdasd123x",
    database="PL_football",
    autocommit=False,
    raise_on_warnings=True
)

server_cursor = server_conn.cursor()
print(f"[succesful] - connected to mysql server")

server_cursor.close()
server_conn.close()


database_connection = mysql.connector.connect(

host=MYSQL_HOST,
port=MYSQL_Port,
user="pl_app_writer",
password="asdasd123x",
database="PL_football",
autocommit=False,
raise_on_warnings=True
)
cursor = database_connection.cursor()
print(f"[succesful] - connected to mysql server]")


sql_table = "standing"
cursor.execute("SHOW TABLES LIKE %s", (f"{sql_table}",))

if cursor.fetchone() is None:
    raise SystemExit(f"this table {sql_table} is not found.... please create it...")
else:
    print(f"[succes] - this tabel {sql_table} exist, godt arbjede ;)")

    user_team = "Liverpool'; DROP TABLE standing"
cursor.execute("SELECT * FROM standing WHERE team = %s", (user_team,))


#START THE UPSERT (UPDATE INSERT) OPERATION

table_collums = ['season','position', 'team_id', 'team', 'played', 'won', 'lost', 'draw', 'goals_for', 'goals_against', 'goal_difference', 'points', 'form']
 

standing_df = df[table_collums]

standings_record_tubles = standing_df.itertuples(index=False, name=None)

list_of_standing_record_tubles = list(standings_record_tubles)

UPSERT_SQL = f"""
INSERT INTO {sql_table} 
(season, position, team_id, team, played, won, lost, draw, goals_for, goals_againts, goal_difference, points, form)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    position = VALUES(position),
    team = VALUES(team),
    played = VALUES(played),
    won = VALUES(won),
    lost = VALUES(lost),
    draw = VALUES(draw),
    goals_for = VALUES(goals_for),
    goals_againts = VALUES(goals_againts),
    goal_difference = VALUES(goal_difference),
    points = VALUES(points),
    form = VALUES(form);
"""

no_of_rows_uplaoded_to_mysql = len(list_of_standing_record_tubles)

print(no_of_rows_uplaoded_to_mysql)

import mysql.connector

# Reconnect to MySQL
database_connection = mysql.connector.connect(
host=MYSQL_HOST,
port=MYSQL_Port,
user="pl_app_writer",
password="asdasd123x",
database="PL_football"
)

try:
    cursor = database_connection.cursor()
    cursor.executemany(UPSERT_SQL, list_of_standing_record_tubles)
    database_connection.commit()
    print(f"[success] - upsert attempted for {cursor.rowcount} rows")

except Exception as e:
    # Now rollback works because connection is alive
    database_connection.rollback()
    print(f"[error] - rolled back due to this ...: {e}")

finally:
    if cursor:
        cursor.close()
    if database_connection:
        database_connection.close()
    print("✅ All database connections are now closed.")