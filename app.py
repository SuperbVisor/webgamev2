from flask import Flask, render_template, request, redirect, url_for, session, flash
from authlib.integrations.flask_client import OAuth
import sqlite3
import os
import subprocess
import pytz
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Ganti dengan kunci rahasia Anda

# Konfigurasi OAuth
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Hanya untuk pengembangan lokal
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='260418655884-g8qql6osd9hclkof5835g4hv6j8qekib.apps.googleusercontent.com',
    client_secret='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',
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'}
)

def get_wib_timestamp():
    wib = pytz.timezone('Asia/Jakarta')  # Zona waktu WIB
    return datetime.now(wib).strftime('%Y-%m-%d %H:%M:%S')

# Fungsi untuk menghubungkan ke database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Halaman utama (login)
@app.route('/')
def home():
    return render_template('login.html')

# Halaman pendaftaran
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # Simpan pengguna baru ke database
        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', (username, password, email))
        conn.commit()
        conn.close()

        return redirect(url_for('home'))

    return render_template('register.html')

# Halaman login manual
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()

        if user:
            if username == 'admin123' and password == 'admin123':
                session['username'] = username
                session['role'] = 'admin'  # Tambahkan role admin
                return redirect(url_for('admin_dashboard'))
            else:
                session['username'] = username
                session['role'] = 'user'  # Tambahkan role user
                return redirect(url_for('user_dashboard'))

    return render_template('login.html')

# Halaman login dengan Google
@app.route('/login/google')
def login_google():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token = google.authorize_access_token()
    user_info = google.get('userinfo').json()

    # Simpan pengguna Google ke database jika belum ada
    conn = get_db_connection()
    conn.execute('INSERT OR IGNORE INTO users (username, email, password) VALUES (?, ?, ?)',
                 (user_info['name'], user_info['email'], 'google_user'))
    conn.commit()
    conn.close()

    session['username'] = user_info['name']
    return redirect(url_for('user_dashboard'))

# Halaman dashboard admin
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' in session and session.get('role') == 'admin':
        conn = get_db_connection()
        new_messages_count = conn.execute("SELECT COUNT(*) FROM messages WHERE recipient = 'admin123'").fetchone()[0]
        conn.close()
        return render_template('admin_dashboard.html', new_messages_count=new_messages_count)
    return redirect(url_for('home'))

@app.route('/manage_users')
def manage_users():
    if 'username' in session and session['username'] == 'admin123':
        conn = get_db_connection()
        users = conn.execute('SELECT * FROM users').fetchall()
        conn.close()
        return render_template('manage_users.html', users=users)
    return redirect(url_for('home'))

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'username' in session and session['username'] == 'admin123':
        conn = get_db_connection()
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        flash('User  deleted successfully.')
        return redirect(url_for('manage_users'))
    return redirect(url_for('home'))

# Halaman dashboard user
@app.route('/user_dashboard')
def user_dashboard():
    if 'username' in session and session.get('role') == 'user':
        return render_template('user_dashboard.html')
    return redirect(url_for('home'))

def get_db_connection():
    conn = sqlite3.connect('database.db')  # Ganti dengan path ke database Anda
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/send_feedback', methods=['POST'])
def send_feedback():
    message = request.form['message']
    sender = session['username']  # Ambil username dari session
    recipient = 'admin123'  # Pesan ditujukan ke admin123

    # Dapatkan timestamp WIB
    timestamp = get_wib_timestamp()

    # Simpan pesan ke database dengan timestamp WIB
    conn = get_db_connection()
    conn.execute("INSERT INTO messages (sender, recipient, message, timestamp) VALUES (?, ?, ?, ?)", 
                 (sender, recipient, message, timestamp))
    conn.commit()
    conn.close()

    flash('Your message has been sent to Admin!', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/view_reports')
def view_reports():
    conn = get_db_connection()
    messages = conn.execute("SELECT * FROM messages WHERE recipient = 'admin123' ORDER BY timestamp DESC").fetchall()
    conn.close()
    return render_template('view_reports.html', messages=messages)

@app.route('/pilih_game')
def pilih_game():
    if 'username' in session:
        return render_template('pilih_game.html')
    return redirect(url_for('home'))

@app.route('/play_game1')
def play_game1():
    try:
        # Path lengkap ke file jumpy_game.py
        game_path = os.path.join(os.getcwd(), 'Game1/jumpy_game.py')
        
        # Menjalankan game sebagai proses terpisah
        subprocess.Popen(['python', game_path])
        
        flash('Game sedang berjalan. Silakan mainkan!', 'success')
        return redirect(url_for('pilih_game'))
    except Exception as e:
        flash(f'Gagal menjalankan game: {e}', 'danger')
        return redirect(url_for('pilih_game'))

@app.route('/play_game2')
def play_game2():
    try:
        game_path = os.path.join(os.getcwd(), 'Game2/main.py')
        
        subprocess.Popen(['python', game_path])
        
        flash('Game sedang berjalan. Silakan mainkan!', 'success')
        return redirect(url_for('pilih_game'))
    except Exception as e:
        flash(f'Gagal menjalankan game: {e}', 'danger')
        return redirect(url_for('pilih_game'))

@app.route('/play_game3')
def play_game3():
    try:
        game_path = os.path.join(os.getcwd(), 'Game3/car_game.py')
        
        subprocess.Popen(['python', game_path])
        
        flash('Game sedang berjalan. Silakan mainkan!', 'success')
        return redirect(url_for('pilih_game'))
    except Exception as e:
        flash(f'Gagal menjalankan game: {e}', 'danger')
        return redirect(url_for('pilih_game'))

@app.route('/play_game4')
def play_game4():
    try:
        game_path = os.path.join(os.getcwd(), 'Game4/PixelAdventure.py')
        
        subprocess.Popen(['python', game_path])
        
        flash('Game sedang berjalan. Silakan mainkan!', 'success')
        return redirect(url_for('pilih_game'))
    except Exception as e:
        flash(f'Gagal menjalankan game: {e}', 'danger')
        return redirect(url_for('pilih_game'))

# Halaman logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)  # Bersihkan role juga
    return redirect(url_for('home'))

if __name__ == '__main__':
    # Buat tabel users jika belum ada
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE,
                        email TEXT,
                        password TEXT
                    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sender TEXT NOT NULL,
                        recipient TEXT NOT NULL,
                        message TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )''')

    app.run(debug=True)
