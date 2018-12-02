from app.egresos import blueprint
from flask import render_template
from flask_login import login_required
from bcrypt import checkpw
from app import db, login_manager



@blueprint.route('/<template>')
@login_required
def route_template(template):
    return render_template(template + '.html')


@blueprint.route('/capturar', methods=['GET', 'POST'])
def captura_egresos():
    vendor = list(['Gosh','Caterpillar','Flexi'])
    categoria = list(['categoria_1','categoria_2','categoria_3','categoria_4','categoria_5'])
    sub_categoria = list(['sub_categoria_1','sub_categoria_2','sub_categoria_3','sub_categoria_4','sub_categoria_5'])
    forma_pago = list(['forma_pago_1','forma_pago_2','forma_pago_3','forma_pago_4','forma_pago_5'])

    return render_template("capturar.html",
                           navbar_data_capture = 'active',
                           title = "Registro de Egresos",
                           categoria = categoria,
                           sub_categoria = sub_categoria,
                           forma_pago = forma_pago,
                           vendor = vendor,
                           velocity_max = 1)
