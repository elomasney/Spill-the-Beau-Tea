import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from datetime import datetime
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
    products = list(mongo.db.products.find({"$text": {"$search": query}}))
    results = len(products)
    if results == 0:
        flash("No Results found, please try again")
        return redirect(url_for("all_products"))
    ratings = mongo.db.reviews.aggregate([
        {"$group": {
            "_id": "$product",
            "ratings": {"$sum": 1},
            "average": {"$avg": "$rating"}
        }
        }])
    return render_template(
        "products.html", query=query, products=products,
        results=results, ratings=ratings)


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
    # Edits a category from the database
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


@app.route("/all_products")
def all_products():
    # Renders all products in database
    products = mongo.db.products.find().sort("brand", 1)
    review = list(mongo.db.reviews.find())
    ratings = mongo.db.reviews.aggregate([
        {"$group": {
            "_id": ("$product"),
            "ratings": {"$sum": "$rating"},
            "average": {"$avg": "$rating"}
        }
        }])
    rating_count = ratings["ratings"]
    return render_template(
        'products.html', products=products, ratings=ratings, review=review,
        rating_count=rating_count)


@app.route("/product_info/<product_id>")
def product_info(product_id):
    # Renders one product with details and reviews
    product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
    reviews = list(mongo.db.reviews.find({
        "product": ObjectId(product_id)}).sort("created_on", 1).limit(5))
    review_count = len(reviews)
    message = ""
    if review_count == 0:
        message += "Be the first to write a Review!"
    else:
        message += "Reviews"
    ratings = mongo.db.reviews.aggregate([
        {"$group": {
            "_id": "$product",
            "ratings": {"$sum": "$rating"},
            "average": {"$avg": "$rating"}
        }
        }])

    return render_template(
        'product_info.html', product=product, reviews=reviews,
        ratings=ratings, review_count=review_count, message=message)


@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    # Adds a product to the db - access only for admin
    if request.method == "POST":
        product = {
            "product_name": request.form.get("product_name"),
            "brand": request.form.get("brand"),
            "category_name": request.form.get("category_name"),
            "img_url": request.form.get("product_image"),
            "description": request.form.get("description"),
            "price": request.form.get("product_price"),
            "num_shades": request.form.get("shades"),
            "buy_url": request.form.get("buy_url"),
        }
        mongo.db.products.insert_one(product)
        flash("New Product Added")

        return redirect(url_for("all_products"))

    categories = mongo.db.categories.find()
    return render_template(
        "add_product.html", categories=categories)


@app.route("/edit_product/<product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    # Edits product from the database
    if request.method == "POST":
        submit = {
            "product_name": request.form.get("product_name"),
            "brand": request.form.get("brand"),
            "category_name": request.form.get("category_name"),
            "img_url": request.form.get("product_image"),
            "description": request.form.get("description"),
            "price": request.form.get("product_price"),
            "num_shades": request.form.get("shades"),
            "buy_url": request.form.get("buy_url"),
        }
        mongo.db.products.update({"_id": ObjectId(product_id)}, submit)
        flash("Product successfully updated")
        return redirect(url_for("all_products"))

    categories = mongo.db.categories.find()
    product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
    return render_template(
        "edit_product.html", product=product, categories=categories)


@app.route("/delete_product/<product_id>")
def delete_product(product_id):
    # Deletes a review from the db - Admin & Registered user access
    mongo.db.products.remove({"_id": ObjectId(product_id)})
    flash("Product Successfully Deleted")
    product = mongo.db.products.find()
    return render_template("products.html", product=product)


@app.route("/reviews")
def reviews():
    # Gets all reviews from the db
    # Sorts by product id
    reviews = mongo.db.reviews.find().sort("product", 1)
    return render_template("reviews.html", reviews=reviews)


@app.route("/add_review/<product_id>", methods=["GET", "POST"])
def add_review(product_id):
    # Adds a review to the db
    repurchase = "on" if request.form.get("repurchase") else "off"
    now = datetime.now()
    if request.method == "POST":
        review = {
            "product": ObjectId(product_id),
            "age": request.form.get("age"),
            "rating": int(request.form.get("rating")),
            "title": request.form.get("title"),
            "review": request.form.get("review_content"),
            "repurchase": repurchase,
            "created_by": session["user"],
            "created_on": now.strftime("%d/%m/%Y"),
        }
        mongo.db.reviews.insert_one(review)
        flash("New Review Added")
        return redirect(url_for("product_info", product_id=product_id))

    product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
    return render_template(
        "product-info.html", review=review, product=product,
        now=now, product_id=product_id)


@app.route("/edit_review/<review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    # Edits a review by a user on the db
    reviews = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
    product_id = reviews["product"]
    repurchase = "on" if request.form.get("repurchase") else "off"
    now = datetime.now()
    if request.method == "POST":
        review = {
            "product": ObjectId(product_id),
            "age": request.form.get("age"),
            "rating": int(request.form.get("rating")),
            "title": request.form.get("title"),
            "review": request.form.get("review_content"),
            "repurchase": repurchase,
            "created_by": session["user"],
            "created_on": now.strftime("%d/%m/%Y"),
        }
        mongo.db.reviews.update({"_id": ObjectId(review_id)}, review)
        flash("Review Updated")
        return redirect(url_for("all_products"))
    products = mongo.db.products.find()
    return render_template(
        "products.html", review=review, reviews=reviews,
        product_id=product_id, now=now, products=products)


@app.route("/delete_review/<review_id>")
def delete_review(review_id):
    # Removes review from the db - Admin & Registered user access
    mongo.db.reviews.remove({"_id": ObjectId(review_id)})
    flash("Review Successfully Deleted")
    review = mongo.db.reviews.find()
    return render_template("products.html", review=review)


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
    products = mongo.db.products.find()
    favourites = mongo.db.users.find_one(
        {"username": session["user"].lower()})["favourites"]
    if session['user']:
        return render_template(
            "profile.html", username=username, products=products,
            favourites=favourites)

    return redirect(url_for("login"))


@app.route("/favourites/<product_id>)", methods=["GET", "POST"])
def favourites(product_id):
    if session["user"]:
        product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
        products = mongo.db.products.find()
        mongo.db.users.update({"username": session["user"]}, {
            "$push": {
                "favourites": {"_id": ObjectId(product_id)},
            }
            })
        flash("Product added to favourites")
        return redirect(url_for("profile", username=session["user"]))
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"].capitalize()
    return render_template(
        "profile.html", username=username, product=product, products=products)


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
