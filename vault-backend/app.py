import os
import sys
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

# 🌐 Config Parameters
DB_HOST = os.getenv('DB_HOST', 'postgres-db')
DB_USER = os.getenv('DB_USER', 'vault_admin')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'SecretVaultPassword123!')
DB_NAME = os.getenv('DB_NAME', 'link_vault_prod')

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=5432
    )

def init_db():
    """Verifies backend database structure existence prior to listening for routing traffic"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS links (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            url TEXT NOT NULL,
            "group" VARCHAR(255) DEFAULT 'Tools & Utilities'
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("Database schema verification clear!", flush=True)

@app.route('/', methods=['GET', 'POST'])
def handle_links():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    if request.method == 'POST':
        data = request.json
        cur.execute(
            'INSERT INTO links (name, url, "group") VALUES (%s, %s, %s);',
            (data['name'], data['url'], data['group'])
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success"}), 201
        
    # GET method execution
    cur.execute('SELECT id, name, url, "group" FROM links ORDER BY id DESC;')
    links = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(links)

@app.route('/<int:link_id>', methods=['PUT', 'DELETE'])
def handle_single_link(link_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'DELETE':
        cur.execute('DELETE FROM links WHERE id = %s;', (link_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "deleted"}), 200
        
    if request.method == 'PUT':
        data = request.json
        cur.execute(
            'UPDATE links SET name = %s, url = %s, "group" = %s WHERE id = %s;',
            (data['name'], data['url'], data['group'], link_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "updated"}), 200

if __name__ == '__main__':
    # ⏳ Database Availability Validation loop
    retries = 20
    db_connected = False
    
    while retries > 0:
        try:
            print("Verifying structural pipeline backplane connection...", flush=True)
            init_db()
            db_connected = True
            break
        except Exception as e:
            print(f"Database network not accessible yet. Retrying in 3 seconds... ({e})", flush=True)
            time.sleep(3)
            retries -= 1

    if not db_connected:
        print("CRITICAL: Failed to connect to database engine. Exiting backend program.", flush=True)
        sys.exit(1)

    print("Starting Flask application engine listener layer...", flush=True)
    app.run(host='0.0.0.0', port=9000, debug=False)
