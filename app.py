import random
from flask import Flask, render_template
import pymysql

app = Flask(__name__)

@app.route('/')
def mostrar_numeros():
    return render_template('numeros.html')

# ... (otras rutas)

@app.route('/generar_numeros', methods=['POST'])
def generar_numeros():
    cantidad_aleatorios = 2

    # Validar que cantidad_aleatorios sea un número positivo
    if not isinstance(cantidad_aleatorios, int) or cantidad_aleatorios <= 0:
        return "La cantidad de números aleatorios debe ser un entero positivo."

    # Configuración de la conexión a la base de datos usando with statement
    try:
        with pymysql.connect(host='localhost', user='root', passwd='', db='bolsagana') as miConexion:
            cur = miConexion.cursor()

            # Obtener la cantidad total de registros en la tabla
            cur.execute("SELECT COUNT(*) FROM grupo")
            total_registros = cur.fetchone()[0]

            # Obtener la cantidad total de registros en la tabla para los números con estado=1
            cur.execute("SELECT COUNT(*) FROM grupo WHERE estado=1")
            total_registros_estado = cur.fetchone()[0]

            # Verificar si hay suficientes registros activos para obtener la cantidad deseada
            if total_registros_estado < cantidad_aleatorios:
                return "No hay suficientes registros activos para obtener la cantidad deseada."
            else:
                # Obtener 2 números aleatorios únicos con reemplazo
            # numeros_aleatorios = [f"{random.randint(0, 9):02d}" for _ in range(cantidad_aleatorios)]

            #print("numeros obtenidos :", numeros_aleatorios)

                # Crear la consulta SQL con los números aleatorios
                consulta_sql = f"SELECT code FROM grupo WHERE estado=1 ORDER BY RAND() LIMIT 2"
                cur.execute(consulta_sql)

                print(consulta_sql)


                # Obtener los códigos elegidos
                elegidos = [code[0] for code in cur.fetchall()]

                print("elegidos :", elegidos)

                if len(elegidos) == cantidad_aleatorios:
                    # Insertar los números aleatorios en la tabla "compra_boletas"
                    for num_aleatorio in elegidos:
                        cur.execute("INSERT INTO compra_boletas (code) VALUES (%s)", (num_aleatorio,))
                        # Actualizar el campo "estado" en la tabla "grupo"
                        cur.execute("UPDATE grupo SET estado = 0 WHERE code = %s", (num_aleatorio,))

                    # Confirmar la transacción y cerrar la conexión
                    miConexion.commit()

                    # Renderizar la plantilla HTML
                    return render_template('numeros.html', numeros=elegidos)
    except pymysql.Error as e:
        # Manejo de excepciones para errores de base de datos
        return f"Error de base de datos: {e}"

if __name__ == '__main__':
    app.run(debug=True)
