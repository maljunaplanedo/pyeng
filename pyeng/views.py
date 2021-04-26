from flask import current_app as app
from flask import render_template, redirect, request, make_response, send_file
from pyeng.utils.helpers import *
from pyeng.database import Session as DBSession
from time import time
from werkzeug.security import generate_password_hash, check_password_hash
from pyeng import AUTH_HASH_LEN, AUTH_HASH_COOKIE_LIFESPAN, TASK1_FULL_WORD_BONUS, TASK1_WRONG_LETTER_FINE
import json


@app.route('/add_class', methods=['POST'])
def add_class():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        name = request.values.get('name')
        if not check_class_name(name):
            return redirect('/add_class_page?error=wrongname')

        db.add(Class(name))
        db.commit()

        return redirect('/classes')


@app.route('/add_class_page', methods=['GET'])
def add_class_page():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        result = render_template('html_begin.html', title="Добавить класс")
        result += render_template('page_head.html', client=client,
                                  User=User)
        result += render_template('add_class.html', error=request.values.get('error'))
        result += render_template('html_end.html')

    return result


@app.route('/add_class_task', methods=['POST'])
def add_class_task():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        task_id = request.values.get('task_id')
        class_id = request.values.get('class_id')

        if task_id is None or class_id is None:
            return redirect('/')

        task_id = int(task_id)
        class_id = int(class_id)

        task = db.query(Task).get(task_id)
        class_ = db.query(Class).get(class_id)

        if task is None or class_ is None:
            return redirect('/')

        add_time = int(time())
        class_task = ClassTask(class_, task, add_time)
        db.add(class_task)

        class_students = db.query(User).filter(User.class_ == class_).all()
        for student in class_students:
            db.add(StudentsTask(add_time, class_task, task, student))

        db.commit()
        return redirect(f'/class_tasks?id={class_id}')


@app.route('/add_class_task_page', methods=['GET'])
def add_class_task_page():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        class_id = request.values.get('class_id')
        if class_id is None:
            return redirect('/')
        class_id = int(class_id)

        class_ = db.query(Class).get(class_id)
        if class_ is None:
            return redirect('/')

        result = render_template('html_begin.html', title="Задать задание " + class_.name)
        result += render_template('page_head.html', client=client, User=User)

        tasks = db.query(Task).all()

        result += render_template('add_class_task.html', tasks=tasks, class_=class_)
        result += render_template('html_end.html')

        return result


@app.route('/add_student', methods=['POST'])
def add_student():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        name = request.values.get('name')
        surname = request.values.get('surname')
        class_id = request.values.get('class_id')

        if name is None or surname is None or class_id is None:
            return redirect('/')

        class_ = db.query(Class).get(class_id)
        if class_ is None:
            return redirect('/')

        error_url = f'add_student_page?class_id={class_id}=&error={{error}}'

        if not check_name(name):
            return redirect(error_url.format(error='wrongname'))
        if not check_name(surname):
            return redirect(error_url.format(error='wrongsurname'))

        student = add_unconf_user(db, name, surname, User.STUDENT_TYPE, class_)

        db.commit()

        result = render_template('html_begin.html', title="Ученик успешно добавлен")
        result += render_template('page_head.html', client=client, User=User)
        result += render_template('student_added.html', student=student, class_=class_)
        result += render_template('html_end.html')

        return result


@app.route('/add_student_page', methods=['GET'])
def add_student_page():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        class_id = request.values.get('class_id')
        if class_id is None:
            return redirect('/')
        class_id = int(class_id)

        class_ = db.query(Class).get(class_id)
        if class_ is None:
            return redirect('/')

        result = render_template('html_begin.html', title="Добавить ученика в " + class_.name)
        result += render_template('page_head.html', client=client, User=User)

        error = request.values.get('error')
        result += render_template('add_student.html', class_=class_, error=error)
        result += render_template('html_end.html')

        return result


@app.route('/add_task', methods=['POST'])
def add_task():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        type_ = request.values.get('type')
        name = request.values.get('name')
        given = request.values.get('given')
        answer = request.values.get('answer')
        duration = request.values.get('duration')

        if (type_ is None or name is None or given is None or
                answer is None or duration is None):
            return redirect('/')

        type_ = int(type_)
        duration = int(duration)

        error_url = 'add_task_page?error={error}'

        if type_ != 1:
            return redirect(error_url.format('wrongtype'))
        elif not check_task_name(name):
            return redirect(error_url.format('wrongname'))
        elif not check_task_given(given):
            return redirect(error_url.format('wronggiven'))
        elif not check_task_answer_format(answer):
            return redirect(error_url.format('wronganswer'))
        elif not check_task_duration(duration):
            return redirect(error_url.format('wrongduration'))

        task = Task(type_, name, given, answer, duration)
        db.add(task)
        db.commit()

        return redirect('/tasks')


@app.route('/add_task_page', methods=['GET'])
def add_task_page():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        result = render_template('html_begin.html', title='Добавить задание')
        result += render_template('page_head.html', client=client, User=User)

        error = request.values.get('error')

        result += render_template('add_task.html', error=error)
        result += render_template('html_end.html')

        return result


@app.route('/auth', methods=['POST'])
def auth():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.GUEST_TYPE):
            return redirect('/')

        error_url = 'auth_page?error=wrong'

        login = request.values.get('login')
        password = request.values.get('password')

        if login is None or password is None:
            return redirect('/')

        if not check_login_format(login) or not check_password_format(password):
            return redirect(error_url)

        candidate = db.query(User).filter(User.login == login).first()
        if candidate is None:
            return redirect(error_url)

        if not check_password_hash(candidate.password, password):
            return redirect(error_url)

        auth_hash = generate_random_string(AUTH_HASH_LEN)
        auth_object = Auth(generate_password_hash(auth_hash), candidate)
        db.add(auth_object)
        db.commit()

        response = make_response(redirect('/'))
        response.set_cookie('auth_id', str(auth_object.id), max_age=AUTH_HASH_COOKIE_LIFESPAN)
        response.set_cookie('auth_hash', auth_hash, max_age=AUTH_HASH_COOKIE_LIFESPAN)

        return response


@app.route('/auth_page', methods=['GET'])
def auth_page():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.GUEST_TYPE):
            return redirect('/')

        error = request.values.get('error')

        result = render_template('html_begin.html', title='Авторизация')
        result += render_template('auth.html', error=error)
        result += render_template('html_end.html')

        return result


@app.route('/classes', methods=['GET'])
def classes():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        result = render_template('html_begin.html', title='Классы')
        result += render_template('page_head.html', client=client, User=User)

        class_list = db.query(Class).all()

        result += render_template('classes.html', classes=class_list)
        result += render_template('html_end.html')

        return result


@app.route('/class_students', methods=['GET'])
def class_students_page():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        class_id = request.values.get('id')
        if class_id is None:
            return redirect('/')
        class_id = int(class_id)

        class_ = db.query(Class).get(class_id)
        if class_ is None:
            return redirect('/')

        result = render_template('html_begin.html', title='Ученики ' + class_.name)
        result += render_template('page_head.html', client=client, User=User)

        result += render_template('class_students.html', class_=class_)
        result += render_template('html_end.html')

        return result


@app.route('/class_task', methods=['GET'])
def class_task_page():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        class_task_id = request.values.get('id')
        if class_task_id is None:
            return redirect('/')
        class_task_id = int(class_task_id)

        class_task = db.query(ClassTask).get(class_task_id)
        if class_task is None:
            return redirect('/')

        for students_task in class_task.students_tasks:
            students_task.update_time()
        db.commit()

        result = render_template('html_begin.html',
                                 title=f'Результаты {class_task.class_.name}' +
                                 f'по заданию {class_task.task.name}')

        result += render_template('page_head.html', client=client, User=User)
        result += render_template('class_task.html', class_task=class_task)
        result += render_template('html_end.html')

        return result


@app.route('/class_tasks', methods=['GET'])
def class_tasks():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        class_id = request.values.get('id')
        if class_id is None:
            return redirect('/')

        class_id = int(class_id)
        class_ = db.query(Class).get(class_id)
        if class_ is None:
            return redirect('/')

        result = render_template('html_begin.html', title='Задания ' + class_.name)
        result += render_template('page_head.html', client=client, User=User)
        result += render_template('class_tasks.html', class_=class_)
        result += render_template('html_end.html')

        return result


@app.route('/', methods=['GET'])
def index():
    with DBSession() as db:
        client = get_client(db)
        if check_client_type(client, User.STUDENT_TYPE):
            return redirect(f'student?id={client.id}')
        elif check_client_type(client, User.GUEST_TYPE):
            return redirect('auth_page')

        result = render_template('html_begin.html', title='Система тестирования')
        result += render_template('page_head.html', client=client, User=User)
        result += render_template('index.html')
        result += render_template('html_end.html')

        return result


@app.route('/reg', methods=['POST'])
def reg():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.GUEST_TYPE):
            return redirect('/')

        invite_code = request.values.get('invite_code')
        login = request.values.get('login')
        password = request.values.get('password')

        error_url = 'reg_page?error={error}'

        if invite_code is None or login is None or password is None:
            return redirect('/')

        if not check_invite_code(invite_code):
            return redirect(error_url.format(error='notexist'))
        if not check_login_format(login):
            return redirect(error_url.format(error='loginnotvalid'))
        if not check_password_format(password):
            return redirect(error_url.format(error='passwordnotvalid'))

        unconf_user = db.query(UnconfUser).filter(UnconfUser.code == invite_code).first()
        if unconf_user is None:
            return redirect(error_url.format(error='notexist'))

        if db.query(User).filter(User.login == login).count() > 0:
            return redirect(error_url.format(error='loginexists'))

        password = generate_password_hash(password)
        db.add(User(login, password, unconf_user.name, unconf_user.surname,
                    unconf_user.type, unconf_user.class_))
        db.delete(unconf_user)

        db.commit()
        return redirect('auth_page')


@app.route('/reg_page', methods=['GET'])
def reg_page():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.GUEST_TYPE):
            return redirect('/')

        error = request.values.get('error')

        result = render_template('html_begin.html', title='Регистрация')
        result += render_template('reg.html', error=error)
        result += render_template('html_end.html')

        return result


@app.route('/remove_class', methods=['GET'])
def remove_class():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        class_id = request.values.get('id')
        if class_id is None:
            return redirect('/')

        class_id = int(class_id)
        class_ = db.query(Class).get(class_id)
        if class_ is None:
            redirect('/')
        db.delete(class_)

        db.commit()

        return redirect('classes')


@app.route('/remove_class_task', methods=['GET'])
def remove_class_task():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        class_task_id = request.values.get('id')
        if class_task_id is None:
            return redirect('/')

        class_task_id = int(class_task_id)
        class_task = db.query(ClassTask).get(class_task_id)
        if class_task is None:
            return redirect('/')

        class_id = class_task.class_.id
        db.delete(class_task)

        db.commit()

        return redirect(f'class_tasks?id={class_id}')


@app.route('/remove_student', methods=['GET'])
def remove_student():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        student_id = request.values.get('id')
        if student_id is None:
            return redirect('/')
        student_id = int(student_id)

        student = db.query(User).get(student_id)
        if student is None:
            return redirect('/')

        class_id = student.class_.id

        db.delete(student)

        db.commit()

        return redirect(f'class_students?id={class_id}')


@app.route('/remove_task', methods=['GET'])
def remove_task():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        task_id = request.values.get('id')
        if task_id is None:
            return redirect('/')
        task_id = int(task_id)
        task = db.query(Task).get(task_id)
        if task is None:
            return redirect('/')

        db.delete(task)

        db.commit()

        return redirect('tasks')


@app.route('/remove_unconf_student', methods=['GET'])
def remove_unconf_student():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        student_id = request.values.get('id')
        if student_id is None:
            return redirect('/')
        student_id = int(student_id)

        student = db.query(User).get(student_id)
        if student is None:
            return redirect('/')

        class_id = student.class_.id
        db.delete(student)

        db.commit()

        return redirect(f'class_students?id={class_id}')


@app.route('/student', methods=['GET'])
def student_page():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE, User.STUDENT_TYPE):
            return redirect('/')

        student_id = request.values.get('id')
        if student_id is None:
            return redirect('/')

        student = db.query(User).get(student_id)
        if (student is None or student.type != User.STUDENT_TYPE or
                (client.type == User.STUDENT_TYPE and client.id != student.id)):
            return redirect('/')

        for students_task in student.students_tasks:
            students_task.update_time()
        db.commit()

        if client.type == User.STUDENT_TYPE:
            running_task = student.get_running_task()
            if running_task is not None:
                return redirect(f'/task_runner_page?id={running_task.id}')

        result = render_template('html_begin.html', title=student.name + ' ' + student.surname)
        result += render_template('page_head.html', client=client, User=User)
        result += render_template('student.html', is_teacher=client.type == User.TEACHER_TYPE,
                                  student=student)
        result += render_template('html_end.html')

        return result


@app.route('/students_task', methods=['GET'])
def students_task_page():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE, User.STUDENT_TYPE):
            return redirect('/')

        students_task_id = request.values.get('id')
        if students_task_id is None:
            return redirect('/')

        students_task = db.query(StudentsTask).get(students_task_id)
        if students_task is None:
            return redirect('/')

        student = students_task.student
        if client.type == User.STUDENT_TYPE and client.id != student.id:
            return redirect('/')

        students_task.update_time()
        db.commit()

        if client.type == User.STUDENT_TYPE:
            running_task = student.get_running_task()
            if running_task is not None:
                return redirect(f'/task_runner_page?id={running_task.id}')

        result = render_template('html_begin.html',
                                 title=f'Задание {students_task.task.name}')
        result += render_template('page_head.html', client=client, User=User)
        result += render_template('students_task.html', is_teacher=client.type == User.TEACHER_TYPE,
                                  students_task=students_task, StudentsTask=StudentsTask)
        result += render_template('html_end.html')

        return result


@app.route('/task', methods=['GET'])
def task_page():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        task_id = request.values.get('id')
        if task_id is None:
            return redirect('/')
        task_id = int(task_id)

        task = db.query(Task).get(task_id)
        if task is None:
            return redirect('/')

        result = render_template('html_begin.html', title=f'Задание {task.name}')
        result += render_template('page_head.html', client=client, User=User)
        result += render_template('task.html', task=task)
        result += render_template('html_end.html')

        return result


@app.route('/task_runner', methods=['POST'])
def task_runner():
    with DBSession() as db:
        client = get_client(db)

        answer = {}
        if not check_client_type(client, User.STUDENT_TYPE):
            return json.dumps({'command': 'to_index'})

        command = request.values.get('command')

        students_task_id = request.values.get('student_task')
        if command is None or students_task_id is None:
            return json.dumps({'command': 'to_index'})
        students_task_id = int(students_task_id)

        students_task = db.query(StudentsTask).get(students_task_id)
        if students_task is None:
            return json.dumps({'command': 'to_index'})

        other_running_task = students_task.student.get_running_task()
        if other_running_task is not None and other_running_task.id != students_task.id:
            return json.dumps({'command': 'to_index'})

        time_left = students_task.update_time()
        db.commit()

        if students_task.status == StudentsTask.FINISHED_STATUS or time_left < 0 or command == 'end':
            students_task.status = StudentsTask.FINISHED_STATUS
            answer.update({'command': 'to_index'})
        elif command == 'init':
            answer['command'] = 'ok'
            answer['task_type'] = int(students_task.task.type)
            answer['task_name'] = students_task.task.name
            answer['given'] = students_task.task.given

            if students_task.status == StudentsTask.NOT_STARTED_STATUS:
                students_task.begin_time = int(time())
                students_task.status = StudentsTask.RUNNING_STATUS
                answer['time_left'] = students_task.task.duration

                if students_task.task.type == 1:
                    gap_nom = students_task.task.given.count('##')
                    emp = []
                    for i in range(gap_nom):
                        emp.append('')

                    emp = json.dumps(emp)
                    students_task.answers = emp
            else:
                answer['time_left'] = time_left

            answer['result'] = students_task.result
            answer['answers'] = students_task.answers
        elif students_task.status == StudentsTask.NOT_STARTED_STATUS:
            answer.update({'command': 'to_index'})
        elif command == 'input':
            if students_task.task.type == 1:
                gap_nom = request.values.get('gap_nom')
                letter = request.values.get('letter')

                if gap_nom is None or letter is None:
                    return json.dumps({'command': 'to_index'})

                gap_nom = int(gap_nom)
                true_answers = json.loads(students_task.task.answer)
                clients_answers = json.loads(students_task.answers)

                if (gap_nom >= len(true_answers) or
                        len(true_answers[gap_nom]) <= len(clients_answers[gap_nom])):
                    return json.dumps({'command': 'to_index'})

                if true_answers[gap_nom][len(clients_answers[gap_nom])] == letter:
                    clients_answers[gap_nom] += letter

                    if clients_answers[gap_nom] == true_answers[gap_nom]:
                        answer['full_word'] = 'true'
                        clients_answers[gap_nom] += '##'
                        students_task.result += TASK1_FULL_WORD_BONUS
                    students_task.answers = json.dumps(clients_answers)
                    answer['command'] = 'good'
                else:
                    students_task.result -= TASK1_WRONG_LETTER_FINE
                    answer['command'] = 'bad'

            answer['result'] = students_task.result
            answer['time_left'] = time_left

        db.commit()
        return json.dumps(answer)


@app.route('/task_runner_page')
def task_runner_page():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.STUDENT_TYPE):
            return redirect('/')

        students_task_id = request.values.get('id')
        if students_task_id is None:
            return redirect('/')
        students_task_id = int(students_task_id)

        result = render_template('html_begin.html', title='Тестирующая система',
                                 enable_testing_system=students_task_id)
        result += render_template('page_head.html', client=client, User=User)
        result += render_template('html_end.html')

        return result


@app.route('/tasks')
def tasks_page():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        tasks = db.query(Task).all()

        result = render_template('html_begin.html', title='Задания')
        result += render_template('page_head.html', client=client, User=User)
        result += render_template('tasks.html', tasks=tasks)
        result += render_template('html_end.html')

        return result


@app.route('/unauth')
def unauth():
    with DBSession() as db:
        auth_id = request.cookies.get('auth_id')
        auth_hash = request.cookies.get('auth_hash')
        if auth_id is None or auth_hash is None:
            return redirect('/')
        auth_id = int(auth_id)

        auth_object = db.query(Auth).get(auth_id)
        if not check_password_hash(auth_object.auth_hash, auth_hash):
            return redirect('/')

        response = make_response(redirect('/'))
        response.set_cookie('auth_id', '', expires=0)
        response.set_cookie('auth_hash', '', expires=0)

        db.delete(db.query(Auth).get(auth_id))
        db.commit()

        return response


@app.route('/scripts/<path:filename>', methods=['GET'])
def get_script(filename):
    return send_file(f'scripts/{filename}')
