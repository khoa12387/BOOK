from app.models import Category, Product, UserRoleEnum
from app import app, db ,dao
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask_login import logout_user, current_user
from flask import redirect, request


admin = Admin(app=app, name='Quản trị bán hàng', template_mode='bootstrap4')


class AuthenticatedAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.ADMIN


class AuthenticatedUser(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class MyProductView(AuthenticatedAdmin):
    column_list = ['id', 'name', 'price','quantity','active']
    column_searchable_list = ['name']
    column_filters = ['name', 'price']
    column_editable_list = ['name', 'price']
    create_modal = True
    edit_modal = True
    can_create = False



class MyCategoryView(AuthenticatedAdmin):
    column_list = ['id', 'name', 'products']
    column_searchable_list = ['name']
    column_filters = ['name' ]
    column_editable_list = ['name']
    create_modal = True
    edit_modal = True



class StatsView(AuthenticatedUser):
    @expose("/")
    def index(self):
        kw = request.args.get("kw")
        return self.render('admin/reports.html',
                           stats=dao.Report_frequency(kw),
                           month_stats=dao.revenue_month(2024))


class LogoutView(AuthenticatedUser):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/admin')

class MyAdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html', stats=dao.count_products_by_cate())

class Book(AuthenticatedUser):
    @expose("/")
    def index(self):
        return self.render('admin/book.html')

class Rule(AuthenticatedUser):
    @expose("/")
    def index(self):
        return self.render('admin/rule.html')

class HomePage(AuthenticatedUser):
    @expose("/")
    def index(self):
        return redirect('/')

admin.add_view(Book(name='Nhập sách'))
admin.add_view(Rule(name='Quy định'))
admin.add_view(MyCategoryView(Category, db.session))
admin.add_view(MyProductView(Product, db.session))
admin.add_view(StatsView(name='Thông kê báo cáo'))
admin.add_view(HomePage(name="Trang chủ"))
admin.add_view(LogoutView(name='Đăng xuất'))

