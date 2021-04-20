import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/", methods=["GET", "POST"])
@app.route("/home")
def home():
    categories = mongo.db.categories.aggregate([
        {"$group": {"_id": "$category_group", }}])
    return render_template(
        "home.html", categories=categories)


@app.route("/search", methods=["GET", "POST"])
def search():
    # Enables search functionality on homepage search bar
    query = request.form.get("query")
    products = mongo.db.products.find({"$text": {"$search": query}})
    results = products.count()
    return render_template(
        "products.html", query=query, products=products, results=results)


@app.route("/all_categories")
def all_categories():
    # Renders all categories - for admin purposes
    categories = mongo.db.categories.find()
    return render_template(
        'categories.html', categories=categories)


@app.route("/get_categories/<category_group>")
def get_categories(category_group):
    # Gets categories in a particular category group from dropdown menu
    categories = mongo.db.categories.find({"category_group": "category_group"})
    if category_group == "Eyes & Brows":
        categories = mongo.db.categories.find(
            {"category_group": "Eyes & Brows"})
    elif category_group == "Face":
        categories = mongo.db.categories.find({"category_group": "Face"})
    elif category_group == "Lips":
        categories = mongo.db.categories.find({"category_group": "Lips"})
    elif category_group == "Tools & Accessories":
        categories = mongo.db.categories.find(
            {"category_group": "Tools & Accessories"})
    return render_template(
        "categories.html", category_group=category_group,
        categories=categories)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    # Adds a category to the db - access only for admin
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name"),
            "category_group": request.form.get("category_group"),
            "img_url": request.form.get("category_image")
        }
        mongo.db.categories.insert_one(category)
        flash("New Category Added")
        return redirect(url_for("all_categories"))

    category_group = mongo.db.categories.aggregate([
        {"$group": {"_id": "$category_group", }}])
    return render_template(
        "add_category.html", category_group=category_group)


@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name"),
            "category_group": request.form.get("category_group"),
            "img_url": request.form.get("category_image")
        }
        mongo.db.categories.update({"_id": ObjectId(category_id)}, submit)
        flash("Category successfully updated")
        return redirect(url_for("all_categories"))

    category_group = mongo.db.categories.aggregate([
        {"$group": {"_id": "$category_group", }}])
    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template(
        "edit_category.html", category=category, category_group=category_group)


@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    # Deletes a category from the db - access only for admin
    mongo.db.categories.remove({"_id": ObjectId(category_id)})
    flash("Category Successfully Deleted")
    categories = mongo.db.categories.find()
    return render_template('categories.html', categories=categories)


@app.route("/search_categories", methods=["GET", "POST"])
def search_categories():
    # Gets products in specific category
    product_query = request.form.get("product_query")
    products = list(mongo.db.products.find(
        {"$text": {"$search": product_query}}))

    return render_template("products.html", products=products)


@app.route("/all_products")
def all_products():
    # Renders all products in database
    products = mongo.db.products.find()
    return render_template(
        'products.html', products=products)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        # check if email already exists in database
        existing_email = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})
        if existing_email:
            flash("Email already registered")
            return redirect(url_for("register"))

        # Adds user registration details to the db
        register = {
            "username": request.form.get("username").lower(),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "favourites": []
        }
        mongo.db.users.insert_one(register)

        # put new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
               existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(
                    request.form.get("username").capitalize()))
                return redirect(url_for("profile", username=session["user"]))
            else:
                # invalid password entered by user
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=("GET", "POST"))
def profile(username):
    # grab the sessions username from the db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"].capitalize()

    if session['user']:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
