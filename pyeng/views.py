from flask import current_app as app
from flask import render_template, redirect, request
from pyeng.utils.helpers import *
from pyeng.database import Session as DBSession


@app.route('/test', methods=['GET'])
def test():
    return str(request.args.get('name'))


@app.route('/add_class', methods=['GET'])
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
    # if not check_client_type(client, User.TEACHER_TYPE):
    #     return redirect('/')

    result = render_template('html_begin.html', title="Добавить класс")
    result += render_template('page_head.html', client=client,
                              User=User)
    result += render_template('add_class.html', error=request.args.get('error'))
    result += render_template('html_end.html')

    return result
