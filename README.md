


## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Support](#support)

## Introduction
**Striiks** is a simple streak days-counter program made in python to make or break habits.

## Installation

Prerequisites:\n
Your system must have installed any DBMS (such as MySQL, MongoDB or any other)

Clone the repo:
```
git clone 'https://github.com/harshluckyme/striiks.git'
cd streaks
```

Install the requirements:
```
python3 -m pip install -r requirements.txt
```

Set the variables for mysql in **config.py**:
```
HOST = "localhost"
USER = "root"
PASS = "admin"
```

Run the **setup.py**
```
python3 setup.py
```


## Usage

Run the **"main.py"** program
```
python3 main.py
```

Help Menu:
|                               |               |
|-------------------------------|---------------|
| For this help menu            | /h or help    |
| To start a streak             | /s or start   |
| To add an existing streak     | /a or add     |
| To simple view the streaks    | /v or view    |
| To list the streaks or broken | /l or list    |
| To break or delete a streak   | /b or break   |
| To quit this app              | /q or quit    |

## Support

Please [open an issue](https://github.com/harshluckyme/striiks/issues/new) for support.
