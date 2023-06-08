from flask import Flask, redirect, url_for, session, request, render_template
from flask_ckeditor import CKEditor
from db_scripts import *
from settings import *

app = Flask(__name__)
ckeditor = CKEditor(app)

@app.route('/')
@app.route('/home')
def index():    
    posts = get_three_last_posts()
    qnas = getQnAs()
    user = getUser()
    return render_template("home.html", user=user, posts=posts, qnas=qnas)

@app.route('/posts/')
def posts():
    posts = getAllPosts()
    user = getUser()
    return render_template('posts.html', posts=posts, user=user)

@app.route('/posts/<post_id>')
def post(post_id):
    post = getPostsByIds(post_id)[0]
    return render_template('post.html', post=post)

@app.route('/authorization_to_admin_account_super_duper_secret', methods=['GET', 'POST'])
def auth():
    errors = []
    user = getUser()
    if request.method == 'POST':
        if request.form['login'] == "":
            errors.append("Поле Логін не може бути порожнім!")

        if user['login'] != request.form['login']:
            errors.append("Такого логіну не існує!")
        
        if request.form['password'] == "":
            errors.append("Поле Пароль не може бути порожнім!")
        else:
            if user['password'] != request.form['password']:
                errors.append("Пароль невірний!")
    
        if not errors:
            session["AUTH"] = True
            return redirect(url_for('admin_panel'))

    return render_template('auth.html', errors=errors)

@app.route('/admin_panel_super_duper_secret_page/', methods=['GET', 'POST'])
@app.route('/admin_panel_super_duper_secret_page/user_edit/', methods=['GET', 'POST'])
def admin_panel():
    if not "AUTH" in session:
        return render_template("403.html"), 403
    errors = []
    user1 = getUser()
    if request.method == 'POST':

        user = request.form.copy()

        if request.form['name'] == '':
            errors.append("Поле Ім\'я не може бути порожнім!")
        if request.form['login'] == '':
            errors.append("Поле Логін не може бути порожнім!")
        if request.form['description'] == '':
            errors.append("Поле Опис не може бути порожнім!")

        if request.form['password'] != '':
            if request.form['password'] != request.form['password_confirm']:
                errors.append("Пароль та підтвердження паролю не співпадають!")
            elif len(request.form['password']) < 8:
                errors.append("Пароль містить менше 8 символів")
            else:
                user['password'] = request.form['password']

        if len(errors) == 0 and request.files['image'].filename != '':
            image = request.files['image']
            image.save(f"{PATH_STATIC}{image.filename}")
            user['image'] = image.filename

        if request.files['image'].filename == '':
            user['image'] = user1['image']
        
        if len(errors) == 0:
            updateUser(user)
            return redirect(url_for('admin_panel'))
        
    return render_template('userEdit.html', user=user1, errors=errors)

@app.route('/admin_panel_super_duper_secret_page/post_edit/', methods=['GET', 'POST'])
def post_edit():
    if not "AUTH" in session:
        return render_template("403.html"), 403
    posts = getAllPosts()
    if request.method == 'POST':
        try:
            selected_index = int(request.form["posts_list"])
            return redirect(url_for('postEdit', post_id=selected_index))
        except:
            return redirect(url_for('createPost'))
    return render_template('selectPost.html', posts=posts)

@app.route('/admin_panel_super_duper_secret_page/post_edit/<post_id>', methods=['GET', 'POST'])
def postEdit(post_id):
    if not "AUTH" in session:
        return render_template("403.html"), 403
    post1 = getPostsByIds(post_id)[0]
    post_text = post1['text']
    errors = []
    if request.method == 'POST':

        post = request.form.copy()

        if request.form['title'] == '':
            errors.append('Поле заголовок не може бути пустим!')
        if request.form.get('ckeditor') == '':
            errors.append('Поле текст не може бути пустим!')
        if request.files['image'].filename == '':
            errors.append('В пості обов\'язково повиинне бути головне зображення!')

        if len(errors) == 0 and request.files['image'].filename != '':
            image = request.files['image']
            image.save(f"{PATH_STATIC}{image.filename}")
            post['image'] = image.filename
        
        if len(errors) == 0:
            updatePost(post, post_id)
            return redirect(url_for('admin_panel'))
    return render_template('postEdit.html', post=post1, post_text=post_text, errors=errors, post_id=post_id)

@app.route('/admin_panel_super_duper_secret_page/create_post', methods=['GET', 'POST'])
def createPost():
    if not "AUTH" in session:
        return render_template("403.html"), 403
    errors = []
    if request.method == 'POST':

        post = request.form.copy()

        if request.form['title'] == '':
            errors.append('Поле заголовок не може бути пустим!')
        if request.form.get('ckeditor') == '':
            errors.append('Поле текст не може бути пустим!')
        if request.files['image'].filename == '':
            errors.append('В пості обов\'язково повиинне бути головне зображення!')

        if len(errors) == 0 and request.files['image'].filename != '':
            image = request.files['image']
            image.save(f"{PATH_STATIC}{image.filename}")
            post['image'] = image.filename
        
        if len(errors) == 0:
            createPost_in_db(post)
            return redirect(url_for('admin_panel'))
    return render_template('createPost.html', errors=errors)

@app.route('/admin_panel_super_duper_secret_page/delete_post/<post_id>', methods=['POST'])
def delete_post(post_id):
    if not "AUTH" in session:
        return render_template("403.html"), 403
    deletePost(post_id)
    return redirect(url_for('post_edit'))

@app.route('/admin_panel_super_duper_secret_page/qna_edit/', methods=['GET', 'POST'])
def qna_edit():
    if not "AUTH" in session:
        return render_template("403.html"), 403
    questions = getAllQuestions()
    if request.method == 'POST':
        try:
            selected_index = int(request.form["question_list"])
            return redirect(url_for('questionEdit', question_id=selected_index))
        except:
            return redirect(url_for('createQuestion'))
    return render_template('selectQuestion.html', questions=questions)

@app.route('/admin_panel_super_duper_secret_page/createQuestion/', methods=['GET', 'POST'])
def createQuestion():
    if not "AUTH" in session:
        return render_template("403.html"), 403
    errors = []
    if request.method == 'POST':

        qna = request.form.copy()

        if request.form['title'] == '':
            errors.append('Поле заголовок не може бути пустим!')
        if request.form.get('ckeditor') == '':
            errors.append('Поле текст не може бути пустим!')
        
        if len(errors) == 0:
            addQnA(qna)
            return redirect(url_for('admin_panel'))
    return render_template('createQuestion.html', errors=errors)

@app.route('/admin_panel_super_duper_secret_page/qna_edit/<question_id>', methods=['GET', 'POST'])
def questionEdit(question_id):
    if not "AUTH" in session:
        return render_template("403.html"), 403
    og_qnas = getQuestionByID(question_id)[0]
    qna_answer = og_qnas['answer']
    errors = []
    if request.method == 'POST':

        qnas = request.form.copy()

        if request.form['title'] == '':
            errors.append('Поле заголовок не може бути пустим!')
        if request.form.get('ckeditor') == '':
            errors.append('Поле текст не може бути пустим!')

        if len(errors) == 0:
            UpdateQNA(qnas, question_id)
            return redirect(url_for('admin_panel'))
    return render_template('questionEdit.html', qna=og_qnas, qna_text=qna_answer, errors=errors, question_id=question_id)

@app.route('/admin_panel_super_duper_secret_page/delete_question/<qna_id>', methods=['POST'])
def deleteQuestion(qna_id):
    if not "AUTH" in session:
        return render_template("403.html"), 403
    deleteQnA(qna_id)
    return redirect(url_for('qna_edit'))

app.config["SECRET_KEY"] = "MTEwIDEwMCAxMTYgMTA5IDExMiAzMiA5NyA5OSAxMTYgMTEzIDEyMiAzMiA5NyAxMjI="
app.config['CKEDITOR_FILE_UPLOADER'] = 'upload'

if __name__ == "__main__":
    app.run(debug=True, port=5000)