from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from app import db, app
from flask_login import UserMixin
from datetime import datetime
import enum


class UserRoleEnum(enum.Enum):
    USER = 1
    ADMIN = 2


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100))
    user_role = Column(Enum(UserRoleEnum), default=UserRoleEnum.USER)
    receipts = relationship('Receipt', backref='user', lazy=True)

    def __str__(self):
        self.name


class Category(db.Model):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=True)
    products = relationship('Product', backref='category', lazy=True)

    def __str__(self):
        return self.name


class Product(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=True)
    price = Column(Float, default=0)
    image = Column(String(100))
    active = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)
    receipt_details = relationship('ReceiptDetails', backref='product', lazy=True)

    def __str__(self):
        return self.name


class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=datetime.now())
    active = Column(Boolean, default=True)


class Receipt(BaseModel):
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    receipt_details = relationship('ReceiptDetails', backref='receipt', lazy=True)


class ReceiptDetails(BaseModel):
    quantity = Column(Integer, default=0)
    price = Column(Float, default=0)
    receipt_id = Column(Integer, ForeignKey(Receipt.id), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        import hashlib
        u = User(name='Admin', username='admin',
                 password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()), user_role=UserRoleEnum.ADMIN)
        db.session.add(u)
        db.session.commit()

        c1 = Category(name='Ngôn Tình')
        c2 = Category(name='Kinh Dị ')
        c3 = Category(name='Truyện Ngắn')
        c4 = Category(name='Trinh Thám')
        c5 = Category(name='Light Novel')

        db.session.add(c1)
        db.session.add(c2)
        db.session.add(c3)
        db.session.add(c4)
        db.session.add(c5)
        db.session.commit()

        p1 = Product(name='Tết Ở Làng Địa Ngục', price=130000, category_id=2, image="https://res.cloudinary.com/driiz3taz/image/upload/v1703773932/Te_oqyap4.jpg")
        p2 = Product(name='Sĩ Số Lớp Vắng 0', price=200000, category_id=2, image="https://res.cloudinary.com/driiz3taz/image/upload/v1703773932/SiSoVang0_mvc1af.jpg")
        p3 = Product(name='Đồ Vật Có Linh Hồn', price=230000, category_id=2, image="https://res.cloudinary.com/driiz3taz/image/upload/v1703773931/nhung-do-vat-co-linh-hon-1_2_edgxb6.jpg")
        p4 = Product(name='Thất Tịch Không Mưa ', price=110000, category_id=1, image="https://res.cloudinary.com/driiz3taz/image/upload/v1703773929/ThatTichKhongMua_xwlu1u.jpg")
        p5 = Product(name='Nụ Hôn Của Sói ', price=140000, category_id=1, image="https://res.cloudinary.com/driiz3taz/image/upload/v1703773931/nu-hon-cua-soi-2d_5408664d93b64dd4bd0ec392ff2ee9cb_master_1_jg0vvy.jpg")
        p6 = Product(name='Mãi Mãi Là Bao Xa', price= 150000, category_id=1, image="https://res.cloudinary.com/driiz3taz/image/upload/v1703773930/MaiMaiLaBaoXa_rxzzh3.jpg" )
        p7 = Product(name='Cậu Là Bạn Nhỏ ', price=250000, category_id=3, image="https://res.cloudinary.com/driiz3taz/image/upload/v1703773931/ViCauLaBanNhoCuaTo_k2k2ey.jpg")
        p8 = Product(name='Đám Trẻ Ở Đại Dương', price=230000, category_id=3, image="https://res.cloudinary.com/driiz3taz/image/upload/v1703773929/DamNhoODaiSuongDen_pqnfh9.jpg")
        p9 = Product(name='Tật Xấu Người Việt', price=310000, category_id=3, image="https://res.cloudinary.com/driiz3taz/image/upload/v1703773928/TatXauNguoiViet_xm7nua.jpg")
        p10 = Product(name='Bi Kịch Ba Hồ', price=20000, category_id=4, image="https://res.cloudinary.com/driiz3taz/image/upload/v1703773928/BiKichBaHoi_v9eik3.jpg")
        p11 = Product(name='Thú Tội', price=35000, category_id=4, image="https://res.cloudinary.com/driiz3taz/image/upload/v1703773927/ThuToi_cprtle.jpg")
        p12 = Product(name='Nguồn Cội', price=31000, category_id=4, image="https://res.cloudinary.com/driiz3taz/image/upload/v1703773928/NguonCoi_g5fn3s.jpg")
        p13 = Product(name='Chúa Tể Bóng Tối', price=203000, category_id=5, image="https://res.cloudinary.com/driiz3taz/image/upload/v1703773930/ChuaTeBongToi_jmwntx.jpg")
        p14 = Product(name='OVERLORD', price=255000, category_id=5, image="https://res.cloudinary.com/driiz3taz/image/upload/v1703773928/overlord_8_-_bia_1_1_dum8lb.jpg")
        p15 = Product(name='Thánh Hiệp Sĩ ', price=190000, category_id=5, image="https://res.cloudinary.com/driiz3taz/image/upload/v1703773942/ThanhHiepSi_zx24kw.png")
        db.session.add_all([p1, p2, p3, p4, p5, p6, p7,p8,p9,p10,p11,p12,p13,p14,15])
        db.session.commit()