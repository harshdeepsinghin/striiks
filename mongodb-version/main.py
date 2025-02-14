########## ----- MODULE IMPORTATION ----- ##########

import datetime  # for streak days counter
from tabulate import tabulate  # for beautiful help menu
from pymongo import MongoClient  # for MongoDB connection
from dotenv import load_dotenv  # to load environment variables from .env file
import os  # to access environment variables
import random
from urllib.parse import quote_plus

########## ----- LOAD ENVIRONMENT VARIABLES ----- ##########

# Load environment variables from .env file
load_dotenv()

# Get MongoDB credentials from environment variables
USERNAME = os.getenv("MONGODB_USERNAME")
PASSWORD = os.getenv("MONGODB_PASSWORD")
CLUSTER = os.getenv("MONGODB_CLUSTER")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# Encode USERNAME and PASSWORD
ENCODED_USERNAME = quote_plus(USERNAME)
ENCODED_PASSWORD = quote_plus(PASSWORD)
print(USERNAME, PASSWORD, CLUSTER, DATABASE_NAME, sep="\n")
# Construct the MongoDB URI
MONGODB_URI = f"mongodb+srv://{ENCODED_USERNAME}:{ENCODED_PASSWORD}@cluster0.9vczn.mongodb.net/?retryWrites=true&w=majority&appName={CLUSTER}"

########## ----- MONGODB CONNECTION ----- ##########

# Connect to MongoDB using the URI from the .env file
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]  # Use the database name from the .env file
streaks_collection = db.streaks  # Collection for active streaks
broken_collection = db.broken  # Collection for broken streaks

########## ----- MISC SETUP ----- ##########

ID = random.randint(1000, 9999)
NOW = datetime.datetime.now()  # today's date with time
TODAY = NOW.date()  # today's date only

########## ----- DEFINITION OF FUNCTIONS ----- ##########

def IDC():
    if streaks_collection.find_one({"ID": ID}) or broken_collection.find_one({"ID": ID}):
        return True

def help():
    print(tabulate(
        [['For this help menu', '/h or help'],
         ['To start a streak', '/s or start'],
         ['To view the streaks', '/v or view'],
         ['To restart a streak', '/r or restart'],
         ['To break a streak', '/b or break'],
         ['For advance help menu', '/m or menu'],
         ['To quit this app', '/q or quit']],
        tablefmt='fancy_grid'))

def menu():
    print(tabulate(
        [['For this advance help menu', '/m or menu'],
         ['For the basic help menu', '/h or help'],
         ['To start a streak', '/s or start'],
         ['To add an existing streak', '/a or add'],
         ['To view the streaks', '/v or view'],
         ['To advance view the running or broken streaks', '/l or list'],
         ['  To advance view running streaks directly', '/l/s'],
         ['  To advance view broken streaks directly', '/l/bn'],
         ['To restart a streak', '/r or restart'],
         ['To break a streak', '/b or break'],
         ['To delete a streak from the database permanently', '/d or delete'],
         ['  To delete a running streak directly', '/d/s'],
         ['  To delete a broken streak directly', '/d/bn'],
         ['To quit this app', '/q or quit']],
        tablefmt='fancy_grid'))

def start(WHAT, WHY):  # to start a streak
    global ID
    if IDC():  # so that no duplicate IDs exist
        ID = random.randint(1000, 9999)
    streak = {
        "ID": ID,
        "WHAT": WHAT,
        "WHY": WHY,
        "STARTED_ON": str(TODAY)
    }
    streaks_collection.insert_one(streak)

def add(WHAT, WHY, WHEN):  # to add a streak by giving already started streak's date
    global ID
    if IDC():  # so that no duplicate IDs exist
        ID = random.randint(1000, 9999)
    streak = {
        "ID": ID,
        "WHAT": WHAT,
        "WHY": WHY,
        "STARTED_ON": WHEN
    }
    streaks_collection.insert_one(streak)

def view():  # to list necessary attributes only
    streaks = list(streaks_collection.find({}, {"_id": 0, "WHAT": 1, "STARTED_ON": 1}))
    if streaks:
        for streak in streaks:
            streak["STREAK_IN_DAYS"] = (datetime.datetime.now() - datetime.datetime.strptime(streak["STARTED_ON"], "%Y-%m-%d")).days
        print(tabulate(streaks, headers="keys", tablefmt='rounded_grid'))
    else:
        print("List is empty!!!")

def listall(CATEG):  # to list all the attributes of the tables
    if CATEG == "STREAKS":
        streaks = list(streaks_collection.find({}, {"_id": 0}))
        if streaks:
            for streak in streaks:
                streak["STREAK_IN_DAYS"] = (datetime.datetime.now() - datetime.datetime.strptime(streak["STARTED_ON"], "%Y-%m-%d")).days
            print(tabulate(streaks, headers="keys", tablefmt='fancy_grid'))
        else:
            print("List is empty!!!")
    elif CATEG == "BROKEN":
        broken = list(broken_collection.find({}, {"_id": 0}))
        if broken:
            for streak in broken:
                streak["STREAK_IN_DAYS"] = (datetime.datetime.strptime(streak["BROKEN_ON"], "%Y-%m-%d") - datetime.datetime.strptime(streak["STARTED_ON"], "%Y-%m-%d")).days
            print(tabulate(broken, headers="keys", tablefmt='fancy_grid'))
        else:
            print("List is empty!!!")

def restart(FROM, WHICH):  # to restart the streak
    if FROM == "STREAKS":
        streaks_collection.update_one({"ID": WHICH}, {"$set": {"STARTED_ON": str(TODAY)}})
    elif FROM == "BROKEN":
        broken_streak = broken_collection.find_one({"ID": WHICH})
        if broken_streak:
            streaks_collection.insert_one({
                "ID": broken_streak["ID"],
                "WHAT": broken_streak["WHAT"],
                "WHY": broken_streak["WHY"],
                "STARTED_ON": str(TODAY)
            })
            broken_collection.delete_one({"ID": WHICH})

def breaks(WHICH):  # to break the streak by transferring it to BROKEN list from STREAKS list
    streak = streaks_collection.find_one({"ID": WHICH})
    if streak:
        broken_collection.insert_one({
            "ID": streak["ID"],
            "WHAT": streak["WHAT"],
            "WHY": streak["WHY"],
            "STARTED_ON": streak["STARTED_ON"],
            "BROKEN_ON": str(TODAY)
        })
        streaks_collection.delete_one({"ID": WHICH})

def delete(FROM, WHICH):  # to delete the streak
    if FROM == "STREAKS":
        streaks_collection.delete_one({"ID": WHICH})
    elif FROM == "BROKEN":
        broken_collection.delete_one({"ID": WHICH})

########## ----- MAIN FUNCTION ----- ##########

def main():
    help()
    while True:
        Q = input("\n" + "Enter query: ")

        try:
            if Q == "/h" or Q == "help":
                help()

            elif Q == "/m" or Q == "menu":
                menu()

            elif Q == "/s" or Q == "start":
                WHAT = str(input("What habit to create or to break (eg. Avoid Coffee): "))
                WHY = str(input("Why you want to do so (eg. Because of addiction): "))
                start(WHAT, WHY)
                print(f"Streak for {WHAT} started. All the best!")

            elif Q == "/a" or Q == "add":
                WHAT = str(input("What habit to create or to break (eg. Avoid Coffee): "))
                WHY = str(input("Why you want to do so (eg. Because of addiction): "))
                WHEN = str(input("When did you started (in YYYY-MM-DD): "))
                add(WHAT, WHY, WHEN)
                print(f"Streak for {WHAT} added. All the best!")

            elif Q == "/v" or Q == "view":
                view()

            elif Q == "/l" or Q == "list":
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

            elif Q == "/r" or Q == "restart":
                print(tabulate([
                    ['To restart a running streak', '/s or streaks'],
                    ['To restart a broken streak', '/bn or broken']],
                    tablefmt="rounded_grid"))

                T = str(input("Enter Query [restart]: "))

                if T == '/s' or T == 'streaks':
                    streaks = list(streaks_collection.find({}, {"_id": 0}))
                    if streaks:
                        for streak in streaks:
                            streak["STREAK_IN_DAYS"] = (datetime.datetime.now() - datetime.datetime.strptime(streak["STARTED_ON"], "%Y-%m-%d")).days
                        print(tabulate(streaks, headers="keys", tablefmt='fancy_grid'))
                        WHICH = int(input("Enter ID of the streak you want to restart: "))
                        JKL = input("Are you sure to restart the streak? y/N: ") or "N"
                        if JKL == "Y" or JKL == "y":
                            restart("STREAKS", WHICH)
                            print(f"Streak for {streaks_collection.find_one({'ID': WHICH})['WHAT']} restarted. All the best!")
                    else:
                        print("No running streaks found!")

                elif T == '/bn' or T == 'broken':
                    broken = list(broken_collection.find({}, {"_id": 0}))
                    if broken:
                        for streak in broken:
                            streak["STREAK_IN_DAYS"] = (datetime.datetime.strptime(streak["BROKEN_ON"], "%Y-%m-%d") - datetime.datetime.strptime(streak["STARTED_ON"], "%Y-%m-%d")).days
                        print(tabulate(broken, headers="keys", tablefmt='fancy_grid'))
                        WHICH = int(input("Enter ID of the streak you want to restart: "))
                        JKL = input("Are you sure to restart the streak? y/N: ") or "N"
                        if JKL == "Y" or JKL == "y":
                            restart("BROKEN", WHICH)
                            print(f"Streak for {broken_collection.find_one({'ID': WHICH})['WHAT']} restarted. All the best!")
                    else:
                        print("No broken streaks found!")

            elif Q == "/b" or Q == "break":
                streaks = list(streaks_collection.find({}, {"_id": 0}))
                if streaks:
                    for streak in streaks:
                        streak["STREAK_IN_DAYS"] = (datetime.datetime.now() - datetime.datetime.strptime(streak["STARTED_ON"], "%Y-%m-%d")).days
                    print(tabulate(streaks, headers="keys", tablefmt='fancy_grid'))
                    WHICH = int(input("Enter ID of the streak you want to break: "))
                    JKL = input("Are you sure to break the streak? y/N: ") or "N"
                    if JKL == "Y" or JKL == "y":
                        breaks(WHICH)
                        print(f"Streak for {streaks_collection.find_one({'ID': WHICH})['WHAT']} broke. Ahh! Better luck next time!")
                else:
                    print("No running streaks found!")

            elif Q == "/d" or Q == "delete":
                print(tabulate([
                    ['To delete from running streaks', '/s or streaks'],
                    ['To delete from broken streaks', '/bn or broken']],
                    tablefmt="rounded_grid"))

                T = str(input("Enter Query [delete]: "))

                if T == '/s' or T == 'streaks':
                    streaks = list(streaks_collection.find({}, {"_id": 0}))
                    if streaks:
                        for streak in streaks:
                            streak["STREAK_IN_DAYS"] = (datetime.datetime.now() - datetime.datetime.strptime(streak["STARTED_ON"], "%Y-%m-%d")).days
                        print(tabulate(streaks, headers="keys", tablefmt='fancy_grid'))
                        WHICH = int(input("Enter ID of the streak you want to delete: "))
                        JKL = input("Are you sure to delete the streak? y/N: ") or "N"
                        if JKL == "Y" or JKL == "y":
                            delete("STREAKS", WHICH)
                            print(f"Streak for {streaks_collection.find_one({'ID': WHICH})['WHAT']} deleted permanently!")
                    else:
                        print("No running streaks found!")

                elif T == '/bn' or T == 'broken':
                    broken = list(broken_collection.find({}, {"_id": 0}))
                    if broken:
                        for streak in broken:
                            streak["STREAK_IN_DAYS"] = (datetime.datetime.strptime(streak["BROKEN_ON"], "%Y-%m-%d") - datetime.datetime.strptime(streak["STARTED_ON"], "%Y-%m-%d")).days
                        print(tabulate(broken, headers="keys", tablefmt='fancy_grid'))
                        WHICH = int(input("Enter ID of the streak you want to delete: "))
                        JKL = input("Are you sure to delete the streak? y/N: ") or "N"
                        if JKL == "Y" or JKL == "y":
                            delete("BROKEN", WHICH)
                            print(f"Streak for {broken_collection.find_one({'ID': WHICH})['WHAT']} deleted permanently!")
                    else:
                        print("No broken streaks found!")

            elif Q == "/q" or Q == "quit":
                print("Bye, see you again...")
                break

            else:
                print('\n' + 'Wrong argument passed!' + '\n')
                continue

        except Exception as e:  # to except errors
            print(f"Error: {e}")
            print('\n' + 'Oops! Something went wrong, please try again...' + '\n')

########## ----- MAIN FUNCTION CALLING ----- ##########

main()  # to run the whole program

########## ----- THE END ----- ##########
########## ----- THANK YOU ----- ##########
