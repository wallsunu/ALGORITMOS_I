from flask import Flask, render_template, jsonify, request, redirect, url_for, session, g, flash
import sqlite3
from datetime import datetime
import calendar
import re

# Inicializa la aplicación Flask y establece la carpeta de plantillas
app = Flask(__name__, template_folder=r'C:\Users\sanny\OneDrive\Documents\de0\env\templates')
app.secret_key = 'tu_clave_secreta'

# Nombre del archivo de base de datos SQLite
DATABASE = 'database.db'

# Configuración de la conexión a la base de datos SQLite
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

# Crear las tablas si no existen    
def create_table():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        # Tabla de usuarios
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL,
                            peso REAL,
                            talla REAL,
                            genero TEXT)''')

        # Tabla de comidas
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS comidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                kcal INTEGER,
                proteinas INTEGER,
                grasas INTEGER,
                tipo TEXT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabla de progreso del usuario
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS progreso_usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                porcentaje INTEGER,
                perdida_peso INTEGER,
                frecuencia_ejercicio INTEGER,
                consumo_agua INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Tabla de historial de recetas
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS historial (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                calorias INTEGER NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabla para registrar agua
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS agua (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            cantidad INTEGER,  -- Cantidad de agua en mililitros (o la unidad que elijas)
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(usuario_id)
        )
        ''')

        # Tabla para registrar ejercicio
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ejercicio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            duracion INTEGER,  -- Duración del ejercicio en minutos (o la unidad que elijas)
            tipo TEXT,         -- Tipo de ejercicio (opcional)
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(usuario_id)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS progreso_del_dia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            peso REAL,
            comentarios TEXT
        )
        ''')
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS progreso_nutrientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            nutrientes TEXT NOT NULL
        )
        """)

        # Confirmar los cambios
        db.commit()

# Llamamos a la función para crear las tablas al iniciar la aplicación
create_table()


# Cerrar la conexión a la base de datos al finalizar la petición
@app.teardown_appcontext
def close_db(error):
    if 'db' in g:
        g.db.close()

# Foros
forums = {
    "inicio": [],
    "ejercicios": [],
    "recetas": []
}

# Lista de nutrientes registrados
nutrientes_registrados = []

@app.route('/progreso')
def progreso():
    db = get_db()
    cursor = db.cursor()

    # Metas
    meta_agua = 10
    meta_ejercicio = 10

    # Obtener datos del usuario
    cursor.execute('SELECT SUM(cantidad) FROM agua WHERE user_id = ?', (1,))
    total_agua = cursor.fetchone()[0] or 0

    cursor.execute('SELECT SUM(duracion) FROM ejercicio WHERE user_id = ?', (1,))
    total_ejercicio = cursor.fetchone()[0] or 0

    # Calcular porcentajes
    porcentaje_agua = min((total_agua / meta_agua) * 10, 20)
    porcentaje_ejercicio = min((total_ejercicio / meta_ejercicio) * 10, 10)

    return render_template('progreso.html', 
                           porcentaje_agua=porcentaje_agua, 
                           porcentaje_ejercicio=porcentaje_ejercicio)


    
def insertar_datos_prueba():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        # Insertar datos de prueba para agua
        cursor.execute('INSERT INTO agua (user_id, cantidad) VALUES (?, ?)', (1, 1500))
        cursor.execute('INSERT INTO agua (user_id, cantidad) VALUES (?, ?)', (1, 600))

        # Insertar datos de prueba para ejercicio
        cursor.execute('INSERT INTO ejercicio (user_id, duracion, tipo) VALUES (?, ?, ?)', (1, 20, 'correr'))
        cursor.execute('INSERT INTO ejercicio (user_id, duracion, tipo) VALUES (?, ?, ?)', (1, 15, 'caminar'))

        db.commit()

# Llamar a la función para insertar los datos de prueba
insertar_datos_prueba()


    
def insertar_datos_prueba():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        # Insertar datos de prueba para agua
        cursor.execute('INSERT INTO agua (user_id, cantidad) VALUES (?, ?)', (1, 1500))
        cursor.execute('INSERT INTO agua (user_id, cantidad) VALUES (?, ?)', (1, 600))

        # Insertar datos de prueba para ejercicio
        cursor.execute('INSERT INTO ejercicio (user_id, duracion, tipo) VALUES (?, ?, ?)', (1, 20, 'correr'))
        cursor.execute('INSERT INTO ejercicio (user_id, duracion, tipo) VALUES (?, ?, ?)', (1, 15, 'caminar'))

        db.commit()

# Llamar a la función para insertar los datos de prueba
insertar_datos_prueba()


# Rutas de la aplicación

@app.route('/')
def index():
    return render_template('presentacion.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['usuario']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        
        if user:
            # Guardar los datos del usuario en la sesión
            session['username'] = username
            session['peso'] = user['peso']
            session['talla'] = user['talla']
            session['genero'] = user['genero']
            
            return redirect(url_for('registrar_datos'))  # Redirigir a registrar_datos si es necesario
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos.")

    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor()
        
        try:
            # Insertar el nuevo usuario en la base de datos
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            db.commit()
            
            # Iniciar sesión después del registro exitoso
            session['username'] = username
            return redirect(url_for('registrar_datos'))
        
        except sqlite3.IntegrityError:
            # El nombre de usuario ya existe
            return render_template('registro.html', error="El nombre de usuario ya existe.")
        except Exception as e:
            # Manejo de errores generales
            print(f"Ocurrió un error: {e}")
            return render_template('registro.html', error="Ocurrió un error, intenta nuevamente.")
    
    return render_template('registro.html')

@app.route('/volver', methods=['GET'])
def volver():
    return redirect(url_for('login'))

@app.route('/registroDatos', methods=['GET', 'POST'])
def registrar_datos():
    # Verifica si ya existen los datos en la sesión
    if 'peso' in session and 'talla' in session and 'genero' in session:
        # Si ya están en la sesión, no pedirlos de nuevo
        return redirect(url_for('ajustes'))  # Redirigir a ajustes o alguna otra página
    
    if request.method == 'POST':
        genero = request.form.get('genero')
        peso = float(request.form.get('peso'))  # Convertir a float
        talla = float(request.form.get('talla'))  # Mantener en cm

        # Asegúrate de que los valores son positivos
        if peso <= 0 or talla <= 0:
            return "Peso y talla deben ser positivos", 400  # Manejo de errores

        # Convertir talla de cm a metros
        talla_metros = talla / 100  # Convertir a metros

        # Calcular IMC
        imc = peso / (talla_metros ** 2)

        # Almacenar los datos en la sesión
        session['genero'] = genero
        session['peso'] = peso
        session['talla'] = talla  # Almacenar en cm
        session['imc'] = imc  # Almacenar el IMC

        # Redirigir a la página de peso después de registrar los datos
        return redirect(url_for('peso'))

    return render_template('registrar_datos.html')


@app.route('/set_dieta', methods=['GET', 'POST'])
def set_dieta():
    dieta = request.form['dieta']
    session['dieta'] = dieta
    return redirect(url_for('vegano') if dieta == 'vegano' else 'index')

@app.route('/reset_dieta')
def reset_dieta():
    session.pop('dieta', None)
    return redirect(url_for('ajustes'))

# Inicialización de variables para las comidas y totales
meals = {
    'desayuno': [],
    'almuerzo': [],
    'cena': []
}

total_kcal = 0
total_proteinas = 0
total_grasas = 0
meta_kcal = 2000

@app.route('/plan')
def plan():
    db = get_db()
    total_data = db.execute('SELECT SUM(kcal) as total_kcal, SUM(proteinas) as total_proteinas, SUM(grasas) as total_grasas FROM comidas').fetchone()
    
    return render_template("plan.html", 
                           total_kcal=total_data['total_kcal'] or 0, 
                           proteinas=total_data['total_proteinas'] or 0, 
                           grasas=total_data['total_grasas'] or 0, 
                           meta_kcal=meta_kcal)


@app.route('/add_meal', methods=['POST'])
def add_meal():
    nombre = request.form.get("meal_name")
    kcal = int(request.form.get("kcal", 0))
    proteinas = int(request.form.get("proteinas", 0))
    grasas = int(request.form.get("grasas", 0))
    meal_type = request.form.get("meal_type")

    # Guardar la comida en la base de datos
    db = get_db()
    db.execute('INSERT INTO comidas (nombre, kcal, proteinas, grasas, tipo) VALUES (?, ?, ?, ?, ?)',
               (nombre, kcal, proteinas, grasas, meal_type))
    db.commit()

    # Calcular el progreso
    total_data = db.execute('SELECT SUM(kcal) as total_kcal FROM comidas').fetchone()
    progreso = min((total_data['total_kcal'] or 0) / meta_kcal * 100, 100)  # Limitar a 100%

    return jsonify({
        "total_kcal": total_data['total_kcal'] or 0,
        "proteinas": proteinas,
        "grasas": grasas,
        "progreso": progreso
    })


@app.route("/reset_totals", methods=["POST"])
def reset_totals():
    db = get_db()
    db.execute('DELETE FROM comidas')
    db.commit()
    
    return jsonify({
        "total_kcal": 0,
        "proteinas": 0,
        "grasas": 0,
        "progreso": 0
    })


recetas = [
    {"nombre": "Sándwich de pollo con zanahorias", "detalles": "1 sándwich (221 g) - 407 kcal"},
    {"nombre": "Pollo a la Mostaza y Orégano", "detalles": "1 porción (278 g) - 390 kcal"},
    {"nombre": "Sándwich de Pollo con Zanahoria y Espinaca", "detalles": "797 kcal"},
]

# Ruta para "historial"
@app.route('/historial', methods=['GET', 'POST'])
def historial():
    # Obtener el historial de recetas de la base de datos
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM historial")
    recetas_historial = cursor.fetchall()
    return render_template('historial.html', recetas=recetas_historial)

@app.route('/agregar_historial', methods=['POST'])
def agregar_historial():
    desayuno_kcal = request.form.get('desayuno_kcal')
    almuerzo_kcal = request.form.get('almuerzo_kcal')
    cena_kcal = request.form.get('cena_kcal')

    # Calcular el total de calorías
    total_calorias = int(desayuno_kcal or 0) + int(almuerzo_kcal or 0) + int(cena_kcal or 0)

    # Insertar en la tabla de historial
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO historial (nombre, calorias) VALUES (?, ?)
    ''', ("Plan de hoy", total_calorias))
    db.commit()

    return redirect(url_for('historial'))




@app.route('/vegano', methods=['GET', 'POST'])
def vegano():
    if request.method == 'POST':
        opcion = request.form.get('opcion')
        session['opcion'] = opcion
        return redirect(url_for('recetas'))
    return render_template('vegano.html')

# Ruta para "recetas"
@app.route('/recetas', methods=['GET', 'POST'])
def recetas():
    if request.method == 'POST':
        # Obtener los valores de las calorías
        desayuno_kcal = int(request.form['desayuno_kcal'])
        almuerzo_kcal = int(request.form['almuerzo_kcal'])
        cena_kcal = int(request.form['cena_kcal'])

        # Calcular las calorías totales
        total_calorias = desayuno_kcal + almuerzo_kcal + cena_kcal

        # Insertar la receta en la base de datos
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''INSERT INTO historial (nombre, calorias) VALUES (?, ?)''', 
                       ('Desayuno + Almuerzo + Cena', total_calorias))
        db.commit()

        # Redirigir al historial después de guardar
        return redirect(url_for('historial'))

    return render_template('recetas.html')

@app.route('/comunidad')
def comunidad():
    return render_template('comunidad.html')

@app.route('/comunidad/<section>', methods=['GET', 'POST'])
def foro_section(section):
    if section not in forums:
        return redirect(url_for('comunidad'))

    # Verifica si el usuario está logueado
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = session['username']  # Obtén el nombre de usuario desde la sesión
        content = request.form['content']
        message = {'username': username, 'content': content}
        forums[section].append(message)
        return redirect(url_for('foro_section', section=section))

    return render_template('foro_section.html', section=section, messages=forums[section])


@app.route('/ajustes', methods=['GET', 'POST'])
def ajustes():
    # Verifica si el usuario está autenticado
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirige al login si no está autenticado

    # Obtenemos los valores del usuario desde la sesión
    usuario = {
        'nombre': session.get('username', 'Usuario'),
        'peso': session.get('peso', None),
        'talla': session.get('talla', None),
        'genero': session.get('genero', 'No especificado')
    }

    # Si el formulario es enviado con los datos de actualización
    if request.method == 'POST':
        # Actualizamos los valores en la sesión con los nuevos datos
        if 'newPeso' in request.form:
            session['peso'] = request.form['newPeso']
        if 'newTalla' in request.form:
            session['talla'] = request.form['newTalla']
        if 'newGenero' in request.form:
            session['genero'] = request.form['newGenero']
        if 'newUsername' in request.form:
            session['username'] = request.form['newUsername']

        # Confirmación de cambios
        flash('Datos actualizados correctamente', 'success')

        return redirect(url_for('ajustes'))  # Redirigimos a ajustes para mostrar los cambios

    return render_template('ajustes.html', usuario=usuario)

@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        new_username = request.form['newUsername']
        new_peso = request.form['newPeso']
        new_talla = request.form['newTalla']
        new_genero = request.form['newGenero']  # Obtener el nuevo género

        # Actualiza la base de datos
        cursor.execute("UPDATE users SET username = ?, peso = ?, talla = ?, genero = ? WHERE username = ?", 
                       (new_username, new_peso, new_talla, new_genero, session['username']))
        db.commit()

        # Actualiza la sesión con el nuevo nombre de usuario
        session['username'] = new_username

        # Renderiza la misma página de actualización de perfil con los nuevos datos
        return render_template('ajustes.html', usuario={'nombre': new_username, 'peso': new_peso, 'talla': new_talla, 'genero': new_genero})

    # Si se accede mediante GET, muestra la página de actualización de perfil
    cursor.execute("SELECT peso, talla, genero FROM users WHERE username = ?", (session['username'],))
    user_data = cursor.fetchone()
    peso = user_data[0]
    talla = user_data[1]
    genero = user_data[2]

    return render_template('ajustes.html', usuario={'nombre': session['username'], 'peso': peso, 'talla': talla, 'genero': genero})

@app.route('/borrar_cuenta', methods=['POST'])
def borrar_cuenta():
    if 'username' in session:
        username = session['username']

        # Conectar a la base de datos
        db = get_db()
        cursor = db.cursor()

        # Eliminar al usuario de la base de datos
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        db.commit()

        # Limpiar la sesión
        session.clear()

    return redirect(url_for('login'))  # Redirigir al login después de borrar la cuenta

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/registroNutrientes', methods=['GET', 'POST'])
@app.route('/registroNutrientes/<int:mes>/<int:year>/<int:dia>', methods=['GET', 'POST'])
def registro_nutrientes(mes=None, year=None, dia=None):
    if mes is None or year is None or dia is None:
        # Aquí podrías obtener los valores por defecto (por ejemplo, el mes actual o el día actual)
        from datetime import datetime
        today = datetime.today()
        mes = today.month
        year = today.year
        dia = today.day

    # Lógica para registrar los nutrientes
    return render_template('registroNutrientes.html', mes=mes, year=year, dia=dia)



@app.route('/calendario', methods=['GET'])
def calendario():
    year = int(request.args.get('year', datetime.now().year))
    mes = int(request.args.get('mes', datetime.now().month))

    # Crear el calendario
    cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
    dias_del_mes = cal.monthdayscalendar(year, mes)

    # Mes y año en formato para el título
    mes_nombre = calendar.month_name[mes]

    return render_template('calendario.html', mes=mes, year=year, mes_nombre=mes_nombre, dias_del_mes=dias_del_mes)


@app.route('/')
def home():
    # Ejemplo de cómo usar url_for con los parámetros mes, año y dia
    mes = 11
    year = 2024
    dia = 18
    # Generar la URL para la ruta 'dia'
    url = url_for('dia', mes=mes, year=year, dia=dia)
    return f'<a href="{url}">Ir al día</a>'

@app.route('/dia/<int:mes>/<int:year>/<int:dia>', methods=['GET', 'POST'])
def dia(mes, year, dia):
    # Crear la fecha en formato 'YYYY-MM-DD' para usar en la base de datos
    fecha = f"{year}-{mes:02d}-{dia:02d}"

    # Obtener los datos del día desde la base de datos
    datos = obtener_datos_del_dia(fecha)

    if request.method == 'POST':
        # Si el formulario fue enviado, guardar los nuevos datos
        peso = request.form['peso']
        comentarios = request.form['comentarios']
        guardar_datos_del_dia(fecha, peso, comentarios)
        return render_template('dia.html', mes=mes, year=year, dia=dia, datos=(peso, comentarios))

    return render_template('dia.html', mes=mes, year=year, dia=dia, datos=datos)


# Ruta para la página de peso
@app.route('/peso', methods=['GET', 'POST'])
def peso():
    # Obtener IMC desde la sesión
    imc = session.get('imc')
    
    if request.method == 'POST':
        current_weight = request.form.get('currentWeight')
        target_weight = request.form.get('targetWeight')

        session['current_weight'] = current_weight
        session['target_weight'] = target_weight

        # Redirigir a otra página si es necesario, por ejemplo a 'plan.html'
        return render_template('plan.html', total_kcal=0, proteinas=0, grasas=0)

    return render_template('peso.html', imc=imc)  # Pasar IMC a la plantilla

# Ruta para manejar los recordatorios de agua y ejercicio
@app.route('/recordatorio', methods=['POST'])
def recordatorio():
    if 'waterIntake' in request.form:
        water_intake = request.form['waterIntake']
        # Guardar en la base de datos
        conn = get_db()
        conn.execute('INSERT INTO recordatorios (tipo, cantidad) VALUES (?, ?)', ('agua', water_intake))
        conn.commit()
        conn.close()
        return redirect(url_for('progreso'))  # Redirigir al progreso después de registrar el agua

    if 'exerciseTime' in request.form:
        exercise_time = request.form['exerciseTime']
        # Guardar en la base de datos
        conn = get_db()
        conn.execute('INSERT INTO recordatorios (tipo, cantidad) VALUES (?, ?)', ('ejercicio', exercise_time))
        conn.commit()
        conn.close()
        return redirect(url_for('progreso'))  # Redirigir al progreso después de registrar el ejercicio

    return redirect(url_for('peso'))
def recordatorio():
    db = get_db()
    if 'waterIntake' in request.form:
        water_intake = int(request.form['waterIntake'])
        db.execute('INSERT INTO agua (user_id, cantidad) VALUES (?, ?)', (1, water_intake))
    
    if 'exerciseTime' in request.form:
        exercise_time = int(request.form['exerciseTime'])
        db.execute('INSERT INTO ejercicio (user_id, duracion, tipo) VALUES (?, ?, ?)', (1, exercise_time, 'ejercicio'))

    db.commit()

    # Redirigir al progreso para mostrar los datos actualizados
    return redirect(url_for('progreso'))

# Función para guardar los datos del día en la base de datos
def guardar_datos_del_dia(fecha, nutrientes):
    conn = sqlite3.connect('fitness.db')  # Asegúrate de que este archivo existe
    cursor = conn.cursor()
    cursor.execute("INSERT INTO progreso_nutrientes (fecha, nutrientes) VALUES (?, ?)", (fecha, nutrientes))
    conn.commit()
    conn.close()

# Función para obtener los datos del día desde la base de datos
def obtener_datos_del_dia(fecha):
    conn = sqlite3.connect('fitness.db')  # Nombre de tu base de datos
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM progreso_del_dia WHERE fecha = ?", (fecha,))
    datos = cursor.fetchone()  # Devuelve una tupla con los datos o None si no hay resultados
    conn.close()

    return datos

# Inicio de la aplicación
if __name__ == '__main__':
    app.run(debug=True)

