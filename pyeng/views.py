from flask import current_app as app
from flask import render_template, redirect, request
from pyeng.utils.helpers import *
from pyeng.database import Session as DBSession
from time import time


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

