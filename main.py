from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self,username, password):
        self.username = username
        self.password = password

def get_blog_posts():
    return Blog.query.all()

def get_users():
    return User.query.all()

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup','list_blogs', 'index', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    return render_template('index.html', page_title="Blog Users", users=get_users())

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user in get_users():
            if user.password == password:
                session['username'] = username
                flash("Logged in")
                return redirect('/newpost')
            else:
                flash('User password incorrect', 'error')
                return redirect('/login')
        else:
            flash('User does not exist', 'error')
            return redirect('/login')

    return render_template('login.html', page_title="Login")

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if (username.strip() == ""):
            flash("Please enter a valid username", "error")
            return redirect('/signup')
        else:
            if len(username) < 3:
                flash("Username must contain at least 3 characters. Please enter a valid username", 
                "error")
                return redirect('/signup')

        if (password.strip() == ""):
            flash("Please enter a valid password", "error")
            return redirect('/signup')
        else:
            if len(password) < 3:
                flash("Password must contain at least 3 characters. Please enter a valid password", 
                "error")
                return redirect('/signup')

        if password == verify:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                flash('This username is already taken', 'error')
                return redirect ('/signup')
        else:
            flash('Passwords do not match', 'error')

    return render_template('signup.html', page_title="Signup")

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'GET':
        return render_template('newpost.html',page_title="New Blog Post")

    else:
        if request.method == 'POST':
            blog_title = request.form['title']
            blog_body = request.form['body']
            owner = User.query.filter_by(username=session['username']).first()

            title_error = ''
            body_error = ''

            if len(blog_title) < 1:
                title_error = 'Please fill in the title'
            
            if len(blog_body) < 1:
                body_error = 'Please fill in the body'

            if not title_error and not body_error:
                newpost = Blog(blog_title, blog_body, owner)
                db.session.add(newpost)
                db.session.commit()
                id = str(newpost.id)
                return redirect('/blog?id='+ id)
            else:
                return render_template('newpost.html',page_title="New Blog Post",
                blog_title=blog_title, blog_body=blog_body,
                title_error=title_error, body_error=body_error)


@app.route('/blog', methods=['GET'])
def list_blogs():
    id = request.args.get('id')
    user = request.args.get('user')

    if id == None:
        if user == None:
            return render_template('blog.html', page_title="Welcome to Blogz", 
            blogs=get_blog_posts(), users=get_users())  
        else:
            user = int(user)
            return render_template('display_user_blogs.html', page_title="User Blog Posts", 
            users=get_users(), user=user, blogs=get_blog_posts())    
    else:
        id = int(id)
        return render_template('display_blog.html', page_title="Display Individual Post", 
        blogs=get_blog_posts(), id=id, users=get_users())


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')
    
if __name__ == '__main__':
    app.run()
