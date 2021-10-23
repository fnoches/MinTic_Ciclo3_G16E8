from typing import cast
from flask import Flask
from flask import render_template as render
from flask import redirect
from flask import request
from sqlalchemy import create_engine
from db import get_db, close_db

app = Flask(__name__)

lista_estudiantes = ["Est1", "Est2", "Est3"]

lista_docentes = ["Profesor1", "Profesor2", "Profesor3"]

lista_cursos = {
    "123": {'materia':"Materia 1", 'profesor':"Profesor 1", 'estudiantes':['Est 1', 'Est 2', 'Est 3']},
    "234": {'materia':"Materia 2", 'profesor':"Profesor 2", 'estudiantes':['Est 1', 'Est 2', 'Est 3']},
    "345": {'materia':"Materia 3", 'profesor':"Profesor 3", 'estudiantes':['Est 1', 'Est 2', 'Est 3']},
    "456": {'materia':"Materia 4", 'profesor':"Profesor 2", 'estudiantes':['Est 1', 'Est 2', 'Est 3']},
    "678": {'materia':"Materia 5", 'profesor':"Profesor 1", 'estudiantes':['Est 1', 'Est 2', 'Est 3']},
}

engine = create_engine('sqlite:///census_nyc')

sesion_iniciada = False

@app.route("/", methods=["GET"])
@app.route("/inicio", methods=["GET","POST"])
def inicio():
    # Si ya inició sesión -> Página de Cursos
    # Sino -> Bienvenida
    return render(
        "inicio.html",
        sesion_iniciada=sesion_iniciada,
        lista_cursos=lista_cursos
    )

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == 'POST':    
        id = request.form['id']
        nombre = request.form['nombre']
        correo = request.form['correo']
        telefono = request.form['telefono']
        contraseña = request.form['contraseña']
        categoria = request.form['categoria']

        error = None
        db = get_db()

        if error is not None:
            return render("registro.html")
        else:
            if categoria == "Estudiante":
                db.execute(
                    'INSERT INTO estudiantes(id_estudiante, nombre_estudiante, correo_estudiante, telefono_estudiante, contraseña_estudiante) VALUES (?,?,?,?,?) ',(id, nombre, correo, telefono, contraseña)
                )
                db.commit()
            else:
                db.execute(
                    'INSERT INTO docentes(id_docente, nombre_docente, correo_docente, telefono_docente, contraseña_docente) VALUES (?,?,?,?,?) ',(id, nombre, correo, telefono, contraseña)
                )
                db.commit()
            db=close_db()
            return redirect("/ingreso")

    else:    
        return render("registro.html")
    

@app.route("/ingreso", methods=["GET", "POST"])
def ingreso():
    global sesion_iniciada
    if request.method == "GET":
        return render("ingreso.html")
    else:
        id = request.form['id']
        contraseña = request.form['contraseña']
        categoria = request.form['categoria']
        db = get_db()
        
        if categoria == "Estudiante":
            contra = db.execute('SELECT contraseña_estudiante FROM estudiantes WHERE id_estudiante = ?',(id,)).fetchone()
        else:
            contra = db.execute('SELECT contraseña_docente FROM docentes WHERE id_docente = ?',(id,)).fetchone()

        if  contra[0] == contraseña:
            sesion_iniciada = True
            return redirect("/usuario")
        else:
            return redirect("/ingreso")

@app.route("/salir", methods=["POST"])
def salir():
    global sesion_iniciada
    sesion_iniciada = False
    return redirect("/inicio")

@app.route("/usuario", methods=["GET"])
def pp_usuario():
    return render("usuario.html")

@app.route("/usuario/perfil", methods=["GET", "POST"])
def perfil():
    return render("perfil.html")

@app.route("/usuario/<id_usuario>", methods=["GET"])
def usuario_info(id_usuario):
    if id_usuario in lista_estudiantes:
        return f"Estás viendo el perfil del estudiante: {id_usuario}"
    elif id_usuario in lista_docentes:
        return f"Estás viendo el perfil del profesor: {id_usuario}"
    else: 
        return f"Error: el usuario {id_usuario} no existe"

@app.route("/usuario/<id_usuario>/cursos", methods=["GET"])
def usuario_cursos(id_usuario):
    if id_usuario in lista_estudiantes:
        return render("cursos.html")
    else: 
        return f"Error: el usuario {id_usuario} no existe"

@app.route("/usuario/cursos/<id_curso>", methods=["GET"])
def usuario_cursox(id_curso):
    if id_curso in lista_cursos:
        return f"Estás viendo el curso {id_curso}, sus actividades y los comentarios de cada una."
    else: 
        return f"Error: el curso {id_curso} no existe"

@app.route("/usuario/cursos/<id_curso>/actividades", methods=["GET", "POST"])
def usuario_acts(id_curso):
    return f"Estás viendo las actividades creadas para el curso {id_curso}"

@app.route("/usuario/cursos/<id_curso>/crearact", methods=["GET"])
def usuario_crearact(id_curso):
    return f"Estás viendo la página de creación de actividad para el curso {id_curso}"

@app.route("/usuario/<id_usuario>/calificaciones", methods=["GET"])
def usuario_calificaciones(id_usuario):
    return render("calificaciones.html")

@app.route("/usuario/superadmin/dashboard", methods=["GET","POST"])
def dashboard():
    return f"Estás viendo la página de dashboard administrativo para el superadministrador, aquí puedes crear cursos, eliminarlos, asignar profesores y estudiantes a cada uno, y manejar todo el sistema de gestión de notas."

@app.route("/curso/<id_curso>", methods=["GET"])
def curso_detalle(id_curso):
    #try:
    #   id_curso = int(id_curso)
    #except Exception as e:
    #   id_curso = 0
    if id_curso in lista_cursos:
        return lista_cursos[id_curso]
    else: 
        return f"Error: el curso que estás buscando ({id_curso}) no existe"

if __name__=="__main__":
    app.run(debug=True)