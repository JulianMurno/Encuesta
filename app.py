import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)

# Función para obtener la conexión a la base de datos
def get_db_connection():
    conn = sqlite3.connect('encuestas.db')
    conn.row_factory = sqlite3.Row
    return conn

# Ruta principal: Mostrar todas las encuestas activas
@app.route('/')
def index():
    conn = get_db_connection()
    encuestas = conn.execute('SELECT * FROM Encuestas WHERE fecha_fin >= DATE("now")').fetchall()
    conn.close()
    return render_template('index.html', encuestas=encuestas)

# Ruta para ver los detalles de una encuesta
@app.route('/encuesta/<int:encuesta_id>')
def encuesta(encuesta_id):
    conn = get_db_connection()
    encuesta = conn.execute('SELECT * FROM Encuestas WHERE id = ?', (encuesta_id,)).fetchone()
    conn.close()
    if encuesta is None:
        return 'Encuesta no encontrada', 404
    return render_template('encuesta.html', encuesta=encuesta)

# Ruta para ver los resultados de una encuesta
@app.route('/resultados/<int:encuesta_id>')
def resultados(encuesta_id):
    conn = get_db_connection()
    encuesta = conn.execute('SELECT * FROM Encuestas WHERE id = ?', (encuesta_id,)).fetchone()
    
    # Obtener todas las preguntas
    preguntas = conn.execute('SELECT * FROM Preguntas WHERE encuesta_id = ?', (encuesta_id,)).fetchall()

    # Obtener las respuestas agrupadas por pregunta
    respuestas = {}
    for pregunta in preguntas:
        respuestas[pregunta['id']] = conn.execute(
            'SELECT respuesta FROM Respuestas WHERE pregunta_id = ?',
            (pregunta['id'],)
        ).fetchall()

    conn.close()

    if encuesta is None:
        return 'Encuesta no encontrada', 404
    
    return render_template('resultados.html', encuesta=encuesta, preguntas=preguntas, respuestas=respuestas)




# Ruta para realizar una encuesta (renombrado para evitar conflicto)
@app.route('/encuestar/<int:encuesta_id>', methods=['GET', 'POST'])
def realizar_encuesta(encuesta_id):
    conn = get_db_connection()
    encuesta = conn.execute('SELECT * FROM Encuestas WHERE id = ?', (encuesta_id,)).fetchone()
    preguntas = conn.execute('SELECT * FROM Preguntas WHERE encuesta_id = ?', (encuesta_id,)).fetchall()

    if request.method == 'POST':
        # Guardar las respuestas en la base de datos
        for pregunta in preguntas:
            respuesta = request.form.get(f"{pregunta['id']}")  # Usando el nombre de la columna para acceder al id de la pregunta
            if respuesta:
                # Insertar la respuesta en la tabla Respuestas
                conn.execute('''INSERT INTO Respuestas (encuesta_id, pregunta_id, respuesta)
                                VALUES (?, ?, ?)''', 
                             (encuesta_id, pregunta['id'], respuesta))  # Usando el nombre de la columna
        conn.commit()
        conn.close()

        return render_template('gracias.html')  # Página de agradecimiento después de enviar la respuesta

    conn.close()
    return render_template('encuestar.html', encuesta=encuesta, preguntas=preguntas)




if __name__ == '__main__':
    app.run(debug=True)
