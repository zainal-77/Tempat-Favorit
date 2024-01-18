from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from math import radians, sin, cos, sqrt, atan2
import os
import time

app = Flask(__name__, static_url_path='/static')
CORS(app)

# Configure MySQL
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'tempat_favorit'

mysql = MySQL(app)

# Configure upload folder
UPLOAD_FOLDER = 'static/photos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


# Helper function to get all places from the database
def get_all_places_from_db():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM places')
    places = cur.fetchall()
    cur.close()
    return places


# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM places')
    places = cur.fetchall()
    cur.close()
    return render_template('index.html', places=places)


# Route untuk menambah tempat
@app.route('/add_place', methods=['POST'])
def add_place():
    name = request.form['name']
    latitude = float(request.form['latitude'])
    longitude = float(request.form['longitude'])
    photo = request.files.get('photo')

    if photo and allowed_file(photo.filename):
        filename = secure_filename(photo.filename)
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(photo_path)

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO places (name, latitude, longitude, photo) VALUES (%s, %s, %s, %s)',
                    (name, latitude, longitude, filename))
        mysql.connection.commit()
        cur.close()

        # Setelah menambahkan tempat, arahkan ulang ke halaman utama
        return redirect(url_for('index'))
    else:
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO places (name, latitude, longitude) VALUES (%s, %s, %s)',
                    (name, latitude, longitude))
        mysql.connection.commit()
        cur.close()

        # Setelah menambahkan tempat, arahkan ulang ke halaman utama
        return redirect(url_for('index'))


# Route untuk mengedit data
@app.route('/edit/<int:place_id>', methods=['GET'])
def edit_place(place_id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM places WHERE id = %s', (place_id,))
    place = cur.fetchone()
    cur.close()

    if place:
        # Jika tempat ditemukan, kirimkan halaman edit
        return render_template('edit.html', place=place)
    else:
        # Jika tempat tidak ditemukan, kirimkan respons 404 atau halaman lain
        return jsonify({'error': 'Place not found'}), 404


# Route untuk mengupdate data tempat
@app.route('/places/<int:place_id>', methods=['POST', 'PUT'])
def update_place(place_id):
    name = request.form['name']
    latitude = float(request.form['latitude'])
    longitude = float(request.form['longitude'])
    photo = request.files.get('photo')

    if photo and allowed_file(photo.filename):
        filename = secure_filename(photo.filename)
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(photo_path)

        cur = mysql.connection.cursor()
        cur.execute('UPDATE places SET name = %s, latitude = %s, longitude = %s, photo = %s WHERE id = %s',
                    (name, latitude, longitude, filename, place_id))
        mysql.connection.commit()
        cur.close()

        # Setelah memperbarui tempat, arahkan ulang ke halaman utama
        return redirect(url_for('index'))
    else:
        cur = mysql.connection.cursor()
        cur.execute('UPDATE places SET name = %s, latitude = %s, longitude = %s WHERE id = %s',
                    (name, latitude, longitude, place_id))
        mysql.connection.commit()
        cur.close()

        # Setelah memperbarui tempat, arahkan ulang ke halaman utama
        return redirect(url_for('index'))

@app.route('/places/<int:place_id>/delete', methods=['GET'])
def delete_place(place_id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM places WHERE id = %s', (place_id,))
    mysql.connection.commit()
    cur.close()

    # After deleting the place, redirect to the index page
    return redirect(url_for('index'))




# Route untuk menghitung jarak
@app.route('/calculate_distance', methods=['POST'])
def calculate_distance():
    place1_id = request.form['place1']
    place2_id = request.form['place2']

    cur = mysql.connection.cursor()
    cur.execute('SELECT latitude, longitude FROM places WHERE id IN (%s, %s)', (place1_id, place2_id))
    places_data = cur.fetchall()
    cur.close()

    if len(places_data) == 2:
        place1_latitude, place1_longitude = places_data[0]
        place2_latitude, place2_longitude = places_data[1]

        distance = calculate_haversine_distance(place1_latitude, place1_longitude, place2_latitude, place2_longitude)

        # Fetch places again for rendering
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM places')
        places = cur.fetchall()
        cur.close()

        return render_template('index.html', places=places, distance_result=f'Distance: {distance:.2f} km')
    else:
        return render_template('index.html', distance_result='Error calculating distance')


def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    # Earth radius in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    # Calculate the differences
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # Calculate the distance using Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


def run_sql_script(script_filename):
    with open(script_filename, 'r') as sql_file:
        commands = sql_file.read().split(';')
        cur = mysql.connection.cursor()
        for command in commands:
            if command.strip() != '':
                cur.execute(command)
        mysql.connection.commit()
        cur.close()


def setup_database():
    script_path = os.path.join(os.path.dirname(__file__), 'create_table.sql')
    run_sql_script(script_path)


def wait_for_mysql():
    max_retries = 30
    delay_seconds = 5

    for _ in range(max_retries):
        try:
            mysql.connection.ping()
            print("MySQL is ready!")
            return
        except Exception as e:
            print(f"MySQL not ready, retrying... ({e})")
            time.sleep(delay_seconds)

    print("Max retries reached, unable to connect to MySQL.")


if __name__ == '__main__':
    with app.app_context():
        wait_for_mysql()
        setup_database()
    app.run(debug=True, host='0.0.0.0')
