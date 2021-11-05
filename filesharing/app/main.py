from flask import Blueprint, render_template, make_response, url_for, request, flash, redirect, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
from uuid import uuid4
import os
from .models import File, SharedFile, User
from . import db, visit_url, talisman

main = Blueprint('main', __name__)

'''
@main.after_app_request
def set_headers(resp):

    """
    resp.headers['Content-Security-Policy'] = "default-src 'none'; script-src 'self' 'unsafe-inline'; style-src https://stackpath.bootstrapcdn.com"
    resp.headers['X-Frame-Options'] = 'DENY'
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['X-XSS-Protection'] = '1; mode=block'
    """
    resp.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    return resp
'''


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
            return redirect(url_for('main.show_files'))

    return make_response(render_template('upload.html'))

@main.route('/upload/<uuid>')
@login_required
@talisman(content_security_policy={'script-src':"'self'"})
def download_file(uuid):
    file = File.query.filter(File.uuid == uuid).first()

    if not file:
        return redirect(url_for('main.error',msg='File not found'))
    
    if file.user_id != current_user.id:
        
        sf = SharedFile.query.filter(SharedFile.file_uuid == file.uuid, SharedFile.user_id == current_user.id).first()
        if not sf:
            return redirect(url_for('main.error',msg='Forbidden'))

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
        return redirect(url_for('main.error',msg='File not found'))    
    elif file.user_id != current_user.id:
        return redirect(url_for('main.error',msg='Forbidden'))
    
    if request.method == 'POST':
        
        email = request.form.get('email')

        if not email:
            return redirect(url_for('main.error',msg='Missing "email" value'))
        
        u = User.query.filter(User.email == email).first()
        
        if not u:
            return redirect(url_for('main.error',msg='User not found'))

        if u.id == current_user.id:
            return redirect(url_for('main.error',msg='wtf, no'))

        if file.filename == 'flag':
            return redirect(url_for('main.error',msg='No flag sharing plz'))

        try:
            sf = SharedFile(file_uuid=file.uuid, user_id=u.id)

            db.session.add(sf)
            db.session.commit()
        except IntegrityError:
            return redirect(url_for('main.error',msg='File already shared with this user'))

        return 'Done'

    return render_template('share.html')
    

@main.route('/abuse', methods=['GET','POST'])
@login_required
def report_abuse():
    if request.method == 'POST':
        url = request.form.get('url')

        if url and url.startswith('http'):
            if visit_url(url):
                return 'ok'
            else:
                return redirect(url_for('main.error'))
        else:
            flash('Invalid data','error')
            
    return render_template('abuse.html')


@main.route('/error')
def error():

    msg = request.args.get('msg')
    if not msg:
        msg = "Error"
    return render_template('error.html',msg=msg), 400
    
