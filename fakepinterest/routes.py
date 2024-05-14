from flask import render_template, url_for, redirect
from fakepinterest import app, database, bcrypt
from flask_login import login_required, login_user,logout_user, current_user
from fakepinterest.forms import FormLogin, FormCriarConta, FormFoto
from fakepinterest.models import Usuario, Foto
import os
from werkzeug.utils import secure_filename

@app.route("/", methods=["GET", "POST"])
def homepage():
    formlogin = FormLogin()
    if formlogin.validate_on_submit():
        usuario = Usuario.query.filter_by(email=formlogin.email.data).first()
        if usuario :
            if bcrypt.check_password_hash(usuario.senha.encode("utf-8"), formlogin.senha.data):
                login_user(usuario, remember=True)
                return redirect(url_for("perfil", usuario=usuario.username))
    return render_template("homepage.html", form=formlogin)

@app.route("/criarconta", methods=["GET", "POST"])
def criar_conta():
    form_criarconta = FormCriarConta()
    
    if form_criarconta.validate_on_submit():
        print("dentro do if")
        senha = bcrypt.generate_password_hash(form_criarconta.senha.data).decode("utf-8")
        usuario = Usuario(username=form_criarconta.username.data, 
                          email=form_criarconta.email.data,
                          senha=senha)
        database.session.add(usuario)
        database.session.commit()
        login_user(usuario, remember=True)
        return redirect(url_for("perfil", usuario=usuario.username))
    else:
        print(form_criarconta.errors)
    return render_template("criarconta.html", form=form_criarconta)


@app.route("/perfil/<usuario>", methods =["GET", "POST"])
@login_required
def perfil(usuario): #recebe a string usuario
    usuario_perfil = Usuario.query.filter_by(username = usuario).first()
    if usuario_perfil.username == current_user.username:
        # o usuário está no prórprio perfil
        form_foto = FormFoto()
        if form_foto.validate_on_submit():
            arquivo = form_foto.foto.data
            nome_seguro = secure_filename(arquivo.filename)
            
            #salvar arquivo na pasta fotos_post
            caminho = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config["UPLOAD_FOLDER"], nome_seguro) 
            arquivo.save(caminho)
            #registrar arquivo no banco de dados
            foto = Foto(imagem= nome_seguro, id_usuario= current_user.id)
            database.session.add(foto)
            database.session.commit()
        return render_template("perfil.html", usuario=current_user, form = form_foto)
    else:
        # o usuário está vendo perfil de outro usuário
        return render_template("perfil.html", usuario=usuario_perfil, form=None)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))

@app.route("/feed")
@login_required
def feed():
    fotos = Foto.query.order_by(Foto.data_criacao.desc()).all()
    return render_template("feed.html", fotos = fotos)