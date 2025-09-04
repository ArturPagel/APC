from flask import Flask, render_template, request, redirect, url_for, render_template_string, session, flash
from modelsTeste import *

import os
from werkzeug.utils import secure_filename
from pony.orm import Database, Required, Optional, Set, PrimaryKey, db_session, commit, select

db = Database()
app = Flask(__name__)



@app.route("/")
def home():
    return render_template("base.html")

@app.route("/auxiliar")
def cadastro():
    return render_template("cadastro.html")

@app.route("/acesso")
def acesso():
    return render_template("login.html")


@app.route("/acesso/cadastro/novo_usuario", methods=["POST"])
def novo_usuario():
    nome = request.form.get("first_name")
    sobrenome = request.form.get("last_name")
    username = request.form.get("username")
    email = request.form.get("email")
    senha = request.form.get("password")
    
    with db_session:
        novo_user = UsuarioTeste(nome=nome, sobrenome=sobrenome, username=username, email=email, senha=senha)
        commit()

        return redirect(url_for("login"))


@app.route("/acesso/login")
def login():
    return render_template("login.html")

@app.route("/acesso/login/usuario", methods=["POST"])
@db_session
def loginUser():
    login_usuario = request.form.get("login_user")
    senha = request.form.get("password")

    usuario = select(u for u in UsuarioTeste
                    if (u.email == login_usuario or u.username == login_usuario)
                    and u.senha == senha).first()

    if usuario:
        session["nome"] = usuario.nome
        session["sobrenome"] = usuario.sobrenome
        session["username"] = usuario.username
        session["email"] = usuario.email
        session["foto_perfil"] = usuario.foto

        return redirect(url_for("home"))
        
    else:
        return render_template_string("""
            <script>
                alert("Email ou senha incorretos.");
                window.location.href = "/acesso/login";
            </script>
        """)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/perfil")
def perfil():
    return render_template("perfil.html")

@app.route("/perfil/atualizado", methods=["POST"])
def update_perfil():
    novo_nome = request.form.get("nome")
    novo_sobrenome = request.form.get("sobrenome")
    novo_username = request.form.get("username")
    novo_email = request.form.get("email")
    nova_foto = request.files.get("foto_perfil")

    with db_session:
        usuario = UsuarioTeste.get(email=session.get("email"))

        if usuario:
            usuario.nome = novo_nome
            usuario.sobrenome = novo_sobrenome
            usuario.username = novo_username
            usuario.email = novo_email

            # Se uma nova foto foi enviada
            if nova_foto and nova_foto.filename != '':
                nome_arquivo = secure_filename(nova_foto.filename)
                caminho_foto = os.path.join(CAMINHO_FOTOS, nome_arquivo)
                url_foto = f'/static/imagens/fotosperfil/{nome_arquivo}'
                nova_foto.save(caminho_foto)

                # Atualiza no banco
                usuario.foto_perfil = f"/{caminho_foto}"

                # Atualiza na session
                session["foto_perfil"] = f"/{url_foto}"

            # Atualiza os dados na session
            session["nome"] = novo_nome
            session["sobrenome"] = novo_sobrenome
            session["username"] = novo_username
            session["email"] = novo_email

            flash("Perfil atualizado com sucesso!", "success")
            return redirect(url_for("perfil"))  # sua rota de perfil

        else:
            flash("Usuário não encontrado.", "error")
            return redirect(url_for("login"))

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")