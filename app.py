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

# ---------------- ROTAS PRINCIPAIS ---------------- #

@app.route("/")
def home():
    return render_template("base.html")

@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@app.route("/login")
def login():
    return render_template("login.html")

# ---------------- CADASTRO ---------------- #

@app.route("/cadastrar", methods=["POST"])
def novo_usuario():
    nome = request.form.get("first_name")
    sobrenome = request.form.get("last_name")
    username = request.form.get("username")
    email = request.form.get("email")
    senha = request.form.get("password")

    if not all([nome, sobrenome, username, email, senha]):
        flash("Preencha todos os campos.", "warning")
        return redirect(url_for("cadastro"))

    senha_hash = generate_password_hash(senha)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Verifica duplicados
    cursor.execute("SELECT * FROM usuarios WHERE email=%s OR username=%s", (email, username))
    existing = cursor.fetchone()
    if existing:
        flash("Email ou usuário já cadastrado.", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for("cadastro"))

    # Insere novo usuário
    cursor.execute(
        "INSERT INTO usuarios (nome, sobrenome, username, email, senha) VALUES (%s, %s, %s, %s, %s)",
        (nome, sobrenome, username, email, senha_hash)
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("Usuário cadastrado com sucesso! Faça login.", "success")
    return redirect(url_for("login"))

# ---------------- LOGIN ---------------- #

@app.route("/login_usuario", methods=["POST"])
def loginUser():
    login_usuario = request.form.get("login_user")
    senha = request.form.get("password")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE email=%s OR username=%s", (login_usuario, login_usuario))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()

    if usuario and check_password_hash(usuario["senha"], senha):
        session["nome"] = usuario["nome"]
        session["sobrenome"] = usuario["sobrenome"]
        session["username"] = usuario["username"]
        session["email"] = usuario["email"]

        flash(f"Bem-vindo, {usuario['nome']}!", "success")
        return redirect(url_for("home"))
    else:
        return render_template_string("""
            <script>
                alert("Email ou senha incorretos.");
                window.location.href = "/login";
            </script>
        """)

# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():
    session.clear()
    flash("Logout realizado com sucesso.", "info")
    return redirect(url_for("login"))

# ---------------- PERFIL ---------------- #

@app.route("/perfil")
def perfil():
    if "email" not in session:
        flash("Você precisa estar logado.", "warning")
        return redirect(url_for("login"))
    return render_template("perfil.html")

@app.route("/perfil/atualizado", methods=["POST"])
def update_perfil():
    if "email" not in session:
        flash("Você precisa estar logado.", "warning")
        return redirect(url_for("login"))

    novo_nome = request.form.get("nome")
    novo_sobrenome = request.form.get("sobrenome")
    novo_username = request.form.get("username")
    novo_email = request.form.get("email")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios WHERE email=%s", (session["email"],))
    usuario = cursor.fetchone()

    if usuario:
        cursor.execute(
            "UPDATE usuarios SET nome=%s, sobrenome=%s, username=%s, email=%s WHERE id=%s",
            (novo_nome or usuario["nome"],
             novo_sobrenome or usuario["sobrenome"],
             novo_username or usuario["username"],
             novo_email or usuario["email"],
             usuario["id"])
        )
        conn.commit()

        # Atualiza sessão
        session["nome"] = novo_nome or usuario["nome"]
        session["sobrenome"] = novo_sobrenome or usuario["sobrenome"]
        session["username"] = novo_username or usuario["username"]
        session["email"] = novo_email or usuario["email"]

        flash("Perfil atualizado com sucesso!", "success")
    else:
        flash("Usuário não encontrado.", "error")

    cursor.close()
    conn.close()
    return redirect(url_for("perfil"))

# ---------------- SOBRE ---------------- #

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

# ---------------- MAIN ---------------- #
if __name__ == "__main__":
    app.run(debug=True)
