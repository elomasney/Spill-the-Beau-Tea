import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for, abort)
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
    """
    Gets category groups for dropdown menu
    from the db and renders the homepage
    """
    categories = mongo.db.categories.aggregate([
        {"$group": {"_id": "$category_group", }}])
    return render_template(
        "home.html", categories=categories)


@app.route("/search", methods=["GET", "POST"])
def search():
    """
    Enables search functionality on homepage search bar
    Gets input value from search bar
    """
    query = request.form.get("query")
    # List of products based on the value of the query
    products = list(mongo.db.products.find({"$text": {"$search": query}}))
    # Number of results returned from query search
    results = len(products)
    # If no results are found
    if results == 0:
        flash("No Results found, please try again")
        return redirect(
            url_for("all_products", _external=True, _scheme='https'))
    # Gets ratings from reviews and calculates the average rating
    ratings = list(mongo.db.reviews.aggregate([
        {"$group": {
            "_id": "$product",
            "ratings": {"$sum": 1},
            "average": {"$avg": "$rating"}
        }}]))
    has_rating = []
    # Gets list of product ids in ratings
    for rating in ratings:
        has_rating.append(rating["_id"])
    # Check if a user is in session to check if products are in user favourites
    if "user" in session:
        user = mongo.db.users.find_one({"username": session["user"]})
        favourites = []
        user_favourites = list(mongo.db.products.find(
            {"_id": {"$in": user["favourites"]}}))
        for favourite in user_favourites:
            favourites.append(favourite["_id"])
        return render_template(
            "products.html", query=query, products=products,
            favourites=favourites, results=results,
            ratings=ratings, has_rating=has_rating)
    return render_template(
        "products.html", query=query, products=products,
        results=results, ratings=ratings, has_rating=has_rating)


@app.route("/all_categories")
def all_categories():
    """ Gets all categories from the db"""
    categories = mongo.db.categories.find().sort("category_group", 1)
    return render_template(
        'categories.html', categories=categories)


@app.route("/get_categories/<category_group>")
def get_categories(category_group):
    """ Gets categories in a particular category group from dropdown menu """
    categories = list(mongo.db.categories.find(
        {"category_group": category_group}))
    # If category doesn't exist render 404 page
    if len(categories) == 0:
        abort(404)
    return render_template(
        "categories.html", category_group=category_group,
        categories=categories)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    """ Adds a category to the db - access only for admin """
    # Checks if user is in session
    if "user" in session:
        # Checks if user is admin
        if session["user"] == "admin".lower():
            if request.method == "POST":
                category = {
                    "category_name": request.form.get("category_name"),
                    "category_group": request.form.get("category_group"),
                    "img_url": request.form.get("category_image")
                }
                mongo.db.categories.insert_one(category)
                flash("New Category Added")
                return redirect(
                    url_for("all_categories", _external=True, _scheme='https'))
            # Groups all categories by category_group
            category_group = mongo.db.categories.aggregate([
                {"$group": {"_id": "$category_group", }}])
            return render_template(
                "add_category.html", category_group=category_group)
        # if user is not admin redirect to homepage
        else:
            flash('You are not authorised to add a category')
            return redirect(url_for('home'))
    # if user not in session display 404 page
    else:
        abort(404)


@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    """ Allows Admin to edit a category from the database """
    # Checks if user is in session
    if "user" in session:
        # Checks if user is admin
        if session["user"] == "admin".lower():
            # Gets all categories by category id
            category = mongo.db.categories.find_one_or_404(
                {"_id": ObjectId(category_id)})
            if request.method == "POST":
                submit = {
                    "category_name": request.form.get("category_name"),
                    "category_group": request.form.get("category_group"),
                    "img_url": request.form.get("category_image")
                }
                mongo.db.categories.update(
                    {"_id": ObjectId(category_id)}, submit)
                flash("Category successfully updated")
                return redirect(
                    url_for("all_categories", _external=True, _scheme='https'))
            # Groups all categories by category group
            category_group = mongo.db.categories.aggregate([
                {"$group": {"_id": "$category_group", }}])
            return render_template(
                "edit_category.html", category=category,
                category_group=category_group)
        # if user is not admin redirect to homepage
        else:
            flash('You are not authorised to edit a category')
            return redirect(url_for('home'))
    # if user not in session display 404 page
    else:
        abort(404)


@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    # Checks if user is in session
    if "user" in session:
        # Checks if user is admin
        if session["user"] == "admin".lower():
            """ Deletes a category from the db - access only for admin """
            mongo.db.categories.remove({"_id": ObjectId(category_id)})
            flash("Category Successfully Deleted")
            # Gets all categories from the db and sorts by category_group
            categories = mongo.db.categories.find().sort("category_group", 1)
            return render_template('categories.html', categories=categories)
        # if user is not admin redirect to homepage
        else:
            flash('You are not authorised to delete a category')
            return redirect(url_for('home'))
    # if user not in session display 404 page
    else:
        abort(404)


@app.route("/all_products")
def all_products():
    """ Renders all products in database """
    products = mongo.db.products.find().sort("brand", 1)
    # Gets ratings from reviews and calculates the average rating
    ratings = list(mongo.db.reviews.aggregate([
        {"$group": {
            "_id": "$product",
            "ratings": {"$sum": 1},
            "average": {"$avg": "$rating"}
        }}]))
    has_rating = []
    # Gets list of product ids in ratings
    for rating in ratings:
        has_rating.append(rating["_id"])
    # Check if a user is in session to check if products are in user favourites
    if "user" in session:
        user = mongo.db.users.find_one({"username": session["user"]})
        favourites = []
        user_favourites = list(mongo.db.products.find(
            {"_id": {"$in": user["favourites"]}}))
        for favourite in user_favourites:
            favourites.append(favourite["_id"])
        return render_template(
            'products.html', products=list(products), ratings=ratings,
            has_rating=has_rating, favourites=favourites)
    return render_template(
            'products.html', products=list(products), ratings=ratings,
            has_rating=has_rating)


@app.route("/product_info/<product_id>")
def product_info(product_id):
    """ Renders one product with details and reviews """
    product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
    # Gets a list of the most recent 5 product reviews
    reviews = list(mongo.db.reviews.find({
        "product": ObjectId(product_id)}).sort("created_on", -1).limit(5))
    # Count the number of reviews for the product
    review_count = len(reviews)
    message = ""
    # Displays message if there are zero reviews for the product
    if review_count == 0:
        message += "Be the first to write a Review!"
    # Displays the header Reviews if there are reviews
    else:
        message += "Reviews"
    # Groups reviews by product id - gets average ratings from reviews
    ratings = mongo.db.reviews.aggregate([
        {"$group": {
            "_id": "$product",
            "average": {"$avg": "$rating"}
        }
        }])
    # Checks if user is in session to find if a product is in user favs
    if "user" in session:
        user = mongo.db.users.find_one({"username": session["user"]})
        favourites = []
        user_favourites = list(mongo.db.products.find(
            {"_id": {"$in": user["favourites"]}}))
        # Gets the product ids for items in user favs
        for favourite in user_favourites:
            favourites.append(favourite["_id"])
        return render_template(
            'product_info.html', product=product, reviews=reviews,
            ratings=list(ratings), review_count=review_count,
            message=message, favourites=favourites)
    return render_template(
            'product_info.html', product=product, reviews=reviews,
            ratings=list(ratings), review_count=review_count,
            message=message)


@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    """ Adds a product to the db - access only for admin """
    # Checks if user is in session
    if "user" in session:
        # Checks if user is admin
        if session["user"] == "admin".lower():
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

                return redirect(
                    url_for("all_products", _external=True, _scheme='https'))
            # Gets all categories from the db
            categories = mongo.db.categories.find()
            return render_template(
                "add_product.html", categories=categories)
        # if user is not admin redirect to homepage
        else:
            flash('You are not authorised to add a product')
            return redirect(url_for('home'))
    # if user not in session display 404 page
    else:
        abort(404)


@app.route("/edit_product/<product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    """ Allows Admin to edit a product from the database """
    # Checks if user is in session
    if "user" in session:
        # Checks if user is admin
        if session["user"] == "admin".lower():
            # Gets one product from the db
            product = mongo.db.products.find_one_or_404(
                {"_id": ObjectId(product_id)})

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
                return redirect(
                    url_for("all_products", _external=True, _scheme='https'))
            # Gets all categories from the db
            categories = mongo.db.categories.find()
            return render_template(
                "edit_product.html", product=product, categories=categories)
        # if user is not admin redirect to homepage
        else:
            flash('You are not authorised to edit a product')
            return redirect(url_for('home'))
    # if user not in session display 404 page
    else:
        abort(404)


@app.route("/delete_product/<product_id>")
def delete_product(product_id):
    """
    Deletes a review from the db - Admin & Registered user access
    """
    # Checks if user is in session
    if "user" in session:
        # Checks if user is admin
        if session["user"] == "admin".lower():
            mongo.db.products.remove({"_id": ObjectId(product_id)})
            flash("Product Successfully Deleted")
            return redirect(
                url_for("all_products", _external=True,
                        _scheme='https'))
        # if user is not admin redirect to homepage
        else:
            flash('You are not authorised to delete a product')
            return redirect(url_for('home'))
    # if user not in session display 404 page
    else:
        abort(404)


@app.route("/reviews")
def manage_reviews():
    """
    Gets all reviews from the db.
    Sorts by product id
    """
    # Checks if user is in session
    if "user" in session:
        # Checks if user is admin
        if session["user"] == "admin".lower():
            product = list(mongo.db.products.find())
            reviews = list(mongo.db.reviews.find().sort("product", 1))
            # Gets users from db to display certain items depending on user
            user = mongo.db.users.find_one({"username": session["user"]})
            return render_template(
                "reviews.html", reviews=reviews, product=product, user=user)


@app.route("/reviews/<product_id>")
def reviews(product_id):
    """ Gets all reviews for a specific product from the db """

    product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
    # Finds corresponding reviews for each product
    reviews = list(mongo.db.reviews.find({
        "product": ObjectId(product_id)}).sort("created_on", 1))
    return render_template(
        "reviews.html", reviews=reviews, product=product)


@app.route("/add_review/<product_id>", methods=["GET", "POST"])
def add_review(product_id):
    """ Allows a user to add a review to the db """
    # Checks if user in session
    if "user" in session:
        repurchase = "on" if request.form.get("repurchase") else "off"
        now = datetime.now()
        if request.method == "POST":
            review = {
                "product": ObjectId(product_id),
                "rating": int(request.form.get("rating")),
                "title": request.form.get("title"),
                "review": request.form.get("review_content"),
                "repurchase": repurchase,
                "created_by": session["user"],
                "created_on": now.strftime("%d/%m/%Y"),
            }
            mongo.db.reviews.insert_one(review)
            flash("New Review Added")
            return redirect(
                url_for("product_info", product_id=product_id,
                        _external=True, _scheme='https'))
        # Gets one product from the db
        product = mongo.db.products.find_one_or_404(
            {"_id": ObjectId(product_id)})
        return render_template(
            "product-info.html", review=review, product=product,
            now=now, product_id=product_id)
    # If user not in session redirect to login page
    else:
        flash('You need to log in to add a review.')
        return redirect(url_for('login'))


@app.route("/edit_review/<review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    """ Allows a user to edit a review on the db """
    # Checks if user in session
    if "user" in session:
        review = mongo.db.reviews.find_one_or_404(
            {"_id": ObjectId(review_id)})
        product_id = review["product"]
        repurchase = "on" if request.form.get("repurchase") else "off"
        now = datetime.now()
        if request.method == "POST":
            review_edit = {
                "product": ObjectId(product_id),
                "rating": int(request.form.get("rating")),
                "title": request.form.get("title"),
                "review": request.form.get("review_content"),
                "repurchase": repurchase,
                "created_by": session["user"],
                "created_on": now.strftime("%d/%m/%Y"),
            }
            mongo.db.reviews.update({"_id": ObjectId(review_id)}, review_edit)
            flash("Review Updated")
            return redirect(
                url_for("profile", username=session["user"], _external=True,
                        _scheme='https'))
        reviews = mongo.db.reviews.find()
        return render_template(
            "profile.html", review_edit=review_edit, review=review,
            product_id=product_id, now=now, reviews=reviews)
    # If user not in session redirect to login page
    else:
        flash('You need to log in to edit a review.')
        return redirect(url_for('login'))


@app.route("/delete_review/<review_id>")
def delete_review(review_id):
    """ Removes review from the db - Admin & Registered user access """
    # Checks if user in session
    if "user" in session:
        mongo.db.reviews.remove({"_id": ObjectId(review_id)})
        flash("Review Successfully Deleted")
        username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]
        return redirect(
            url_for("profile", username=username,
                    _external=True, _scheme='https'))
    # If user not in session redirect to login page
    else:
        flash('You need to log in to delete a review.')
        return redirect(url_for('login'))


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Allows a user to register for a user account.
    Adds user to the database
    """
    if request.method == "POST":
        # check if username already exists in database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        if existing_user:
            flash("Username already exists")
            return redirect(
                url_for("register", _external=True, _scheme='https'))

        # check if email already exists in database
        existing_email = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})
        if existing_email:
            flash("Email already registered")
            return redirect(
                url_for("register", _external=True, _scheme='https'))

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
        return redirect(
            url_for("profile", username=session["user"], _external=True,
                    _scheme='https'))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Allows user to login to their user account """
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
               existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}!".format(
                    request.form.get("username").capitalize()))
                return redirect(
                    url_for("profile", username=session["user"],
                            _external=True, _scheme='https'))
            else:
                # invalid password entered by user
                flash("Incorrect Username and/or Password")
                return redirect(
                    url_for("login", _external=True, _scheme='https'))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login", _external=True, _scheme='https'))

    return render_template("login.html")


@app.route("/profile/<username>", methods=("GET", "POST"))
def profile(username):
    """ Checks if user is in session and renders the profile page """
    if "user" in session:
        # grab the session user from the db
        user = mongo.db.users.find_one({"username": session["user"]})
        # gets a list of reviews created by user
        user_reviews = list(mongo.db.reviews.find(
            {"created_by": session["user"]}))
        # Gets list of user favourite products
        favourites = list(mongo.db.products.find(
            {"_id": {"$in": user["favourites"]}}))
        return render_template(
            "profile.html", user=user,
            favourites=favourites, user_reviews=user_reviews
        )

    return redirect(url_for("login", _external=True, _scheme='https'))


@app.route("/favourites/<product_id>)", methods=["GET", "POST"])
def favourites(product_id):
    """ Allows user to add a product to their favourites """
    # Checks if user is in session
    if "user" in session:
        # Adds product to user favourites
        user = mongo.db.users.find_one_and_update(
            {"username": session["user"].lower()},
            {"$push": {"favourites": ObjectId(product_id)}})
        flash("Product added to favourites")
        return redirect(
            url_for("profile", username=user["username"],
                    _external=True, _scheme='https'))

    return redirect(url_for("login", _external=True, _scheme='https'))


@app.route("/delete_favourite/<product_id>)", methods=["GET", "POST"])
def delete_favourite(product_id):
    """ Allows a user to delete a product from their favourites """
    # Checks if user is in session
    if "user" in session:
        # Removes a product from user favourites
        user = mongo.db.users.find_one_and_update(
            {"username": session["user"]},
            {"$pull": {"favourites": ObjectId(product_id)}})
        flash("Product removed from favourites")
        return redirect(
            url_for("profile", username=user["username"], _external=True,
                    _scheme='https'))

    return redirect(url_for("login", _external=True, _scheme='https'))


@app.route("/delete_profile/<username>")
def delete_profile(username):
    """ Allows a user to delete their user account """
    # Checks if user is in session
    if "user" in session:
        # Deletes all reviews created by user
        mongo.db.reviews.delete_many({"created_by": session["user"]})
        # Removes user account from db
        mongo.db.users.remove({"username": session["user"]})
        flash("Your account has been deleted!")
        # Clears session cookies
        session.clear()
        return redirect(
            url_for("home", _external=True, _scheme='https'))


@app.route("/delete_user_account/<user_id>")
def delete_user_account(user_id):
    """ Allows Admin to delete user accounts """
    # Checks if user is in session
    if "user" in session:
        # Checks if user is admin
        if session["user"] == "admin".lower():
            # Gets all reviews created by user account
            mongo.db.reviews.delete_many({"created_by": user_id})
            # Removes user account from the db
            mongo.db.users.remove({"_id": ObjectId(user_id)})
            flash("This account has been deleted!")
            username = mongo.db.users.find_one(
                    {"username": session["user"]})["username"]
            return redirect(
                url_for("profile", username=username,
                        _external=True, _scheme='https'))
    # If user is not in session display 404 page
    else:
        abort(404)


@app.route("/logout")
def logout():
    """ Allows a user to log out of their account """
    # remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login", _external=True, _scheme='https'))


@app.route("/manage_users")
def manage_users():
    """ Allows Admin to manage user accounts """
    # Checks if user is in session
    if "user" in session:
        # Checks if user is admin
        if session["user"] == "admin".lower():
            # Gets a list of all user accounts - Admin access only
            users = list(mongo.db.users.find())
            return render_template("manage_users.html", users=users)
        # if user is not admin redirect to homepage
        else:
            flash('You do not have authorised access')
            return redirect(url_for('home'))
    # if user not in session display 404 page
    else:
        abort(404)


@app.route("/user_feedback/<user_id>", methods=["GET", "POST"])
def user_feedback(user_id):
    """ Allows registered user to submit user feedback to the db """
    # Checks if user is in session
    if "user" in session:
        # If user submits feedback through modal
        if request.method == "POST":
            feedback = {
                "user": ObjectId(user_id),
                "name": request.form.get("name"),
                "comment": request.form.get("comment")
            }
            # Inserts user feedback into user_feedback in db
            mongo.db.user_feedback.insert_one(feedback)
            flash("Your message has been sent")
            return redirect(
                url_for(
                    "profile", username=session["user"],
                    _external=True, _scheme='https'))
    # If user not in session redirect user back to login page
    else:
        flash('You need to log in to access this page.')
        return redirect(url_for('login'))


@app.route("/manage_feedback")
def manage_feedback():
    """ Allows Admin to manage user feedback """
    # Checks if user is in session
    if "user" in session:
        # Checks if user is admin
        if session["user"] == "admin".lower():
            # Gets a list of all user feedback from the db
            feedback = list(mongo.db.user_feedback.find())
            return render_template("user_feedback.html", feedback=feedback)
        # If user not Admin redirect to homepage
        else:
            flash('Authorised permission required')
            return redirect(url_for('home'))
    # if user not in session display 404 page
    else:
        abort(404)


@app.route("/delete_feedback/<user_feedback_id>")
def delete_feedback(user_feedback_id):
    """ Allows Admin to delete user feedback comments from the db """
    # Checks if user is in session
    if "user" in session:
        # Checks if user is admin
        if session["user"] == "admin".lower():
            # Removes a specific feedback entry from the db
            mongo.db.user_feedback.remove({"_id": ObjectId(user_feedback_id)})
            flash("This comment has been deleted!")
            username = mongo.db.users.find_one(
                    {"username": session["user"]})["username"]
            return redirect(
                url_for("profile", username=username,
                        _external=True, _scheme='https'))
        else:
            flash('Authorised permission required')
            return redirect(url_for('home'))
    else:
        abort(404)


# 404 error page
@app.errorhandler(404)
def page_not_found(error):
    """ Renders the 404 error page """
    return render_template("404.html"), 404


# 500 error page
@app.errorhandler(500)
def internal_server(error):
    """ Renders the 500 internal server error page """
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)
