import sqlite3
from settings import *
from datetime import datetime

db_name = 'database.db'
conn = None
cursor = None


def open():
    global conn, cursor
    conn = sqlite3.connect(PATH + db_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()


def close():
    cursor.close()
    conn.close()


def do(query, params=None):
    cursor.execute(query, params)
    conn.commit()


def getUser():
    open()
    cursor.execute('''SELECT * FROM user''')
    user = cursor.fetchone()
    close()

    return user


def getAuthData():
    open()
    cursor.execute('''SELECT * FROM users''')
    data = cursor.fetchone()
    close()

    return {'login': data[0], 'password': data[1]}

def createPost_in_db(data):
    open()
    do(''' INSERT INTO post (category_id, text, img_formainpage, title, datetime) VALUES (?, ?, ?, ?, ?)''', 
       [1, data['ckeditor'], data['image'], data['title'], datetime.now().replace(microsecond=0)])
    close()

def updatePost(data, row):
    open()
    do(''' UPDATE post SET text=(?), title=(?), img_formainpage=(?), datetime=(?) WHERE post_id = (?)''', 
       [data['ckeditor'], data['title'], data['image'], datetime.now().replace(microsecond=0), row])
    close()

def deletePost(post_id):
    open()
    cursor.execute(
        '''DELETE FROM post WHERE post_id=(?)''', 
        [post_id])
    conn.commit()
    close()


def updateUser(data):
    open()
    do(''' UPDATE user SET login=(?), name=(?), description=(?), password=(?), image=(?)''', 
       [data['login'], data['name'], data['description'], data['password'], data['image']])
    close()

def change_password(passw):
    open()
    do('''UPDATE user SET password=(?)''', [passw])
    close()

def addPost(category_id, post):
    open()
    cursor.execute('''INSERT INTO post (category_id,text) VALUES((?),(?))''', [
                   category_id, post])
    conn.commit()
    close()

def delPost(post_id):
    open()
    cursor.execute(
        '''DELETE FROM post WHERE post_id=(?)''', 
        [post_id])
    conn.commit()
    close()

def get_three_last_posts():
    open()
    cursor.execute('''
    SELECT * FROM post ORDER BY post_id DESC LIMIT 3    
    ''')
    result = cursor.fetchall()
    close()
    return result

def getPostsByIds(post_id):
    open()
    cursor.execute('''
    SELECT * FROM post WHERE post_id = (?) ORDER BY post_id DESC 
    ''', [post_id])
    posts = cursor.fetchall()
    close()
    return posts

def getQnAs():
    open()
    cursor.execute('''SELECT * FROM QnA''')
    qnas = cursor.fetchall()
    close()
    return qnas

def getAllPosts():
    open()
    cursor.execute('''SELECT * FROM post ORDER BY post_id DESC''')
    results = cursor.fetchall()
    close()
    return results

def generateAdminHash():
    from werkzeug.security import generate_password_hash
    user = getUser()
    change_password(generate_password_hash(user['password']))