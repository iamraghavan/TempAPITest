import secrets
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = '195.179.236.1'
app.config['MYSQL_USER'] = 'u888860508_egs'
app.config['MYSQL_PASSWORD'] = '232003@Anbu'
app.config['MYSQL_DB'] = 'u888860508_pegs'

mysql = MySQL(app)

# Secret key for JWT
app.config['SECRET_KEY'] = 'secrets.token_hex(32)'

def generate_token(user_id):
    payload = {
        'exp': datetime.utcnow() + timedelta(days=1),  # Token expiration time (e.g., 1 day)
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token

def token_required(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Unauthorized', 'message': 'Token is missing'}), 401

        user_id = verify_token(token)
        if not user_id:
            return jsonify({'error': 'Unauthorized', 'message': 'Invalid or expired token'}), 401

        return f(user_id, *args, **kwargs)

    decorated.__name__ = f.__name__
    return decorated

# Route to generate a JWT token for testing purposes
@app.route('/login', methods=['POST'])
def login():
    auth = request.json
    if auth and auth['username'] == 'testuser' and auth['password'] == 'testpassword':
        token = generate_token(1)  # Assuming user ID is 1 for this example
        return jsonify({'token': token})
    return jsonify({'error': 'Invalid credentials'}), 401

# Routes for CRUD operations
@app.route('/courses', methods=['GET'])
@token_required
def get_courses(user_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM courses")
        data = cur.fetchall()
        cur.close()
        return jsonify({'courses': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/courses/<int:course_id>', methods=['GET'])
@token_required
def get_course(user_id, course_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM courses WHERE course_id = %s", (course_id,))
        data = cur.fetchone()
        cur.close()
        if data:
            return jsonify({'course': data}), 200
        else:
            return jsonify({'message': 'Course not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/courses', methods=['POST'])
@token_required
def add_course(user_id):
    try:
        course_name = request.json.get('course_name')
        course_url = request.json.get('course_url')
        # Add more fields as per your table structure

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO courses (course_name, course_url, created_by) VALUES (%s, %s, %s)", (course_name, course_url, user_id))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Course added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/courses/<int:course_id>', methods=['PUT'])
@token_required
def update_course(user_id, course_id):
    try:
        course_name = request.json.get('course_name')
        course_url = request.json.get('course_url')
        # Add more fields as per your table structure

        cur = mysql.connection.cursor()
        cur.execute("UPDATE courses SET course_name = %s, course_url = %s WHERE course_id = %s", (course_name, course_url, course_id))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Course updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/courses/<int:course_id>', methods=['DELETE'])
@token_required
def delete_course(user_id, course_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM courses WHERE course_id = %s", (course_id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Course deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)
