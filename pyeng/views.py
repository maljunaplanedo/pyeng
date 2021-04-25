from flask import current_app as app
from flask import render_template, redirect, request
from pyeng.utils.helpers import *
from pyeng.database import Session as DBSession
from time import time
from werkzeug.security import generate_password_hash, check_password_hash
from pyeng import AUTH_HASH_LEN, AUTH_HASH_COOKIE_LIFESPAN


@app.route('/test', methods=['GET'])
def test():
    return str(request.args.get('name'))


@app.route('/add_class', methods=['POST'])
def add_class():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        name = request.args.get('name')
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
        result += render_template('add_class.html', error=request.args.get('error'))
        result += render_template('html_end.html')

    return result


@app.route('/add_class_task', methods=['POST'])
def add_class_task():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        task_id = request.args.get('task_id')
        class_id = request.args.get('class_id')

        if task_id is None or class_id is None:
            return redirect('/')

        task_id = int(task_id)
        class_id = int(class_id)

        task = db.query(Task).filter(Task.id == task_id).first()
        class_ = db.query(Class).filter(Class.id == class_id).first()

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

        class_id = request.args.get('class_id')
        if class_id is None:
            return redirect('/')
        class_id = int(class_id)

        class_ = db.query(Class).filter(Class.id == class_id).first()
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

        name = request.args.get('name')
        surname = request.args.get('surname')
        class_id = request.args.get('class_id')

        if name is None or surname is None or class_id is None:
            return redirect('/')

        class_ = db.query(Class).filter(Class.id == class_id).first()
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

        class_id = request.args.get('class_id')
        if class_id is None:
            return redirect('/')
        class_id = int(class_id)

        class_ = db.query(Class).filter(Class.id == class_id).first()
        if class_ is None:
            return redirect('/')

        result = render_template('html_begin.html', title="Добавить ученика в " + class_.name)
        result += render_template('page_head.html', client=client, User=User)

        error = request.args.get('error')
        result += render_template('add_student.html', class_=class_, error=error)
        result += render_template('html_end.html')

        return result


@app.route('/add_task', methods=['POST'])
def add_task():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        type_ = request.args.get('type')
        name = request.args.get('name')
        given = request.args.get('given')
        answer = request.args.get('answer')
        duration = request.args.get('duration')

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


@app.route('add_task_page', methods=['GET'])
def add_task_page():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        result = render_template('html_begin.html', title='Добавить задание')
        result += render_template('page_head.html', client=client, User=User)

        error = request.args.get('error')

        result += render_template('add_task.html', error=error)
        result += render_template('html_end.html')

        return result


@app.route('auth', methods=['POST'])
def auth():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.GUEST_TYPE):
            return redirect('/')

        error_url = 'auth_page?error=wrong'

        login = request.args.get('login')
        password = request.args.get('password')

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
        db.add(Auth(auth_hash, candidate))
        db.commit()

        request.set_cookie('auth_hash', auth_hash, max_age=AUTH_HASH_COOKIE_LIFESPAN)

        return redirect('/')


@app.route('/auth_page', methods=['GET'])
def auth_page():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.GUEST_TYPE):
            return redirect('/')

        error = request.args.get('error')

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
def class_students():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        class_id = request.args.get('id')
        if class_id is None:
            return redirect('/')
        class_id = int(class_id)

        class_ = db.query(Class).filter(Class.id == class_id).first()
        if class_ is None:
            return redirect('/')

        result = render_template('html_begin.html', title='Ученики ' + class_.name)
        result += render_template('page_head.html', client=client, User=User)

        result += render_template('class_students.html', class_=class_)
        result += render_template('html_end.html')

        return result


@app.route('/class_task', methods=['GET'])
def class_task():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        class_task_id = request.args.get('id')
        if class_task_id is None:
            return redirect('/')
        class_task_id = int(class_task_id)

        this_class_task = db.query(ClassTask).filter(ClassTask.id == class_task_id).first()
        if this_class_task is None:
            return redirect('/')

        for students_task in this_class_task.students_tasks:
            students_task.update_time()
        db.commit()

        result = render_template('html_begin.html',
                                 title=f'Результаты {this_class_task.class_.name}' +
                                 f'по заданию {this_class_task.task.name}')

        result += render_template('page_head.html', client=client, User=User)
        result += render_template('class_task.html', class_task=this_class_task)
        result += render_template('html_end.html')

        return result


@app.route('/class_tasks', methods=['GET'])
def class_tasks():
    with DBSession() as db:
        client = get_client(db)
        if not check_client_type(client, User.TEACHER_TYPE):
            return redirect('/')

        class_id = request.args.get('id')
        if class_id is None:
            return redirect('/')

        class_id = int(class_id)
        class_ = db.query(Class).filter(Class.id == class_id).first()
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
            return redirect('student?id=' + client.id)
        elif check_client_type(client, User.GUEST_TYPE):
            return redirect('auth_page')

        result = render_template('html_begin.html', title='Система тестирования')
        result += render_template('page_head.html', client=client, User=User)
        result += render_template('index.html')
        result += render_template('html_end.html')

        return result
