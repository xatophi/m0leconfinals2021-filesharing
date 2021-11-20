from flask import Blueprint, render_template, make_response, url_for, request, flash, redirect, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
from uuid import uuid4
import requests
import os
from .models import File, SharedFile, User
from . import db, talisman

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    return make_response(render_template('home.html'))

@main.route('/play')
@login_required
def play():
    xss = request.args.get('xss')
    return make_response(render_template('play.html',xss=xss))

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':

        if 'file' not in request.files:
            flash('No file part','error')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash('No selected file','error')
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            uuid = uuid4().hex
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], uuid))
            new_file = File(uuid=uuid, filename=filename, user_id=current_user.id)
            db.session.add(new_file)
            db.session.commit()
            flash('File uploaded','success')
            return redirect(url_for('main.show_files'))

    return make_response(render_template('upload.html'))

@main.route('/upload/<uuid>')
@login_required
@talisman(content_security_policy={'script-src':"'self'"})
def download_file(uuid):
    file = File.query.filter(File.uuid == uuid).first()

    if not file:
        flash('File not found','error')
        return redirect(url_for('main.show_files'))
    
    if file.user_id != current_user.id:
        
        sf = SharedFile.query.filter(SharedFile.file_uuid == file.uuid, SharedFile.user_id == current_user.id).first()
        if not sf:
            flash('Forbidden','error')
            return redirect(url_for('main.show_files'))

    return send_from_directory(current_app.config["UPLOAD_FOLDER"], uuid, as_attachment=True, download_name=file.filename)
    

@main.route('/files', methods=['GET'])
@login_required
def show_files():
    files = File.query.filter(File.user_id == current_user.id).all()
    shared_files = File.query.join(SharedFile, File.uuid == SharedFile.file_uuid).filter(SharedFile.user_id == current_user.id).all()
    return make_response(render_template('files.html', files=files, shared_files=shared_files))

@main.route('/share/<uuid>', methods=['GET','POST'])
@login_required
def share(uuid):
    file = File.query.filter(File.uuid == uuid).first()

    if not file:
        flash('File not found','error')
        return redirect(url_for('main.show_files'))
    elif file.user_id != current_user.id:
        flash('Forbidden','error')
        return redirect(url_for('main.show_files'))

    if request.method == 'POST':
        
        email = request.form.get('email')

        if not email:
            flash('Missing "email" value','error')
            return redirect(request.url)

        u = User.query.filter(User.email == email).first()
        
        if not u:
            flash('User not found','error')
            return redirect(request.url)

        if u.id == current_user.id:
            flash('WTF, why?','error')
            return redirect(request.url)
            
        if file.filename == 'flag':
            flash("It's file sharing not flag sharing",'error')
            return redirect(request.url)

        try:
            sf = SharedFile(file_uuid=file.uuid, user_id=u.id)

            db.session.add(sf)
            db.session.commit()
        except IntegrityError:
            flash('File already shared with this user','error')
            return redirect(request.url)

        flash('Shared','success')
        return redirect(request.url)

    return render_template('share.html')
    

@main.route('/abuse', methods=['GET','POST'])
@login_required
def report_abuse():
    if request.method == 'POST':
        url = request.form.get('url')
        team_token = request.form.get('token')

        if team_token and url and url.startswith('http'):
            try:
                # send the request to the bot to visit
                r = requests.post(os.environ['BOT_URL'],json={'url':url, 'token':team_token})
                if r:
                    flash('Visited','success')
                else:
                    flash(f'Error: {r.text}', 'error')
            except:
                flash('Error, contact an admin')
        else:
            flash('Invalid data','error')
            
    return render_template('abuse.html')