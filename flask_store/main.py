from functools import wraps
from datetime import date

from flask import Flask
from flask import render_template, request, redirect, url_for, jsonify
import json

from post import Post
from user import User

app = Flask(__name__)

global logged_username #stores the name of the user who is logged in
logged_username = ""

@app.route('/')
def hello_world():
    return redirect('/main')

@app.route('/main')
def route_main():
    return render_template('main.html', username = logged_username)


def require_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.cookies.get('token')
        if not token or not User.verify_token(token):
            return redirect('/login')
        return func(*args, **kwargs)
    return wrapper

@app.route('/posts')
def list_posts():
    return render_template('posts.html', posts=Post.all())


@app.route('/posts/<int:id>')
def show_post(id):
    post = Post.find(id)

    return render_template('post.html', post=post)


@app.route('/posts/<int:id>/edit', methods=['GET', 'POST'])
def edit_post(id):
    post = Post.find(id)
    if request.method == 'GET':
        return render_template(
            'edit_post.html',
            post=post
        )
    elif request.method == 'POST':
        post.name = request.form['name']
        post.author = request.form['author']
        post.content = request.form['content']
        post.price = request.form['price']
        post.save()
        return redirect(url_for('show_post', id=post.id))

@app.route('/posts/new', methods=['GET', 'POST'])
@require_login
def new_post():
    if request.method == 'GET':
        return render_template('new_post.html')
    elif request.method == 'POST':
        values = (
            None,
            request.form['name'],
            request.form['author'],
            request.form['content'],
            request.form['price'],
            date.today(),
            1,
            ""      
        )
        Post(*values).create()

        return redirect('/')


@app.route('/posts/<int:id>/delete', methods=['POST'])
def delete_post(id):
    post = Post.find(id)
    post.delete()

    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        values = (
            None,
            request.form['username'],
            User.hash_password(request.form['password']),
            request.form['email'],
            request.form['address'],
            request.form['phone']
        )
        User(*values).create()
        global logged_username
        logged_username = request.form['username']
        return redirect('/')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        data = json.loads(request.data.decode('ascii'))
        username = data['username']
        password = data['password']
        global logged_username
        logged_username = username
        user = User.find_by_username(username)
        if not user or not user.verify_password(password):
            return jsonify({'token': None})
        token = user.generate_token()
        return jsonify({'token': token.decode('ascii')})

@app.route('/users')
def list_users():
    return render_template('users.html', users=User.all())

@app.route('/users/<int:id>')
def show_user(id):
    user = User.find(id)

    return render_template('user.html', user=user)    

@app.route('/users/<int:id>/delete', methods=['POST'])
def delete_user(id):
    user = User.find(id)
    user.delete() 

    return redirect('/')

@app.route('/users/<int:id>/edit', methods=['GET', 'POST'])
def edit_user(id):
    user = User.find(id)
    if request.method == 'GET':
        return render_template(
            'edit_user.html',
            user=user
        )
    elif request.method == 'POST':
        user.username = request.form['username']
        user.address = request.form['address']
        user.phone = request.form['phone']
        user.save()
        return redirect(url_for('show_user', id=user.id)) 

@app.route('/posts/<int:id>/buy', methods=['POST'])
def buy_post(id):
    post = Post.find(id)
    post.buyer = logged_username
    post.active = 0
    post.save()

        return redirect(url_for('show_post', id=post.id))                     

if __name__ == '__main__':
    app.run(debug=True)
