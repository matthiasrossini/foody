import pandas as pd
import os
import sys

import stripe

from flask import Flask, render_template, redirect, url_for, request, flash

from foody import app, db  # data
from foody.forms import TableForm, ProductUpload, AddAdmin, AdminLogin, MenuForm, AddWaiter, WaiterLogin, SubmitOrder

from foody.models import Products, Orders, get_products, get_orders, User, register_login, load_user, add_admin, check_admin, add_waiter, check_waiter, logout_client, upload_bytes_to_gcs

from flask_login import LoginManager, UserMixin, login_user, current_user
from flask_login import logout_user, login_required
from foody.__init__ import login_manager

from google.cloud import storage
# from foody.secrets import SQL_PASSWORD, PUBLIC_IP_ADDRESS, SQL_DATABASE_NAME

GC_BUCKET_NAME = "foody-bucket"

###############
# Main Routes #
###############


@app.route("/")
@app.route("/index")
@app.route("/home")
def home():
    products = get_products()
    return render_template('main/home.html', layout=home, products_df=products)

# this is the route Flask-login redirects you to automatically
# if there is a login_required and you are not logged in


@app.route("/login")
def login_route():
    return redirect(url_for("home"))


@app.route("/about")
def about():
    return render_template("main/about.html", title="About", layout="About")

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
    return render_template("addadmin.html", form=form, title="Add Admin")


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
    return render_template("users/adminlogin.html", form=form, title="Admin Login")


@app.route("/add-waiter", methods=["GET", "POST"])
@login_required
def add_waiter_route():
    if current_user.role == "admin":
        form = AddWaiter()
        if form.validate_on_submit():
            add_waiter(form)
            return redirect(url_for("admin_page"))
        return render_template("users/addwaiter.html", form=form, title="Add Waiters")

    else:
        flash(f"Unfortunately, a {current_user.role} cannot add new waiters.")
        return redirect(url_for("home"))


@app.route("/admin")
@login_required
def admin_page():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return render_template("users/adminpage.html", title="Admin")

    else:
        flash("You must be an admin to view this page.")
        return redirect(url_for("home"))


@app.route("/waiter-login", methods=["GET", "POST"])
def waiter_login():

    form = WaiterLogin()

    if form.validate_on_submit():
        if check_waiter(form):
            return redirect(url_for("waiter_page"))
    return render_template("users/waiterlogin.html", form=form, title="Waiter Login")


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
    return render_template("checkin.html", form=form, title="Check-In")


@app.route("/table/<table_number>", methods=["GET", "POST"])
def table(table_number):
    form = TableForm()
    table_number = table_number
    if form.validate_on_submit():
        register_login(form, table_number)
        return redirect(url_for("menu"))
    return render_template("table.html", form=form, table_number=table_number, title="Table")


@app.route("/menu", methods=["GET", "POST"])
@login_required
def menu():
    products = get_products()
    form = SubmitOrder()
    if current_user.role in ["client"]:
        # with engine.connect() as connection:
        #     available_food = connection.execute("select pname from products")
        available_starters = Products.query.filter_by(ptype="starter")
        available_main = Products.query.filter_by(ptype="main")
        available_dessert = Products.query.filter_by(ptype="dessert")
        starters_list = [(i.pname) for i in available_starters] + ["none"]
        main_list = [(i.pname) for i in available_main] + ["none"]
        dessert_list = [(i.pname) for i in available_dessert] + ["none"]
        form = SubmitOrder()
        form.Starters.choices = starters_list
        form.Main.choices = main_list
        form.Dessert.choices = dessert_list
        if form.validate_on_submit():
            starter = form.Starters.data
            main = form.Main.data
            dessert = form.Dessert.data
            if starter != "none":
                product = Products.query.filter_by(pname=starter).first()
                name = product.pname
                price = product.pprice
                Starter = Orders(food=name, price=price, user_table=current_user.table_number)
                db.session.add(Starter)
            if main != "none":
                product2 = Products.query.filter_by(pname=main).first()
                name2 = product2.pname
                price2 = product2.pprice
                Main = Orders(food=name2, price=price2, user_table=current_user.table_number)
                db.session.add(Main)
            if dessert != "none":
                product3 = Products.query.filter_by(pname=dessert).first()
                name3 = product3.pname
                price3 = product3.pprice
                Dessert = Orders(food=name3, price=price3, user_table=current_user.table_number)
                db.session.add(Dessert)
            # db.session.add_all([Starter, Main, Dessert])
            db.session.commit()
            flash("Your order was successfully submitted!")
            return redirect(url_for("meal"))
    return render_template("menu/menu.html", products_df=products, form=form, title="Menu")


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


@app.route("/stripe", methods=["GET", "POST"])
@login_required
def stripe():
    STRIPE_PUBLISHABLE_KEY = "pk_test_51HubNWKUsJQgM5cwhuLnrsSSOsiFfyFwhba9kEqnTJdQ9xB4zuPhqIM6Z6s1VeCWsCK1wkYNBDGXasFmBXyK7R4H00xIAt9ie3"
    STRIPE_SECRET_KEY = "sk_test_51HubNWKUsJQgM5cw3wivbgvNzM5EQRGj2gt5Y6mltt2mqSzeRmGi5pW4cW40nCibQUhSzjEc3WcJMYuwr52mE4gf00QER6iDbf"
    # Stripe.setPublishableKey()
    stripe.api_key = STRIPE_SECRET_KEY
    if current_user.role == "client":
        user_table = current_user.table_number
        orders = get_orders()
        # query = """
        # SELECT *
        # FROM User
        # LEFT JOIN Orders
        # ON User.table_number == Orders.user_table
        # """
        # orders1 = pd.read_sql(query, db.session.bind)
        # orders = orders1.dropna(axis=0, subset=["table_number"])
        order_nums = orders["user_table"].unique()
        # table_orders = {}
        total_price = 0
        for price in order_nums:
            products_for_table = orders.loc[orders["user_table"] == price, "price"]
            products_for_table = list(products_for_table)
            total_price = sum(products_for_table)
        return render_template("stripe.html", total_price=total_price, key=STRIPE_PUBLISHABLE_KEY, title="Payment")
    else:
        flash("Sorry, but this route is for clients only. To try it out yourself, +\
        try out the customer journey from /table/<insert_number_here>!")
        return redirect(url_for("home"))


@app.route('/charge', methods=["GET", "POST"])
def charge():
    return render_template("end.html")


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
            image_as_bytes = form.pimage.data.read()
            # path_in_static_folder = os.path.join("product_images", form.pname.data)
            file_name = form.pname.data
            # filepath = os.path.join("foody/static", path_in_static_folder)
            # f.save(filepath)
            public_img_url = upload_bytes_to_gcs(bucket_name=GC_BUCKET_NAME,
                                             bytes_data=image_as_bytes,
                                             destination_blob_name=file_name)
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
                img_public_url=public_img_url,
                pimage=file_name
            )

            db.session.add(product)
            db.session.commit()

            return redirect(url_for("menu"))

        return render_template("menu/upload.html", form=form, title="Upload")
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
        ON User.table_number == Orders.user_table
        """
        orders1 = pd.read_sql(query, db.session.bind)
        orders = orders1.dropna(axis=0, subset=["table_number"])
        orders = orders[orders.food != "none"]
        if orders.empty:
            flash ("There are currently no orders")
            return redirect("/"+current_user.role)
        else:
            table_orders=[]
            table_nums = orders["table_number"].unique().tolist()
            for table in table_nums:
                products_for_table = orders.loc[orders["table_number"] == table, "food"]
                products_for_table = products_for_table.values.tolist()
                table_orders += [table, products_for_table]
            order_and_table=[]
            i=0
            while i < (len(orders)-3):
                text=f"Table {table_orders[i]}'s orders are:"
                order_list = table_orders[i+1]
                order_string = ""
                for meal in order_list:
                    order_string += f"{meal}, "
                i+=2
                order_and_table += text + order_string
            return render_template("orders.html", order_and_table = order_and_table)
    else:
        flash("Sorry, but customers cannot access this page.")
        return redirect(url_for("menu"))
