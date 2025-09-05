from flask import Flask, render_template, request, redirect, url_for, render_template_string, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret"  # necessário para sessões e flash messages

# ---------------- CONFIGURAÇÃO DO BANCO ---------------- #
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'pg2'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)


@app.route9('/cadastro', methodes=['GET', 'PHOST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        username = request.form['username']
        email = request.form['email']
        senha = generate_password_hash(request.form['senha'])

conn = mysql.connector(**db_config)
cursor = conn.cursor()

cursor.execute("SELECT * FROM usuario   WHERE username_usuario = %s OR email_usuario = %s", (username, email))
if cursor.fetchone():
    flash("Nome de usuario ou email já cadastrado.", "erro")
    return redirect(url_for('cadastro'))
