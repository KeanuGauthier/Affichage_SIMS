from flask import Flask, jsonify, render_template
import mysql.connector
from config import DATABASE

app = Flask(__name__)

def get_measures():
    # Connexion à la base de données MySQL
    connection = mysql.connector.connect(
        host=DATABASE['host'],
        user=DATABASE['user'],
        password=DATABASE['password'],
        database=DATABASE['database']
    )
    cursor = connection.cursor(dictionary=True)

    # Récupération des mesures non marquées (tag = FALSE ou NULL)
    query_select = """
    SELECT id, x, y, angle, distance0, distance1, distance2, distance3, distance4, 
           vitesse_moteur_droit, vitesse_moteur_gauche, date_heure
    FROM mesures
    WHERE tag = FALSE OR tag IS NULL
    ORDER BY date_heure ASC;
    """
    cursor.execute(query_select)
    measures = cursor.fetchall()

    if measures:
        # Mise à jour des mesures pour les marquer comme "traitées"
        ids = [str(measure['id']) for measure in measures]
        query_update = f"""
        UPDATE mesures
        SET tag = TRUE
        WHERE id IN ({", ".join(ids)});
        """
        cursor.execute(query_update)
        connection.commit()

    # Fermeture de la connexion et retour des mesures
    cursor.close()
    connection.close()
    return measures

@app.route('/data')
def data():
    measures = get_measures()
    return jsonify(measures)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)