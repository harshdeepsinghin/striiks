########## ----- MODULE IMPORTATION ----- ##########

import datetime # for streak days counter
from tabulate import tabulate # for beautiful help menu
import mysql.connector as sql # for recording the data
from config import HOST,USER,PASS,DATABASE # for importing the variables
import random

########## ----- MYSQL CONNECTION ----- ##########

c = sql.connect(
    host=HOST,
    user=USER,
    passwd=PASS,
    database=DATABASE
    ) # connection object

k = c.cursor() # mysql cursor

########## ----- MISC SETUP ----- ##########

# k.execute("SELECT * FROM STREAKS")
# rows_streaks = k.fetchall() # all the rows data from streaks

# k.execute("SELECT * FROM BROKEN")
# rows_broken = k.fetchall() # all the rows data from broken

ID=random.randint(1000, 9999)
NOW = datetime.datetime.now() # today's date with time
TODAY = NOW.date() # today's date only

########## ----- DEFINITION OF FUNCTIONS ----- ##########

def IDC():
    k.execute(f"SELECT * FROM STREAKS WHERE ID={ID}")
    R1 = k.fetchone()
    k.execute(f"SELECT * FROM BROKEN WHERE ID={ID}")
    R2 = k.fetchone()
    if R1 or R2:
        return True

def help():
    print(tabulate(
                [['For this help menu','/h or help'],
                ['To start a streak','/s or start'],
                ['To view the streaks','/v or view'],
                ['To restart a streak','/r or restart'], 
                ['To break a streak','/b or break'],
                ['For advance help menu','/m or menu'],
                ['To quit this app','/q or quit']],
                tablefmt='fancy_grid'))

def menu():
    print(tabulate(
                [['For this advance help menu','/m or menu'],
                ['For the basic help menu','/h or help'],
                ['To start a streak','/s or start'],
                ['To add an existing streak','/a or add'],
                ['To view the streaks','/v or view'],
                ['To advance view the running or broken streaks','/l or list'],
                ['  To advance view running streaks directly','/l/s'],
                ['  To advance view broken streaks directly','/l/bn'],
                ['To restart a streak','/r or restart'], 
                ['To break a streak','/b or break'],
                ['To delete a streak from the database permanently','/d or delete'],
                ['  To delete a running streak directly','/d/s'],
                ['  To delete a broken streak directly','/d/bn'],
                ['To quit this app','/q or quit']],
                tablefmt='fancy_grid'))    

def start(WHAT,WHY): # to start a streak
    global ID
    if IDC(): # so that no duplicate IDs exist
        ID=random.randint(1000, 9999)
    ITEMS=(ID,WHAT,WHY,str(TODAY))
    k.execute(f"INSERT INTO STREAKS VALUES{ITEMS}")
    c.commit()

def add(WHAT,WHY,WHEN): # to add a streak by giving already started streak's date
    global ID
    if IDC(): # so that no duplicate IDs exist
        ID=random.randint(1000, 9999)
    ITEMS=(ID,WHAT,WHY,WHEN)
    k.execute(f"INSERT INTO STREAKS VALUES{ITEMS}")
    c.commit()

def view(): # to list neccessory attributes only
    k.execute("SELECT WHAT,DATEDIFF(NOW(),STARTED_ON) AS STREAK_IN_DAYS FROM STREAKS ORDER BY STREAK_IN_DAYS DESC;")
    rows = k.fetchall()
    print(tabulate(rows, headers=k.column_names, tablefmt='rounded_grid'))
    if len(rows) == 0:
        print("List is empty!!!")

def listall(CATEG): # to list all the attributes of the tables
    if CATEG == "STREAKS":
        k.execute(f"SELECT ID,WHAT,WHY,DATEDIFF(NOW(),STARTED_ON) AS STREAK_IN_DAYS,STARTED_ON FROM {CATEG} ORDER BY STREAK_IN_DAYS DESC;")
    elif CATEG == "BROKEN":
        k.execute(f"SELECT ID,WHAT,WHY,DATEDIFF(BROKEN_ON,STARTED_ON) AS STREAK_IN_DAYS, BROKEN_ON FROM {CATEG} ORDER BY STREAK_IN_DAYS DESC;")
    rows = k.fetchall()
    print(tabulate(rows, headers=k.column_names, tablefmt='fancy_grid'))
    if len(rows) == 0:
        print("List is empty!!!")

def restart(FROM,WHICH): # to restart the streak
    k.execute(f"UPDATE {FROM} SET STARTED_ON = \"{TODAY}\" WHERE ID = {WHICH}") # to change the date of the streak by setting the STARTED ON date to TODAY
    c.commit()

def breaks(WHICH): # to break the streak by transferring it to BROKEN list from STREAKS list
    k.execute(f"INSERT INTO BROKEN SELECT *,NOW() FROM STREAKS WHERE ID = {WHICH}") # transferring to BROKEN table
    k.execute(f"DELETE FROM STREAKS WHERE ID = {WHICH}") # deleting from STREAKS
    c.commit()

def delete(FROM,WHICH): # to delete the streak by transferring it to BROKEN list from STREAKS list
    k.execute(f"DELETE FROM {FROM} WHERE ID = {WHICH}") # deleting from STREAKS
    c.commit()



########## ----- MAIN FUNCTION ----- ##########

def main():
    help()
    while True:

        Q=input("\n" + "Enter query: ")

        try:

            if Q == "/h" or Q == "help" :
                help()

            elif Q == "/m" or Q == "menu":
                menu()

            elif  Q == "/s" or Q == "start" :
                WHAT = str(input("What habit to create or to break (eg. Avoid Coffee): "))
                WHY = str(input("Why you want to do so (eg. Because of addiction): "))
                start(WHAT, WHY)
                print(f"Streak for {WHAT} started. All the best!")

            elif  Q == "/a" or Q == "add" :
                WHAT = str(input("What habit to create or to break (eg. Avoid Coffee): "))
                WHY = str(input("Why you want to do so (eg. Because of addiction): "))
                WHEN = str(input("When did you started (in YYYY-MM-DD): "))
                add(WHAT, WHY, WHEN)
                print(f"Streak for {WHAT} added. All the best!")

            elif Q == "/v" or Q == "view":
                view()

            elif  Q == "/l" or Q == "list" :
                print(tabulate([
                    ['To list running streaks', '/s or streaks'],
                    ['To list broken streaks', '/bn or broken']],
                    tablefmt="rounded_grid"))
                T = str(input("Enter Query [list]: "))
                if T == '/s' or T == 'streaks':
                    print('\n' + "List for Running Streaks ")
                    listall("STREAKS")
                elif T == '/bn' or T == 'broken':
                    listall("BROKEN")

            elif Q == '/l/s' or Q == 'running':
                print('\n' + "List for Running Streaks ")
                listall("STREAKS")

            elif Q == '/l/bn' or Q == 'broken':
                listall("BROKEN")

            elif Q == "/r" or Q == "restart" :
                print(tabulate([
                    ['To restart a running streak', '/s or streaks'],
                    ['To restart a broken streak', '/bn or broken']],
                    tablefmt="rounded_grid"))

                T = str(input("Enter Query [restart]: "))

                if T == '/s' or T == 'streaks':
                    k.execute("SELECT *,DATEDIFF(NOW(),STARTED_ON) AS STREAK_IN_DAYS FROM STREAKS ORDER BY STREAK_IN_DAYS DESC;")
                    rows = k.fetchall()
                    print(tabulate(rows, headers=k.column_names, tablefmt='fancy_grid'))
                    WHICH = int(input("Enter ID of the streak you want to restart: "))
                    JKL = input("Are you sure to restart the streak? y/N: ") or "N"
                    if JKL == "Y" or JKL == "y":

                        k.execute(f"SELECT WHAT FROM STREAKS WHERE ID={WHICH}")
                        D = k.fetchone()
                        WHAT = D[0]
                        print(f"Streak for {WHAT} restarted. All the best!")
                        restart("STREAKS",WHICH)

                elif T == '/bn' or T == 'broken':
                    k.execute("SELECT *,DATEDIFF(NOW(),STARTED_ON) AS STREAK_IN_DAYS FROM BROKEN ORDER BY STREAK_IN_DAYS DESC;")
                    rows = k.fetchall()
                    print(tabulate(rows, headers=k.column_names, tablefmt='fancy_grid'))
                    WHICH = int(input("Enter ID of the streak you want to restart: "))
                    JKL = input("Are you sure to restart the streak? y/N: ") or "N"
                    if JKL == "Y" or JKL == "y":

                        k.execute(f"SELECT WHAT FROM BROKEN WHERE ID={WHICH}")
                        D = k.fetchone()
                        WHAT = D[0]
                        print(f"Streak for {WHAT} restarted. All the best!")
                        restart("BROKEN",WHICH)
                        k.execute(f"INSERT INTO STREAKS SELECT ID,WHAT,WHY,STARTED_ON FROM BROKEN WHERE ID = {WHICH}") # transferring to BROKEN table
                        k.execute(f"DELETE FROM BROKEN WHERE ID = {WHICH}") # deleting from STREAKS
                        c.commit()


            elif Q == "/b" or Q == "break" :
                k.execute("SELECT *,DATEDIFF(NOW(),STARTED_ON) AS STREAK_IN_DAYS FROM STREAKS ORDER BY STREAK_IN_DAYS DESC;")
                rows = k.fetchall()
                print(tabulate(rows, headers=k.column_names, tablefmt='fancy_grid'))
                WHICH = int(input("Enter ID of the streak you want to break: "))
                JKL = input("Are you sure to break the streak? y/N: ") or "N"
                if JKL == "Y" or JKL == "y":
                    breaks(WHICH)

                    k.execute(f"SELECT WHAT FROM BROKEN WHERE ID={WHICH}")
                    D = k.fetchone()
                    WHAT = D[0]
                    print(f"Streak for {WHAT} broke. Ahh! Better luck next time!")

            elif Q == "/d" or Q == "delete" :
                print(tabulate([
                    ['To delete from running streaks', '/s or streaks'],
                    ['To delete from broken streaks', '/bn or broken']],
                    tablefmt="rounded_grid"))

                T = str(input("Enter Query [delete]: "))

                if T == '/s' or T == 'streaks':
                    k.execute("SELECT *,DATEDIFF(NOW(),STARTED_ON) AS STREAK_IN_DAYS FROM STREAKS ORDER BY STREAK_IN_DAYS DESC;")
                    rows = k.fetchall()
                    print(tabulate(rows, headers=k.column_names, tablefmt='fancy_grid'))
                    WHICH = int(input("Enter ID of the streak you want to delete: "))
                    JKL = input("Are you sure to delete the streak? y/N: ") or "N"
                    if JKL == "Y" or JKL == "y":
                        k.execute(f"SELECT WHAT FROM STREAKS WHERE ID={WHICH}")
                        D = k.fetchone()
                        WHAT = D[0]
                        delete("STREAKS",WHICH)
                        print(f"Streak for {WHAT} deleted permanently!")

                elif T == '/bn' or T == 'broken':
                    k.execute("SELECT *,DATEDIFF(NOW(),STARTED_ON) AS STREAK_IN_DAYS FROM BROKEN ORDER BY STREAK_IN_DAYS DESC;")
                    rows = k.fetchall()
                    print(tabulate(rows, headers=k.column_names, tablefmt='fancy_grid'))
                    WHICH = int(input("Enter ID of the streak you want to delete: "))
                    JKL = input("Are you sure to delete the streak? y/N: ") or "N"
                    if JKL == "Y" or JKL == "y":
                        k.execute(f"SELECT WHAT FROM BROKEN WHERE ID={WHICH}")
                        D = k.fetchone()
                        WHAT = D[0]
                        delete("BROKEN",WHICH)
                        print(f"Streak for {WHAT} deleted permanently!")

            elif Q == "/q" or Q == "quit":
                print("Bye, see you again...")
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
ROHAN BATRA - TESTER


THANKS TO:

SIR MUKESH (COMPUTER SCIENCE TEACHER)
PYTHON COMMUNITY
STACKOVERFLOW COMMUNITY
LINUX COMMUNITY

"""
