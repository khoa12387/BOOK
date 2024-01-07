import math
from functools import wraps

from flask import render_template, request, redirect, jsonify, session, url_for
import dao
import utils
from app import app, login, db
from flask_login import login_user, logout_user, login_required, user_logged_out, user_login_confirmed, current_user, \
    fresh_login_required
from app.models import UserRoleEnum, User


def user_login_confirmed(func): # Định nghĩa hàm user_login_confirmed
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect('/')
        else:
            return func(*args, **kwargs)
    return wrapper

def user_logged_out(func): # Định nghĩa hàm user_logged_out
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login_view'))
        else:
            return func(*args, **kwargs)
    return wrapper






@app.route('/products/<id>')
def details(id):
    comments = dao.get_comments_by_prod_id(id)
    return render_template('details.html', product=dao.get_product_by_id(id), comments=comments)


@app.route("/api/products/<id>/comments", methods=['post'])
@login_required
def add_comment(id):
    content = request.json.get('content')

    try:
        c = dao.add_comment(product_id=id, content=content)
    except:
        return jsonify({'status': 500, 'err_msg': 'Hệ thống đang có lỗi!'})
    else:

        return jsonify({'status': 200, "c": {'content': c.content, "user": {"avatar": c.user.avatar}}})

@app.route("/")
def index():
    kw = request.args.get('kw')
    cate_id = request.args.get('cate_id')
    page = request.args.get('page')

    prods = dao.get_products(kw, cate_id, page)

    num = dao.count_product()
    page_size = app.config['PAGE_SIZE']

    return render_template('index.html',
                           products=prods, pages=math.ceil(num/page_size))


@app.route('/admin/login', methods=['post'])
def login_admin():
    username = request.form.get('username')
    password = request.form.get('password')
    user_role = UserRoleEnum.ADMIN

    user = dao.auth_user(username=username, password=password, user_role=user_role)
    if user and user.user_role == UserRoleEnum.ADMIN:
        login_user(user)

    return redirect('/admin')


@app.route('/LogOut')
@user_logged_out
def LogOut():
    logout_user()
    return redirect(url_for('login_view'))


@app.route('/register', methods=['get', 'post'])
def register():
    err_msg = None
    if request.method.__eq__('POST'):
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        if password.__eq__(confirm):
            try:
                dao.add_user(name=request.form.get('name'),
                             username= request.form.get('username'),
                             password=password,avatar= None)
            except Exception as ex:
                print(str(ex))
                err_msg = "Hiện tại web site đang gặp sự cố !!!"
            else :
                return redirect('/login')

        else:
            err_msg = "Mật Khẩu không khớp"
    return render_template('/register.html', err_msg=err_msg)


@app.route('/admin/nhapsach', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        image = request.form['image']
        active = 'active' in request.form  # Kiểm tra xem checkbox được chọn hay không
        category_id = int(request.form['category_id'])
        quantity = int(request.form['quantity'])
        email= request.form['email']
        sdt = int(request.form['sdt'])


        dao.add_product(name,price,image,active,category_id,quantity,email,sdt)

        return redirect('/admin/book') # Chuyển hướng sau khi thêm sản phẩm thành công

    return render_template('book.html')

@app.route('/admin/quidinh', methods=['GET', 'POST'])
def edit_rule():
    if request.method == 'POST':
        minQuantity = request.form['minQuantity']
        minQuantityInStorage = request.form['minQuantityInStorage']

        dao.edit_rule(minQuantity, minQuantityInStorage)

        return redirect('/admin/rule')

    return render_template('rule.html')


@app.route("/cart")
def cart():
    return render_template('cart.html')


@app.route("/api/cart", methods=['post'])
def add_to_cart():
    data = request.json

    cart = session.get('cart')
    if cart is None:
        cart = {}

    id = str(data.get("id"))
    if id in cart:
        cart[id]['quantity'] += 1
    else:
        cart[id] = {
            "id": id,
            "name": data.get("name"),
            "price": data.get("price"),
            "quantity": 1
        }

    session['cart'] = cart

    """
        {
            "1": {
                "id": "1",
                "name": "...",
                "price": 123,
                "quantity": 2
            },  "2": {
                "id": "2",
                "name": "...",
                "price": 1234,
                "quantity": 1
            }
        }
    """

    return jsonify(utils.count_cart(cart))


@app.route("/api/cart/<product_id>", methods=['put'])
def update_cart(product_id):
    cart = session.get('cart')
    if cart and product_id in cart:
        quantity = request.json.get('quantity')
        cart[product_id]['quantity'] = int(quantity)

    session['cart'] = cart
    return jsonify(utils.count_cart(cart))


@app.route("/api/cart/<product_id>", methods=['delete'])
def delete_cart(product_id):
    cart = session.get('cart')
    if cart and product_id in cart:
        del cart[product_id]

    session['cart'] = cart
    return jsonify(utils.count_cart(cart))


@app.route("/api/pay", methods=['post'])
def pay():
    cart = session.get('cart')
    if dao.add_receipt(cart):
        del session['cart']
        return jsonify({'status': 200})

    return jsonify({'status': 500, 'err_msg': 'Something wrong!'})


@app.route('/login', methods=['get', 'post'])
@user_login_confirmed
def login_view():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user_role = UserRoleEnum.USER

        user = dao.auth_user(username=username, password=password, user_role=user_role)
        if user and user_role == UserRoleEnum.USER:
            login_user(user)

        next = request.args.get('next')
        if next:
            return redirect(next)

        return redirect("/")

    return render_template('login.html')



@app.context_processor
def common_responses():
    return {
        'categories': dao.get_categories(),
        'cart_stats': utils.count_cart(session.get('cart'))
    }


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


if __name__ == '__main__':
    from app import admin
    app.run(debug=True)
