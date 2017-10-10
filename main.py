from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body

def get_blog_posts():
    return Blog.query.all()

@app.route('/newpost', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('newpost.html',page_title="New Blog Post")

    else:
        if request.method == 'POST':
            blog_title = request.form['title']
            blog_body = request.form['body']

            title_error = ''
            body_error = ''

            if len(blog_title) < 1:
                title_error = 'Please fill in the title'
            
            if len(blog_body) < 1:
                body_error = 'Please fill in the body'

            if not title_error and not body_error:
                newpost = Blog(blog_title, blog_body)
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

    if id == None:
        return render_template('blog.html', page_title="Blogs", blogs=get_blog_posts())       
    else:
        id = int(id)
        return render_template('display_blog.html', blogs=get_blog_posts(), id=id)
    
if __name__ == '__main__':
    app.run()
