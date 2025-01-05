from flask import Flask, request, render_template, redirect, url_for
import os
from models import db, Product
from werkzeug.utils import secure_filename
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:senghour789@localhost:5432/crud_product2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db.init_app(app)
migrate = Migrate(app, db)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'svg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def dashboard():
    products = Product.query.all()
    return render_template('dashboard.html', products=products)


@app.route('/product/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        qty = int(request.form['qty'])
        file = request.files['img']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img_path = f'static/uploads/{filename}'
        else:
            img_path = None

        product = Product(name=name, description=description, price=price, qty=qty, img=img_path)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('form.html', action=' Add')


@app.route('/product/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        product.qty = int(request.form['qty'])
        file = request.files['img']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product.img = f'static/uploads/{filename}'

        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('form.html', product=product, action='Edit')


@app.route('/product/delete/<int:id>', methods=['POST'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        os.remove(product.img)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
