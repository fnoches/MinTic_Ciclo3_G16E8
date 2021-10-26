from flask import Flask
from flask import render_template as render
from flask import redirect, url_for
from flask import request
from sqlalchemy import create_engine
from db import get_db, close_db
from flask import flash
from utils import isUsernameValid, isEmailValid, isPasswordValid, isTipoValid
import yagmail as yagmail

app = Flask(__name__)
app.secret_key= "samara"

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
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']
        categoria = request.form['categoria']

        error = None

        if not isUsernameValid(usuario):
            error = "El usuario debe ser alfanumerico o incluir solo '.','_','-'"
            flash(error)
        if not isEmailValid(correo):
            error = "correo invalido"
            flash(error)
        if not isPasswordValid(contraseña):
            error="contraseña incorrecta"
            flash(error)

        db = get_db()

        if error is not None:
            return render("registro.html", error=error)
        else:
            yag = yagmail.SMTP('ljvillanueva@uninorte.edu.co', '4Wf45w3hch') 
            yag.send(to=correo, subject='Activa tu cuenta',
                contents='Bienvenido, usa este link para activar tu cuenta ')
            flash('Revisa tu correo para activar tu cuenta')
            if categoria == "Estudiante":
                db.execute(
                    'INSERT INTO estudiantes(id_estudiante, nombre_estudiante, correo_estudiante, telefono_estudiante, usuario_estudiante, contraseña_estudiante) VALUES (?,?,?,?,?,?) ',(id, nombre, correo, telefono, usuario, contraseña)
                )
                db.commit()
            else:
                db.execute(
                    'INSERT INTO docentes(id_docente, nombre_docente, correo_docente, telefono_docente, usuario_docente, contraseña_docente) VALUES (?,?,?,?,?,?) ',(id, nombre, correo, telefono, usuario, contraseña)
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
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']
        categoria = request.form['categoria']
        
        error = None
        
        if not isUsernameValid(usuario):
            error = "El usuario debe ser alfanumerico o incluir solo '.','_','-'"
            flash(error)
        
        if not isPasswordValid(contraseña):
            error="contraseña incorrecta"
            flash(error)

        db = get_db()

        if error is not None:
            return render("ingreso.html", error=error)
        else:
            if categoria == "Estudiante":
                contra = db.execute('SELECT contraseña_estudiante FROM estudiantes WHERE usuario_estudiante = ?',(usuario,)).fetchone()
                if  str(contra[0]) == str(contraseña):
                    sesion_iniciada = True
                    return redirect("/perfilestudiante")
                else: 
                    return redirect("/ingreso")            
            else:
                contra = db.execute('SELECT contraseña_docente FROM docentes WHERE usuario_docente = ?',(usuario,)).fetchone()
                if  str(contra[0]) == str(contraseña):
                    sesion_iniciada = True
                    return redirect("/perfilprofesor")
                else: 
                    return redirect("/ingreso") 

@app.route("/salir", methods=["POST"])
def salir():
    global sesion_iniciada
    sesion_iniciada = False
    return redirect("/inicio")

@app.route('/perfilestudiante',methods=["GET","POST"])
def perfil_estudiante():
    return render("perfilestudiante.html")

@app.route('/perfilestudiante/datosestudiante',methods=["GET","POST"])
def datos_estudiante():
    return render("datos_estudiante.html")

@app.route('/perfilestudiante/asignaturas_estudiante',methods=["GET","POST"])
def asignaturas_estudiante():
    return render("asignaturas_estudiante.html")

@app.route("/perfilestudiante/asignaturas_estudiante/cursos/<id_curso>", methods=["GET"])
def usuario_cursox(id_curso):
    if id_curso in lista_cursos:
        return f"Estás viendo el curso {id_curso}, sus actividades y los comentarios de cada una."
    else: 
        return f"Error: el curso {id_curso} no existe"

@app.route('/perfilestudiante/notas_estudiante',methods=["GET","POST"])
def notas_estudiante():
    return render("notas_estudiante.html")

@app.route('/perfilprofesor',methods=["GET","POST"])
def perfil_profesor():
    return render("perfil_profesor.html")

@app.route('/perfilprofesor/datosprofesor',methods=["GET","POST"])
def datos_profesor():
    return render("datos_docente.html")

@app.route('/perfilprofesor/asignaturas_profesor',methods=["GET","POST"])
def asignaturas_profesor():
    return render("asignaturas_profesor.html")

@app.route("/usuario/cursos/<id_curso>/actividades", methods=["GET", "POST"])
def usuario_acts(id_curso):
    return f"Estás viendo las actividades creadas para el curso {id_curso}"

@app.route("/usuario/cursos/<id_curso>/crearact", methods=["GET"])
def usuario_crearact(id_curso):
    return f"Estás viendo la página de creación de actividad para el curso {id_curso}"

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

@app.route("/usuario/superadmin/dashboard", methods=["GET","POST"])
def dashboard():
    return f"Estás viendo la página de dashboard administrativo para el superadministrador, aquí puedes crear cursos, eliminarlos, asignar profesores y estudiantes a cada uno, y manejar todo el sistema de gestión de notas."

if __name__=="__main__":
    app.run(debug=True)