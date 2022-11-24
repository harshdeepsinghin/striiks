########## ----- MODULE IMPORTATION ----- ##########

import mysql.connector as sql
from config import HOST,USER,PASS

########## ----- MYSQL CONNECTION ----- ##########

c = sql.connect(host=HOST, user=USER, passwd=PASS) #connection
k=c.cursor()

########## ----- SETUP-ING  ----- ##########

DATABASE=str(input("Enter database name: "))
k.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE}") # database creation
c.commit()
with open('config.py', 'r+') as F: # saving the database name to config file for variable environment
    if DATABASE not in F.read():
        F.write('\n' + f"DATABASE = \"{DATABASE}\"")

k.execute(f"USE {DATABASE}")
k.execute("CREATE TABLE IF NOT EXISTS STREAKS(ID INTEGER PRIMARY KEY, WHAT VARCHAR(50),  WHY VARCHAR(100), STARTED_ON DATE)") # STREAKS table creation
k.execute("CREATE TABLE IF NOT EXISTS BROKEN(ID INTEGER PRIMARY KEY, WHAT VARCHAR(50),  WHY VARCHAR(100), STARTED_ON DATE, BROKEN_ON DATE)") # BROKEN table creation
c.commit()

print("Setup done successfully!!!" + '\n' + 'Run the program(main.py)')