from flask import Flask, render_template, request, redirect, url_for, session
from services.api_integration import get_country_info
from services.api_integration import get_famous_places
from unittest import result
from logger.logger import log_info

app = Flask(__name__)
app.secret_key = "supersecretkey"


users = {"testuser": "password123"}

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and users[username] == password:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if username in users:
            return render_template("signup.html", error="Username already exists")
        else:
            users[username] = password
            return redirect(url_for("login"))

    
    return render_template("signup.html")
    
@app.route("/index", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect(url_for("login"))
    
    
    if request.args.get("clear"):
        session.pop("last_query", None)
        session.pop("region_results", None)

    country_data = None
    is_region = False
    error = None
    page = int(request.args.get("page", 1))
    per_page = 10

    if request.method == "POST":
        query = request.form["query"].strip()
        session["last_query"] = query
        session.pop("region_results", None)  
        return redirect(url_for("index", page=1))

    if "last_query" in session:
        query = session["last_query"]

        
        if "region_results" in session:
            result = session["region_results"]
        else:
            result = get_country_info(query)
            
            if isinstance(result, list):
                session["region_results"] = result

        if not result:
            error = f"No results found for '{query}'"
            total_pages = 1
        elif isinstance(result, list):  
            is_region = True
            total = len(result)
            start = (page - 1) * per_page
            end = start + per_page
            country_data = result[start:end]
            total_pages = (total + per_page - 1) // per_page
        else:  
            country_data = result
            total_pages = 1
    else:
        total_pages = 1
        page = 1

    return render_template(
        "index.html",
        country_data=country_data,
        is_region=is_region,
        error=error,
        page=page,
        total_pages=total_pages
    )

@app.route("/country/<name>")
def getdetail(name):
    result = get_country_info(name)
    if not result:
        return render_template("index.html", error=f"No details found for {name}")

    
    if isinstance(result, list):  
        return render_template("index.html", country_data=result, is_region=True)
    else:  
        result["famous_places"] = get_famous_places(result["name"])
        return render_template("index.html", country_data=result, is_region=False)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/signup.html")
def signup_html():
    return redirect(url_for("signup"))

@app.route("/login.html")
def login_html():
    return redirect(url_for("login"))

@app.route("/index.html")
def index_html():
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"])


if __name__ == "__main__":
    app.run(debug=True)