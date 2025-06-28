from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os, json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'super-secret-key'

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PRODUCTS_FILE = 'products.json'

def load_products():
    if os.path.exists(PRODUCTS_FILE) and os.path.getsize(PRODUCTS_FILE) > 0:
        with open(PRODUCTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_products(products):
    with open(PRODUCTS_FILE, 'w') as f:
        json.dump(products, f, indent=2)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(image_path)
            relative_path = '/' + image_path.replace('\\', '/')
            products = load_products()
            products.append({'title': title, 'image': relative_path})
            save_products(products)
            return redirect(url_for('dashboard'))

    return render_template('dashboard.html', products=load_products())

@app.route('/delete/<int:index>', methods=['POST'])
def delete_product(index):
    if not session.get('admin'):
        return redirect(url_for('login'))

    products = load_products()
    if 0 <= index < len(products):
        # حذف الصورة من المجلد (اختياري)
        image_path = products[index]['image'].replace('/static/', 'static/')
        if os.path.exists(image_path):
            os.remove(image_path)
        del products[index]
        save_products(products)

    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '123456':
            session['admin'] = True
            return redirect(url_for('dashboard'))
        else:
            return '🔐 Invalid credentials'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/api/products')
def api_products():
    return jsonify(load_products())

if __name__ == '__main__':
    app.run(debug=True)
