import pandas as pd
import os
import sys
from flask import Flask, render_template, redirect, url_for, request, flash

from foody import app, db  # data
from foody.forms import TableForm, ProductUpload, AddAdmin, AdminLogin, MenuForm, AddWaiter, WaiterLogin, StarterOrder, MainOrder, DessertOrder
from foody.models import Products, Orders, get_products, get_orders, User, register_login, load_user, add_admin, check_admin, add_waiter, check_waiter, logout_client

from flask_login import LoginManager, UserMixin, login_user, current_user
from flask_login import logout_user, login_required
from foody.__init__ import login_manager

from sqlalchemy import create_engine

engine = create_engine("sqlite:///site.db")

###############
# Main Routes #
###############


@app.route("/")
@app.route("/index")
@app.route("/home")
def home():
    return render_template('main/home.html', layout=home)

# this is the route Flask-login redirects you to automatically
# if there is a login_required and you are not logged in


@app.route("/login")
def login_route():
    return redirect(url_for("home"))


@app.route("/about")
def about():
    return render_template("main/about.html", title="About", layout=About)

# to delete afterwards


@app.route("/add-admin-here-make-restricted", methods=["GET", "POST"])
def add_admin_route():
    """
    ADD THIS IN LATER FOR SECURITY
    if current_user.access_level = 3:
    """
    form = AddAdmin()
    if form.validate_on_submit():
        if add_admin(form):
            return redirect(url_for("admin_login"))
    return render_template("addadmin.html", form=form)
################
# Login Routes #
################


# Flask-login redirects you automatically here if login_required and you are not logged in
@app.route("/login")
def login():
    return redirect(url_for("home"))


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    form = AdminLogin()
    if form.validate_on_submit():
        if check_admin(form):
            return redirect(url_for("admin_page"))
    return render_template("users/adminlogin.html", form=form)


@app.route("/add-waiter", methods=["GET", "POST"])
@login_required
def add_waiter_route():
    if current_user.role == "admin":
        form = AddWaiter()
        if form.validate_on_submit():
            add_waiter(form)
            return redirect(url_for("admin_page"))
        return render_template("users/addwaiter.html", form=form)

    else:
        flash(f"Unfortunately, a {current_user.role} cannot add new waiters.")
        return redirect(url_for("home"))


@app.route("/admin")
@login_required
def admin_page():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return render_template("users/adminpage.html")
    else:
        flash("You must be an admin to view this page.")
        return redirect(url_for("home"))


@app.route("/waiter-login", methods=["GET", "POST"])
def waiter_login():

    form = WaiterLogin()

    if form.validate_on_submit():
        if check_waiter(form):
            return redirect(url_for("waiter_page"))
    return render_template("users/waiterlogin.html", form=form)


@app.route("/waiter")
@login_required
def waiter_page():
    if current_user.role in ["admin", "waiter"]:
        return render_template("users/waiterpage.html")
    else:
        flash("You must at least be a waiter to access this page.")
        return redirect(url_for("home"))


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


###################
# Customer Routes #
###################


@app.route("/checkin", methods=["GET", "POST"])
def checkin():
    form = TableForm()
    if form.validate_on_submit():
        table_number = form.table_number.data
        register_login(form, table_number)
        return redirect(url_for("menu"))
    return render_template("checkin.html", form=form)


@app.route("/table/<table_number>", methods=["GET", "POST"])
def table(table_number):
    form = TableForm()
    table_number = table_number
    if form.validate_on_submit():
        register_login(form, table_number)
        return redirect(url_for("menu"))
    return render_template("table.html", form=form, table_number=table_number)


@app.route("/menu", methods=["GET", "POST"])
@login_required
def menu():
    if current_user.role in ["client"]:
        products = get_products()
        # with engine.connect() as connection:
        #     available_food = connection.execute("select pname from products")
        available_starters = Products.query.filter_by(ptype="starter")
        available_main = Products.query.filter_by(ptype="main")
        available_dessert = Products.query.filter_by(ptype="dessert")
        starters_list = [(i.pname) for i in available_starters]
        main_list = [(i.pname) for i in available_main]
        dessert_list = [(i.pname) for i in available_dessert]
        form = StarterOrder()
        form.Starters.choices = starters_list
        if form.validate_on_submit():
            starter = form.Starters.data
            starter = Products.query.filter_by(pname=starter).first()
            starter_name = starter.pname
            starter_price = starter.pprice
            Starter_Order = Orders(food=starter_name, price=starter_price,
                                   user_id=current_user.table_number)
            db.session.add(Starter_Order)
            db.session.commit()
        form = MainOrder()
        form.Main.choices = main_list
        if form.validate_on_submit():
            main = form.Main.data
            main = Products.query.filter_by(pname=main).first()
            main_name = main.pname
            main_price = main.pprice
            Main_Order = Orders(food=main_name, price=main_price, user_id=current_user.table_number)
            db.session.add(Main_Order)
            db.session.commit()
        form = DessertOrder()
        form.Dessert.choices = dessert_list
        if form.validate_on_submit():
            dessert = form.Dessert.data
            dessert = Products.query.filter_by(pname=dessert).first()
            dessert_name = dessert.pname
            dessert_price = dessert.pprice
            Dessert_Order = Orders(food=dessert_name, price=dessert_price,
                                   user_id=current_user.table_number)
            db.session.add(Dessert_Order)
            db.session.commit()

            flash("Your order was successfully submitted!")
            return redirect(url_for("meal"))
    return render_template("menu/menu.html", products_df=products, form=form)


@app.route("/meal")
@login_required
def meal():
    if current_user.role == "client":
        orders = get_orders()
        return render_template("meal.html", orders_df=orders)
    else:
        flash("Sorry, but this route is for clients only. To try it out yourself, +\
        try out the customer journey from /table/<insert_number_here>!")
        return redirect(url_for("home"))


@app.route("/stripe")
@login_required
def stripe():
    if current_user.role == "client":
        user_id = current_user.table_number
        orders = get_orders()
        # query = """
        # SELECT *
        # FROM User
        # LEFT JOIN Orders
        # ON User.table_number == Orders.user_id
        # """
        # orders1 = pd.read_sql(query, db.session.bind)
        # orders = orders1.dropna(axis=0, subset=["table_number"])
        order_nums = orders["user_id"].unique()
        # table_orders = {}
        for price in order_nums:
            products_for_table = orders.loc[orders["user_id"] == price, "price"]
            products_for_table = list(products_for_table)
            total_price = sum(products_for_table)
        return render_template("stripe.html")
    else:
        flash("Sorry, but this route is for clients only. To try it out yourself, +\
        try out the customer journey from /table/<insert_number_here>!")
        return redirect(url_for("home"))


@app.route("/end")
@login_required
def end():
    logout_client()
    return render_template("end.html")


###########################
# Waiter and Admin Routes #
###########################


@app.route("/overview", methods=["GET", "POST"])
@login_required
def overview():
    if current_user.role in ["admin", "waiter"]:
        client_df = pd.read_sql(User.query.filter_by(role="client").statement, db.session.bind)
        return render_template("overview.html", df=client_df)
    else:
        flash(f"Sorry, but a {current_user.role} cannot access this page.")
        return redirect(url_for("home"))


@app.route("/upload-product", methods=["GET", "POST"])
@login_required
def upload():
    if current_user.role in ["admin", "waiter"]:
        form = ProductUpload()
        if form.validate_on_submit():

            # Saving Image
            f = form.pimage.data
            path_in_static_folder = os.path.join("product_images", form.pname.data)
            filepath = os.path.join("foody/static", path_in_static_folder)
            f.save(filepath)

            # SQL
            product = Products(
                pname=form.pname.data,
                pdescription=form.pdescription.data,
                pprice=form.pprice.data,
                ptype=form.ptype.data,
                pvegan=form.pvegan.data,
                pvegetarian=form.pvegetarian.data,
                pgluten_free=form.pgluten_free.data,
                plactose_free=form.plactose_free.data,
                pimage=path_in_static_folder
            )

            db.session.add(product)
            db.session.commit()

            return redirect(url_for("menu"))

        return render_template("menu/upload.html", form=form)
    else:
        flash(f"Sorry, but a {current_user.role} cannot add new products.")
        return redirect(url_for("menu"))


@app.route("/orders")
@login_required
def orders():
    if current_user.role in ["admin", "waiter"]:
        orders = get_orders()
        query = """
        SELECT *
        FROM User
        LEFT JOIN Orders
        ON User.table_number == Orders.user_id
        """
        orders1 = pd.read_sql(query, db.session.bind)
        orders = orders1.dropna(axis=0, subset=["table_number"])
        table_nums = orders["table_number"].unique()
        table_orders = {}
        for table in table_nums:
            products_for_table = orders.loc[orders["table_number"] == table, "food"]
            products_for_table = list(products_for_table)
            table_orders[table] = ", ".join(products_for_table)
        return render_template("orders.html", orders=table_orders)
    else:
        flash("Sorry, but customers cannot access this page.")
        return redirect(url_for("menu"))


@app.route("/product/<product_name>")
def single_product(product_name):
    # we access the row of the dataframe that we want
    product_info = data.loc[data["name"] == product_name, :]
    # we transform the single row into a dictionary (this is easier to access in the html)
    # code from: https://stackoverflow.com/questions/50575802/convert-dataframe-row-to-dict
    product_info = product_info.to_dict('records')[0]
    return render_template("menu/single_item.html", product_info=product_info)
