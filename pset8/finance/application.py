import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    # get stocks for and user details
    stocks = db.execute("SELECT * FROM stocks WHERE user_id = :user_id", user_id = session["user_id"])
    user = db.execute("SELECT * FROM users WHERE id = :user_id", user_id = session["user_id"])

    total = 0.0
    # loop through stocks and get details
    for i in range(len(stocks)):
        stock = lookup(stocks[i]["symbol"])
        stocks[i]["name"] = stock["name"]
        stocks[i]["price"] = stock["price"]
        stocks[i]["total"] = stocks[i]["quantity"] * stock["price"]
        total += stocks[i]["total"]
    total += user[0]["cash"]
    total = usd(total)

    return render_template("index.html", stocks = stocks, cash = usd(user[0]["cash"]), total = total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        # apology if no or wrong symbol provided
        if not request.form.get("symbol"):
            return apology("You must provide a stock symbol!")

        # apology if shares not number
        if not (int(request.form.get("shares")) > 0):
            return apology("Shares request must be a positive integer")

        # apology for no symbol
        quote = lookup(request.form.get("symbol"))
        if not quote:
            return apology("Please provide a valid stock symbol")
        cost = int(request.form.get("shares")) * quote["price"]

        # apology if not enough money
        rows = db.execute("SELECT * from users where id = :user_id", user_id = session["user_id"])
        cash = rows[0]["cash"]
        if cash < cost:
            return apology("You do not have enough cash to buy")
        cash_left = cash - cost

        # check if stock already owned
        check_stock = db.execute("SELECT * from stocks WHERE user_id = :user_id AND symbol = :symbol",
                    user_id = session["user_id"], symbol = quote["symbol"])
        if len(check_stock) == 1:
            new_quantity = int(check_stock[0]["quantity"]) + int(request.form.get("shares"))
            new_total = check_stock[0]["total"] + cost
            new_price = "%.2f"%(new_total/new_quantity)
            db.execute("UPDATE stocks SET quantity = :quantity, total = :total, price = :price WHERE user_id = :user_id and symbol = :symbol",
                    quantity = new_quantity, total = new_total, price = new_price, user_id = session["user_id"], symbol = quote["symbol"])
        # create stocks table entry if not bought before
        else:
            db.execute("INSERT INTO stocks (user_id, symbol, quantity, price, total) VALUES (:user_id, :symbol, :quantity, :price, :total)",
                    user_id = session["user_id"],
                    symbol = quote["symbol"],
                    quantity = int(request.form.get("shares")),
                    price = quote["price"],
                    total = cost)
        # update history table
        db.execute("INSERT INTO history (user_id, symbol, quantity, price) VALUES (:user_id, :symbol, :quantity, :price)",
                    user_id = session["user_id"],
                    symbol = quote["symbol"],
                    quantity = int(request.form.get("shares")),
                    price = quote["price"])
        # modify available funds
        db.execute("UPDATE users SET cash = :cash WHERE id = :id", cash = cash_left, id = session["user_id"])
        # redirect to home page
        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    stocks = db.execute("SELECT * from history WHERE user_id = :user_id", user_id = session["user_id"])
    return render_template("history.html", stocks = stocks)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():

    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("You must provide a stock symbol!")
        quote = lookup(request.form.get("symbol"))
        if not quote:
            return apology("failed to find stock")
        return render_template("quoted.html", symbol = quote["symbol"], name = quote["name"], price = quote["price"])

    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # apology if username blank
        if not request.form.get("username"):
            return apology("You must provide a username")
        # apology if username already exists
        rows = db.execute("SELECT * from users WHERE username = :username", username = request.form.get("username"))
        if len(rows) != 0:
            return apology("Username must be unique")
        # apology if password or confirmation blank or both don't match
        if not request.form.get("password") or not request.form.get("confirmation") or request.form.get("password") != request.form.get("confirmation"):
            return apology("Pasword and confirmation mut match")
        # insert new user into users, storing hash of pasword
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                    username = request.form.get("username"),
                    hash = generate_password_hash(request.form.get("password")))
        # login
        rows = db.execute("SELECT * FROM users WHERE username = :username", username = request.form.get("username"))
        session["user_id"] = rows[0]["id"]
        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        # check if any field blank
        if not request.form.get("password") or not request.form.get("newpass") or not request.form.get("newpass2"):
            return apology("You must fill in all fields")
        # check that password changes match
        if request.form.get("newpass") != request.form.get("newpass2"):
            return apology("New password doesn't match")
        #check correct password entered
        rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id = session["user_id"])
        # Check password is correct
        if not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)
        # update password
        db.execute("UPDATE users SET hash = :hash WHERE id = :user_id",
            hash = generate_password_hash(request.form.get("newpass")), user_id = session["user_id"])
        changed = 1
        return render_template("account.html", changed = changed)

    else:
        return render_template("account.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    stocks = db.execute("SELECT * from stocks WHERE user_id = :user_id", user_id = session["user_id"])
    if request.method == "POST":
        # check stocck selected
        if not request.form.get("symbol"):
            return apology("You must provide a stock symbol!")

        # check user owns stock
        stock_check = db.execute("SELECT * from stocks WHERE user_id = :user_id and symbol = :symbol",
                user_id = session["user_id"], symbol = request.form.get("symbol"))
        if len(stock_check) == 0:
            return apology("You must choose stock you own")

        # check number stock sold positive integer
        if not (int(request.form.get("shares")) > 0):
            return apology("Shares request must be a positive integer")

        # check number of stock being sold is owned
        if int(request.form.get("shares")) > int(stock_check[0]["quantity"]):
            return apology("You can't sell more stock than you own")

        # delete stocks if all sold or update stocks
        if request.form.get("shares") == stock_check[0]["quantity"]:
            db.execute("DELETE from stocks WHERE user_id = :user_id AND symbol = :symbool",
                            user_id = session["user_id"], symbol = request.form.get("symbol"))
        else:
            new_quantity = int(stock_check[0]["quantity"]) - int(request.form.get("shares"))
            new_total = new_quantity * stock_check[0]["price"]
            db.execute("UPDATE stocks SET quantity = :quantity, total = :total WHERE user_id = :user_id AND symbol = :symbol",
                        quantity = new_quantity, total = new_total, user_id = session["user_id"], symbol = request.form.get("symbol"))

        # work out new cash
        stock_lookup = lookup(request.form.get("symbol"))
        user = db.execute("SELECT * from users WHERE id = :user_id", user_id = session["user_id"])
        new_cash = user[0]["cash"] + float(request. form.get("shares")) * float(stock_lookup["price"])
        # update history
        db.execute("INSERT INTO history (user_id, symbol, quantity, price) VALUES (:user_id, :symbol, :quantity, :price)",
                    user_id = session["user_id"],
                    symbol = request.form.get("symbol"),
                    quantity = -abs(int(request.form.get("shares"))),
                    price = stock_lookup["price"])
        # update cash
        db.execute("UPDATE users SET cash = :cash WHERE id = :user_id", cash = new_cash, user_id = session["user_id"])
        return redirect("/")
    else:
        return render_template("sell.html", stocks = stocks)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
