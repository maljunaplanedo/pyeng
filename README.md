# English testing system
# ATTENTION
## Read all this manual carefully.

## Installing

1. Clone the repository:
`git clone https://github.com/maljunaplanedo/pyeng`
2. Enter the directory:
`cd pyeng`
3. Create Python virtual environment:
`python3 -m venv env`
4. Activate it:
`source env/bin/activate`   
5. Install project requirements:
`pip install -r requirements.txt`
6. Create database:

   `mkdir databases` 

   `python create_database.py`
7. Add teacher's account (specify name and surname as command line arguments):
`python create_teachers_account.py Marat Satskevich`
8. You will be given an invite code for the teacher. COPY IT!

## Running
(do all the steps inside the virtual environment!)
1. Specify Flask App location:
`export FLASK_APP=pyeng/`
2. Start the server (specify host and port you want):
`flask run --host=localhost --port=5000`

## Using
1. Register the teacher's account: 

    1.1 Click "Зарегистрируйтесь"
   
    1.2 Enter the invite code you copied, specify your login and password
   
    1.3 Sign in
   
2. Add a task:
   
    2.1 Click "Задания"
   
    2.2 Click "Добавить задание"
   
    2.3 Add task's name, given, etc. !ONLY TASK TYPE 1 IS SUPPORTED - FILLING THE GAPS!
        
        Fill these fields like in this example:
       
        Task type: `1`
       
        Task name: `Test task`
       
        Given: `London ## the ## of ## ##`
       
        Answers: `["is", "capital", "Great", "Britain"]`
       
        Duration: `60`

    2.4 Click "Добавить"
   
3. Add a class:
   
    3.1 Go back to the main page
    
    3.2 Click "Классы"
   
    3.3 Click "Добавить класс"
   
    3.4 Specify class name. For example, "11а".
   
4. Add a student to the class
   
    4.1 Click on your new class

    4.2 Click "Ученики"
   
    4.2 Click "Добавить ученика"
   
    4.3 Specify name and surname
   
    4.4 Click "Добавить"

    4.5 !COPY THE INVITE CODE!
   
5. Register the student
   
    5.1 Click "Выйти"
   
    5.2 Click "Зарегистрируйтесь"
   
    5.3 Enter invite code, login, password
   
    5.4 Click "Зарегистрироваться"
   
6. Assign a task to the class
   
    6.1 Authorize as a teacher
   
    6.2 Go to the class, click "Ученики" and make sure the new student is there.

    6.3 Go back and click "Задания"

    6.4 Click "Задать задание классу"

    6.5 Select your task

    6.6 Click "Добавить"

7. Solve the task
    7.1 Click "Выйти"
   
    7.2 Authorize as a student
   
    7.3 Select a task
   
    7.4 Click "Перейти к решению -> Перейти к выполнению"
   
    7.5 Solve it! Try to make mistakes to see how the system will react.
   
    7.6 Click "Завершить"

8. Check the results
   
    8.1 Click "Выйти"
   
    8.2 Authorize as a teacher

    8.3 Click "Классы"

    8.4 Select your class

    8.5 Click "Задания"

    8.6 Select your task

    8.7 See the results.
