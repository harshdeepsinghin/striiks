########## ----- MODULE IMPORTATION ----- ##########

import datetime  # for streak days counter
from tabulate import tabulate  # for beautiful help menu
from pymongo import MongoClient  # for MongoDB connection
from dotenv import load_dotenv  # to load environment variables from .env file
import os  # to access environment variables
from urllib.parse import quote_plus
from bson.objectid import ObjectId  # to work with MongoDB's ObjectId

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

# Construct the MongoDB URI
MONGODB_URI = f"mongodb+srv://{ENCODED_USERNAME}:{ENCODED_PASSWORD}@cluster0.9vczn.mongodb.net/?retryWrites=true&w=majority&appName={CLUSTER}"

########## ----- MONGODB CONNECTION ----- ##########

# Connect to MongoDB using the URI from the .env file
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]  # Use the database name from the .env file
streaks_collection = db.streaks  # Single collection for all streaks

########## ----- MISC SETUP ----- ##########

NOW = datetime.datetime.now()  # today's date with time
TODAY = NOW.date()  # today's date only

########## ----- DEFINITION OF FUNCTIONS ----- ##########

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
         ['  To advance view running streaks directly', '/l/s or running'],
         ['  To advance view broken streaks directly', '/l/bn or broken'],
         ['  To advance view all the streaks', '/l/a or all'],
         ['To restart a streak', '/r or restart'],
         ['To break a streak', '/b or break'],
         ['To delete a streak from the database permanently', '/d or delete'],
         ['To quit this app', '/q or quit']],
        tablefmt='fancy_grid'))

def start(WHAT, WHY):  # to start a streak
    streak = {
        "WHAT": WHAT,
        "WHY": WHY,
        "STARTED_ON": str(TODAY),
        "STATUS": 1,  # 1 for running streak
        "BROKEN_ON": None  # No broken date initially
    }
    result = streaks_collection.insert_one(streak)
    print(f"Streak for {WHAT} started with ID {result.inserted_id}. All the best!")

def add(WHAT, WHY, WHEN):  # to add a streak by giving already started streak's date
    streak = {
        "WHAT": WHAT,
        "WHY": WHY,
        "STARTED_ON": WHEN,
        "STATUS": 1,  # 1 for running streak
        "BROKEN_ON": None  # No broken date initially
    }
    result = streaks_collection.insert_one(streak)
    print(f"Streak for {WHAT} added with ID {result.inserted_id}. All the best!")

def view():  # to list necessary attributes only
    streaks = list(streaks_collection.find({"STATUS": 1}, {"_id": 0, "WHAT": 1, "STARTED_ON": 1}))
    if streaks:
        for streak in streaks:
            streak["STREAK_IN_DAYS"] = (datetime.datetime.now() - datetime.datetime.strptime(streak["STARTED_ON"], "%Y-%m-%d")).days
        print(tabulate(streaks, headers="keys", tablefmt='rounded_grid'))
    else:
        print("List is empty!!!")

def listall(CATEG):  # to list all the attributes of the streaks
    if CATEG == "running":
        streaks = list(streaks_collection.find({"STATUS": 1}, {}))
        if streaks:
            for streak in streaks:
                streak["STREAK_IN_DAYS"] = (datetime.datetime.now() - datetime.datetime.strptime(streak["STARTED_ON"], "%Y-%m-%d")).days
            print(tabulate(streaks, headers="keys", tablefmt='fancy_grid'))
        else:
            print("No running streaks found!")

    elif CATEG == "broken":
        streaks = list(streaks_collection.find({"STATUS": 0}, {}))
        if streaks:
            for streak in streaks:
                streak["STREAK_IN_DAYS"] = (datetime.datetime.strptime(streak["BROKEN_ON"], "%Y-%m-%d") - datetime.datetime.strptime(streak["STARTED_ON"], "%Y-%m-%d")).days
            print(tabulate(streaks, headers="keys", tablefmt='fancy_grid'))
        else:
            print("No broken streaks found!")

    elif CATEG == "all":
        streaks = list(streaks_collection.find({}, {}))
        if streaks:
            for streak in streaks:
                if streak["STATUS"] == 1:
                    streak["STREAK_IN_DAYS"] = (datetime.datetime.now() - datetime.datetime.strptime(streak["STARTED_ON"], "%Y-%m-%d")).days
                else:
                    streak["STREAK_IN_DAYS"] = (datetime.datetime.strptime(streak["BROKEN_ON"], "%Y-%m-%d") - datetime.datetime.strptime(streak["STARTED_ON"], "%Y-%m-%d")).days
            print(tabulate(streaks, headers="keys", tablefmt='fancy_grid'))
        else:
            print("No streaks found!")

def restart(STREAK_ID):  # to restart the streak
    try:
        STREAK_ID = ObjectId(STREAK_ID)  # Convert string to ObjectId
    except:
        print("Invalid ID! Please enter a valid ObjectId.")
        return

    streak = streaks_collection.find_one({"_id": STREAK_ID})
    if not streak:
        print(f"Streak with ID {STREAK_ID} not found!")
        return

    streaks_collection.update_one(
        {"_id": STREAK_ID},
        {"$set": {"STARTED_ON": str(TODAY), "STATUS": 1, "BROKEN_ON": None}}
    )
    print(f"Streak for {streak['WHAT']} restarted. All the best!")

def breaks(STREAK_ID):  # to break the streak
    try:
        STREAK_ID = ObjectId(STREAK_ID)  # Convert string to ObjectId
    except:
        print("Invalid ID! Please enter a valid ObjectId.")
        return

    streak = streaks_collection.find_one({"_id": STREAK_ID})
    if not streak:
        print(f"Streak with ID {STREAK_ID} not found!")
        return

    if streak["STATUS"] == 0:
        print(f"Streak for {streak['WHAT']} is already broken!")
        return

    streaks_collection.update_one(
        {"_id": STREAK_ID},
        {"$set": {"STATUS": 0, "BROKEN_ON": str(TODAY)}}
    )
    print(f"Streak for {streak['WHAT']} broke. Ahh! Better luck next time!")

def delete(STREAK_ID):  # to delete the streak
    try:
        STREAK_ID = ObjectId(STREAK_ID)  # Convert string to ObjectId
    except:
        print("Invalid ID! Please enter a valid ObjectId.")
        return

    streak = streaks_collection.find_one({"_id": STREAK_ID})
    if not streak:
        print(f"Streak with ID {STREAK_ID} not found!")
        return

    confirm = input(f"Are you sure you want to delete the streak for {streak['WHAT']}? (y/N): ").lower()
    if confirm != "y":
        print("Deletion canceled.")
        return

    streaks_collection.delete_one({"_id": STREAK_ID})
    print(f"Streak for {streak['WHAT']} deleted permanently!")

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

            elif Q == "/a" or Q == "add":
                WHAT = str(input("What habit to create or to break (eg. Avoid Coffee): "))
                WHY = str(input("Why you want to do so (eg. Because of addiction): "))
                WHEN = str(input("When did you start (in YYYY-MM-DD): "))
                add(WHAT, WHY, WHEN)

            elif Q == "/v" or Q == "view":
                view()

            elif Q == "/l" or Q == "list":
                print(tabulate([
                    ['To list running streaks', '/l/s or running'],
                    ['To list broken streaks', '/l/bn or broken'],
                    ['To list all streaks', '/l/a or all']],
                    tablefmt="rounded_grid"))
                T = str(input("Enter Query [list]: "))
                if T == '/l/s' or T == 'running':
                    print('\n' + "List for Running Streaks ")
                    listall("running")
                elif T == '/l/bn' or T == 'broken':
                    listall("broken")
                elif T == '/l/a' or T == 'all':
                    listall("all")

            elif Q == "/r" or Q == "restart":
                listall("all")
                STREAK_ID = input("Enter the ObjectId of the streak you want to restart: ")
                restart(STREAK_ID)

            elif Q == "/b" or Q == "break":
                listall("running")
                STREAK_ID = input("Enter the ObjectId of the streak you want to break: ")
                breaks(STREAK_ID)

            elif Q == "/d" or Q == "delete":
                listall("all")
                STREAK_ID = input("Enter the ObjectId of the streak you want to delete: ")
                delete(STREAK_ID)

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