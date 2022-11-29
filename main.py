########## ----- MODULE IMPORTATION ----- ##########

import datetime # for streak days counter
from tabulate import tabulate # for beautiful help menu
import mysql.connector as sql # for recording the data
from config import HOST,USER,PASS,DATABASE # for importing the variables

########## ----- MYSQL CONNECTION ----- ##########

c = sql.connect(
    host=HOST,
    user=USER,
    passwd=PASS,
    database=DATABASE
    ) # connection object

k = c.cursor() # mysql cursor

########## ----- MISC SETUP ----- ##########

k.execute("SELECT * FROM STREAKS")
rows_streaks = k.fetchall() # all the rows data from streaks

k.execute("SELECT * FROM BROKEN")
rows_broken = k.fetchall() # all the rows data from broken

ID=len(rows_streaks) + len(rows_broken) # so that no duplicate IDs exist
NOW = datetime.datetime.now() # today's date with time
TODAY = NOW.date() # today's date only

########## ----- DEFINITION OF FUNCTIONS ----- ##########

def start(WHAT,WHY): # to start a streak
    global ID
    ID+=1
    ITEMS=(ID,WHAT,WHY,str(TODAY))
    k.execute(f"INSERT INTO STREAKS VALUES{ITEMS}")
    c.commit()
    print(f'Streak for {WHAT} started!')

def add(WHAT,WHY,WHEN): # to add a streak by giving already started streak's date
    global ID
    ID+=1
    ITEMS=(ID,WHAT,WHY,WHEN)
    k.execute(f"INSERT INTO STREAKS VALUES{ITEMS}")
    c.commit()
    print(f'Streak for {WHAT} added!')

def breaks(WHICH): # to break the streak by transferring it to BROKEN list from STREAKS list
    k.execute(f"INSERT INTO BROKEN SELECT *,NOW() FROM STREAKS WHERE ID = {WHICH}") # transferring to BROKEN table
    k.execute(f"DELETE FROM STREAKS WHERE ID = {WHICH}") # deleting from STREAKS
    c.commit()

def listall(CATEG): # to list all the attributes of the tables
    if CATEG == "STREAKS":
        k.execute(f"SELECT ID,WHAT,WHY,DATEDIFF(NOW(),STARTED_ON) AS STREAK_IN_DAYS,STARTED_ON FROM {CATEG} ORDER BY STREAK_IN_DAYS DESC;")
    elif CATEG == "BROKEN":
        k.execute(f"SELECT ID,WHAT,WHY,DATEDIFF(BROKEN_ON,STARTED_ON) AS STREAK_IN_DAYS, BROKEN_ON FROM {CATEG} ORDER BY STREAK_IN_DAYS DESC;")
    rows = k.fetchall()
    print(tabulate(rows, headers=k.column_names, tablefmt='fancy_grid'))
    if len(rows) == 0:
        print("List is empty!!!")

def view(): # to list neccessory attributes only
    k.execute("SELECT WHAT,DATEDIFF(NOW(),STARTED_ON) AS STREAK_IN_DAYS FROM STREAKS ORDER BY STREAK_IN_DAYS DESC;")
    rows = k.fetchall()
    print(tabulate(rows, headers=k.column_names, tablefmt='rounded_grid'))

########## ----- HELP MENU ----- ##########

print(tabulate(
                [['For this help menu','/h or help'],
                ['To start a streak','/s or start'],
                ['To add an existing streak','/a or add'],
                ['To simple view the streaks','/v or view'],
                ['To list the streaks or broken','/l or list'],
                ['To break or delete a streak','/b or break'],
                ['To quit this app','/q or quit']],
                tablefmt='fancy_grid'
            ))

########## ----- MAIN FUNCTION ----- ##########

def main():
    while True:

        Q=input("\n" + "Enter query: ")

        try:

            if  Q == "/s" or Q == "start" :
                WHAT = str(input("What habit to create or to break (eg. Avoid Coffee): "))
                WHY = str(input("Why you want to do so (eg. Because of addiction): "))
                start(WHAT, WHY)

            elif  Q == "/a" or Q == "add" :
                WHAT = str(input("What habit to create or to break (eg. Avoid Coffee): "))
                WHY = str(input("Why you want to do so (eg. Because of addiction): "))
                WHEN = str(input("When did you started (in YYYY-MM-DD): "))
                add(WHAT, WHY, WHEN)

            elif Q == "/v" or Q == "view":
                view()

            elif  Q == "/l" or Q == "list" :
                print(tabulate([
                    ['To list running streaks', '/r or running'],
                    ['To list broken streaks', '/bn or broken']],
                    tablefmt="rounded_grid"
                ))
                T = str(input("Enter Query [list]: "))
                if T == '/r' or T == 'running':
                    print('\n' + "List for Running Streaks ")
                    listall("STREAKS")
                elif T == '/bn' or T == 'broken':
                    listall("BROKEN")

            elif Q == '/l/r' or Q == 'running':
                    print('\n' + "List for Running Streaks ")
                    listall("STREAKS")

            elif Q == '/l/bn' or Q == 'broken':
                    listall("BROKEN")

            elif Q == "/b" or Q == "break" :
                k.execute("SELECT *,DATEDIFF(NOW(),STARTED_ON) AS STREAK_IN_DAYS FROM STREAKS ORDER BY STREAK_IN_DAYS DESC;")
                rows = k.fetchall()
                print(tabulate(rows, headers=k.column_names, tablefmt='fancy_grid'))
                WHICH = int(input("Enter ID of the streak you want to break: "))
                breaks(WHICH)

            elif Q == "/h" or Q == "help" :
                print(tabulate(
                        [['For this help menu','/h or help'],
                        ['To start a streak','/s or start'],
                        ['To add an existing streak','/a or add'],
                        ['To simple view the streaks','/v or view'],
                        ['To list the streaks or broken','/l or list'],
                        ['To break or delete a streak','/b or break'],
                        ['To quit this app','/q or quit']],
                    tablefmt='fancy_grid'
                ))

            elif Q == "/q" or Q == "quit":
                break

            else:
                print('\n' + 'Wrong argument passed!' + '\n')
                continue

        except: # to except errors
                print(EOFError())
                print('\n' + 'Oops! Something went wrong, please try again...' + '\n')

########## ----- MAIN FUNCTION CALLING ----- ##########

main() # to run the whole program

########## ----- THE END ----- ##########
########## ----- THANK YOU ----- ##########

"""

CREDITS:

HARSHDEEP SINGH - CODER
KESHAV SINGH - CODER
PRIYANSHU SHARMA - CODER
ROHAN BATRA - HELPER


THANKS TO:

SIR MUKESH (COMPUTER SCIENCE TEACHER)
PYTHON COMMUNITY
STACKOVERFLOW COMMUNITY
LINUX COMMUNITY

"""
