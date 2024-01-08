from datetime import datetime, timedelta

from sqlalchemy import func, extract, desc
from sqlalchemy.orm import joinedload

from app.models import Category, Product, User, Receipt, ReceiptDetails, UserRoleEnum, Comment, Rule
from app import app, db
import hashlib
from flask_login import current_user


def get_categories():
    return Category.query.all()


def get_products(kw, cate_id, page=None):
    products = Product.query

    if kw:
        products = products.filter(Product.name.contains(kw))

    if cate_id:
        products = products.filter(Product.category_id.__eq__(cate_id))

    if page:
        page = int(page)
        page_size = app.config['PAGE_SIZE']
        start = (page - 1) * page_size

        return products.slice(start, start + page_size)

    return products.all()


def count_product():
    return Product.query.count()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def auth_user(username, password, user_role):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username),
                             User.password.__eq__(password),
                             User.user_role.__eq__(user_role)).first()


def add_receipt(cart):
    if cart:
        r = Receipt(user=current_user)
        db.session.add(r)

        for c in cart.values():
            d = ReceiptDetails(quantity=c['quantity'], price=c['price'], receipt=r, product_id=c['id'])
            db.session.add(d)

        try:
            db.session.commit()
        except:
            return False
        else:
            return True

    return False


def add_user(name, username, password, avatar, quantity, email, sdt):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    u = User(name=name, username=username, password=password, avatar=avatar, quantity=quantity, email=email, sdt=sdt)
    db.session.add(u)
    db.session.commit()


def Report_frequency(kw=None):
    # Tính ngày đầu tiên và cuối cùng của tháng hiện tại
    today = datetime.today()
    first_day_of_month = today.replace(day=1)
    last_day_of_month = (today.replace(month=today.month % 12 + 1, day=1) - timedelta(days=1)).replace(hour=23,
                                                                                                       minute=59,
                                                                                                       second=59)

    # Query thông tin mã sản phẩm, tên sản phẩm, doanh thu, tần suất và tỷ lệ của sản phẩm trong tháng
    query = db.session.query(
        Product.id,
        Product.name,
        func.sum(ReceiptDetails.price * ReceiptDetails.quantity).label('revenue'),
        func.sum(ReceiptDetails.quantity).label('total_quantity'),
        func.count(Receipt.id).label('frequency'),
        func.round(func.count(Receipt.id) / (
                func.extract('day', func.timestamp(last_day_of_month)) - func.extract('day', func.timestamp(
            first_day_of_month))) + 1, 2).label('rate'),
    ).join(ReceiptDetails, ReceiptDetails.product_id == Product.id) \
        .join(Receipt, ReceiptDetails.receipt_id == Receipt.id) \
        .filter(Receipt.created_date >= first_day_of_month, Receipt.created_date <= last_day_of_month) \
        .group_by(Product.id)


    if kw:
        query = query.filter(Product.name.contains(kw)).all()

    query = query.order_by(desc(func.sum(ReceiptDetails.quantity)))
    result = query.all()

    return result

def revenue_month(year=2024):
    result = db.session.query(
        Category.id.label('Mã Thể Loại'),
        Category.name.label('Tên Thể Loại'),
        func.extract('month', Receipt.created_date).label('Tháng'),
        func.sum(ReceiptDetails.price * ReceiptDetails.quantity).label('Doanh Thu'),
        func.sum(ReceiptDetails.quantity).label('total_quantity'),
        func.round(
            (func.count(Receipt.id) /
            func.extract('day', func.last_day(func.max(Receipt.created_date))) + 1),2).label('Tỷ Lệ Bán'),
      ).join(Receipt, ReceiptDetails.receipt_id == Receipt.id)\
     .join(Product, ReceiptDetails.product_id == Product.id)\
     .join(Category, Category.id == Product.category_id)\
     .filter(func.extract('year', Receipt.created_date) == year)\
     .group_by(Category.id, Category.name, func.extract('month', Receipt.created_date))
    query= result.all()

    return query


def get_comments_by_prod_id(id):
    return Comment.query.filter(Comment.product_id.__eq__(id)).all()


def add_comment(product_id, content):
    c = Comment(user=current_user, product_id=product_id, content=content)
    db.session.add(c)
    db.session.commit()

    return c


def get_product_by_id(id):
    return Product.query.get(id)


def count_products_by_cate():
    return db.session.query(Category.id, Category.name, func.count(Product.id)) \
        .join(Product, Product.category_id == Category.id, isouter=True).group_by(Category.id).all()


def add_product(name, price, image, active, category_id, quantity):
    p = Product(name=name, image=image, active=active, category_id=category_id, quantity=quantity)
    db.session.add(p)
    db.session.commit()


def edit_rule(minQuantity, minQuantityInStorage):
    r = Rule.query.first()
    r.minQuantity = minQuantity
    r.minQuantityInStorage = minQuantityInStorage
    db.session.commit()


