import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, abort, Response
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
import qrcode
from io import BytesIO
from base64 import b64encode
import random
import string
from functools import wraps
import dotenv

dotenv.load_dotenv()

app = Flask(__name__, 
    # static_url_path='/static',
    static_folder='static',
    template_folder='templates'
)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_SECRET_KEY'] = os.getenv('SECRET_KEY')
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

def check_auth(password):
    return password == ADMIN_PASSWORD

def authenticate():
    return Response(
        'Требуется авторизация\n', 401,
        {'WWW-Authenticate': 'Basic realm="Admin Area"'}
    )

def requires_admin_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# --- MODELS ---
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    questions = db.relationship('Question', backref='quiz', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(256))
    correct_option = db.Column(db.Integer, nullable=False)
    options = db.relationship('Option', backref='question', lazy=True)

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    text = db.Column(db.String(256), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), unique=False, nullable=False)
    quiz_session_id = db.Column(db.Integer, db.ForeignKey('quiz_session.id'), nullable=False)
    score = db.Column(db.Integer, default=0)

class UserAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    selected_option = db.Column(db.Integer, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)

class QuizSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    session_code = db.Column(db.String(12), unique=True, nullable=False)
    users = db.relationship('User', backref='quiz_session', lazy=True)
    score = db.Column(db.Integer, default=0)

# --- ADMIN ROUTES ---
@app.route('/admin', methods=['GET'])
@app.route('/admin/', methods=['GET'])
@requires_admin_auth
def admin_index():
    sessions = QuizSession.query.order_by(QuizSession.id.desc()).all()
    return render_template('admin/index.html', sessions=sessions)

@app.route('/admin/quiz/<int:quiz_id>/qrcode')
def admin_quiz_qrcode(quiz_id):
    url = url_for('client_quiz', quiz_id=quiz_id, _external=True)
    img = qrcode.make(url)
    buf = BytesIO()
    img.save(buf, format='PNG')
    img_b64 = b64encode(buf.getvalue()).decode('utf-8')
    return render_template('admin/qrcode.html', quiz_id=quiz_id, img_b64=img_b64, url=url)

@app.route('/admin/quiz/<int:quiz_id>/rating')
def admin_quiz_rating(quiz_id):
    sessions = QuizSession.query.filter_by(quiz_id=quiz_id).order_by(QuizSession.score.desc()).all()
    return render_template('admin/rating.html', sessions=sessions)

@app.route('/admin/quiz/<int:quiz_id>/rating/json')
def admin_quiz_rating_json(quiz_id):
    sessions = QuizSession.query.filter_by(quiz_id=quiz_id).order_by(QuizSession.score.desc()).all()
    data = [
        {"nickname": s.user.nickname, "score": s.score}
        for s in sessions
    ]
    return {"data": data} if False else data

@app.route('/admin/session/new', methods=['POST'])
@requires_admin_auth
def admin_create_session():
    quiz = Quiz.query.first()
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    sess = QuizSession(quiz_id=quiz.id, session_code=code)
    db.session.add(sess)
    db.session.commit()
    return redirect(url_for('admin_index'))

@app.route('/admin/sessions')
def admin_sessions():
    sessions = QuizSession.query.order_by(QuizSession.id.desc()).all()
    return render_template('admin/sessions.html', sessions=sessions)

@app.route('/admin/session/<session_code>')
@requires_admin_auth
def admin_session(session_code):
    sess = QuizSession.query.filter_by(session_code=session_code).first_or_404()
    url = url_for('client_quiz', session_code=session_code, _external=True)
    return render_template('admin/session.html', session=sess, url=url)

@app.route('/admin/session/<session_code>/qrcode')
@requires_admin_auth
def admin_session_qrcode(session_code):
    url = url_for('client_quiz', session_code=session_code, _external=True)
    img = qrcode.make(url)
    buf = BytesIO()
    img.save(buf, format='PNG')
    img_b64 = b64encode(buf.getvalue()).decode('utf-8')
    return render_template('admin/qrcode.html', img_b64=img_b64, url=url)

@app.route('/admin/session/<session_code>/rating')
@requires_admin_auth
def admin_session_rating(session_code):
    sess = QuizSession.query.filter_by(session_code=session_code).first_or_404()
    users = User.query.filter_by(quiz_session_id=sess.id).order_by(User.score.desc()).all()
    return render_template('admin/rating.html', users=users, session_code=session_code)

@app.route('/admin/session/<session_code>/rating/json')
@requires_admin_auth
def admin_session_rating_json(session_code):
    sess = QuizSession.query.filter_by(session_code=session_code).first_or_404()
    users = User.query.filter_by(quiz_session_id=sess.id).order_by(User.score.desc()).all()
    data = [{"nickname": u.nickname, "score": u.score} for u in users]
    return data

@app.route('/admin/session/<session_code>/delete', methods=['POST'])
@requires_admin_auth
def admin_session_delete(session_code):
    sess = QuizSession.query.filter_by(session_code=session_code).first_or_404()
    for user in sess.users:
        UserAnswer.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
    db.session.delete(sess)
    db.session.commit()
    return redirect(url_for('admin_index'))

# --- CLIENT ROUTES ---
@app.route('/')
def index():
    return render_template('client/index.html')

@app.route('/quiz/<session_code>', methods=['GET', 'POST'])
def client_quiz(session_code):
    sess = QuizSession.query.filter_by(session_code=session_code).first_or_404()
    quiz = db.session.get(Quiz, sess.quiz_id)
    if request.method == 'POST':
        nickname = request.form['nickname']
        user = User(nickname=nickname, quiz_session_id=sess.id, score=0)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        session['session_code'] = session_code
        return redirect(url_for('client_quiz_questions', session_code=session_code, qn=1))
    return render_template('client/enter_nick.html', quiz=quiz)

@app.route('/quiz/<session_code>/q/<int:qn>', methods=['GET', 'POST'])
def client_quiz_questions(session_code, qn):
    sess = QuizSession.query.filter_by(session_code=session_code).first_or_404()
    quiz = db.session.get(Quiz, sess.quiz_id)
    questions = quiz.questions
    if qn > len(questions):
        user_id = session.get('user_id')
        user = db.session.get(User, user_id)
        answers = UserAnswer.query.filter_by(user_id=user_id).all()
        score = sum(1 for a in answers if a.is_correct)
        user.score = score
        db.session.commit()
        return redirect(url_for('client_quiz_result', session_code=session_code, user_id=user_id))
    question = questions[qn-1]
    options = question.options
    if request.method == 'POST':
        selected = int(request.form['option'])
        user_id = session.get('user_id')
        user = db.session.get(User, user_id)
        is_correct = (selected == question.correct_option)
        ans = UserAnswer(user_id=user_id, question_id=question.id, selected_option=selected, is_correct=is_correct)
        db.session.add(ans)
        if is_correct:
            user.score += 1
        db.session.commit()
        return redirect(url_for('client_quiz_questions', session_code=session_code, qn=qn+1))
    return render_template('client/question.html', quiz=quiz, question=question, options=options, qn=qn, total=len(questions), session_code=session_code)

@app.route('/quiz/<session_code>/result/<int:user_id>')
def client_quiz_result(session_code, user_id):
    user = db.session.get(User, user_id)
    if not user:
        abort(404)
    return render_template('client/result.html', session=user)

@app.route('/quiz/<session_code>/rating/json')
def client_quiz_rating_json(session_code):
    sess = QuizSession.query.filter_by(session_code=session_code).first_or_404()
    users = User.query.filter_by(quiz_session_id=sess.id).order_by(User.score.desc()).all()
    data = [{"nickname": u.nickname, "score": u.score} for u in users]
    return data

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False) 