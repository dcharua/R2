from app.home import blueprint
from flask import render_template
from flask_login import login_required
import pandas as pd

import pyodbc


from apscheduler.schedulers.background import BackgroundScheduler
from app.db_models.db_migration import run_all_migrations


@blueprint.route('/index')
@login_required
def index():
<<<<<<< HEAD
    #df = connect_mysql()
    #df.to_csv('tst.csv',sep=',')

    print(' HEEEEEREEEEEEEE ' )
    from app.db_models.db_migration import run_all_migrations
    run_all_migrations()

=======

    print('Here!')
    # sched = BackgroundScheduler(daemon=True)
    # sched.add_job(run_all_migrations, 'interval', minutes=1)
    # #sched.add_job(run_all_migrations(), 'interval', days=1)
    # sched.start()

    run_all_migrations()
>>>>>>> 8895bd9bf6b11b79709c9884ac0766953742c93f

    return render_template('index.html')


@blueprint.route('/<template>')
@login_required
def route_template(template):
    return render_template(template + '.html')
