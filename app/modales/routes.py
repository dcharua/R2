from app.modales import blueprint
from flask import render_template, request, jsonify, redirect
from flask_login import login_required
from bcrypt import checkpw
from app import db, login_manager
from app.db_models.models import *
from sqlalchemy import and_


@blueprint.route('/<template>')
@login_required
def route_template(template):
    return render_template(template + '.html')

###### agregar modales



@blueprint.route('/agregar_categoria', methods=['GET', 'POST'])
@login_required
def agregar_categoria():
    if request.form:
        data = request.form
        categoria = Categorias(nombre=data["nombre"], tipo=data["tipo"]) 
        db.session.add(categoria)
        db.session.commit()   
        return redirect("/administracion/otros")     



@blueprint.route('/agregar_centro', methods=['GET', 'POST'])
@login_required
def agregar_centro():
    if request.form:
        data = request.form
        centro = CentrosNegocio(nombre=data["nombre"], numero=data["numero"],  tipo=data["tipo"],  direccion=data["direccion"],  
        empresa_id=data["empresa"],  arrendadora=data["arrendadora"],  comentario=data["comentario"]  ) 
        db.session.add(centro) 
        db.session.commit()   
        return redirect("/administracion/centros_negocios")

@blueprint.route('/get_data_editar_centro/<cid>', methods=['GET', 'POST'])
@login_required
def get_data_editar_centro(cid):
  centro = CentrosNegocio.query.get(cid)
  return jsonify(id=centro.id, numero=centro.numero, nombre=centro.nombre, tipo=centro.tipo, direccion= centro.direccion,  empresa_id=centro.empresa_id, arrendadora= centro.arrendadora, comentario=centro.comentario) 


@blueprint.route('/editar_centro', methods=['GET', 'POST'])
@login_required
def editar_centro():
    if request.form:
        data = request.form
        print(data)
        centro = CentrosNegocio.query.get(data["id"])

        centro.nombre=data["nombre"]
        centro.numero=data["numero"]
        centro.tipo=data["tipo"]
        centro.direccion=data["direccion"]
        centro.empresa_id=data["empresa"]  
        centro.arrendadora=data["arrendadora"]
        centro.comentario=data["comentario"]
        db.session.add(centro) 
        db.session.commit()   
        return redirect("/administracion/centros_negocios")  





@blueprint.route('/agregar_concepto', methods=['GET', 'POST'])
@login_required
def agregar_concepto():
    if request.form:
        data = request.form
        if (data["categoria"]):
                categoria=data["categoria"]
        if (data["categoria2"]):
                categoria=data["categoria2"]
        concepto = Conceptos(nombre=data["nombre"], categoria_id=categoria) 
        db.session.add(concepto)
        db.session.commit()   
        return redirect("/administracion/otros")      


@blueprint.route('/agregar_empresa', methods=['GET', 'POST'])
@login_required
def agregar_empresa():
    if request.form:
        data = request.form
        empresa = Empresas(nombre=data["nombre"]) 
        db.session.add(empresa)
        db.session.commit()   
        return redirect("/administracion/otros")
    

        
#agregar_forma pago
@blueprint.route('/agregar_forma_pago', methods=['GET', 'POST'])
@login_required
def agregar_forma_pago():
        if request.form:
                data = request.form
                forma_pago= FormasPago(nombre=data["nombre"])
                db.session.add(forma_pago)
                db.session.commit()   
                return redirect("/administracion/otros")   
    

@blueprint.route('/agregar_tipo_ingreso', methods=['GET', 'POST'])
@login_required
def agregar_tipo_ingreso():
    if request.form:
        data = request.form
        tipo_ingreso = Tipo_Ingreso(tipo = data["tipo"]) 
        db.session.add(tipo_ingreso)
        db.session.commit()   
        return redirect("/administracion/otros")     
    
    
    
