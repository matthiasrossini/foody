from models import Products, Table, Orders, get_products, get_orders, User, register_login, load_user, add_admin, check_admin, add_waiter, check_waiter, logout_client

my_order = Orders.query.first()
