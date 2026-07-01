from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
import pymysql

from werkzeug.security import generate_password_hash, check_password_hash
# from config import connection

app = Flask(__name__)
app.secret_key = "nearby_services_finder_secret"
# Gujarat District Coordinates
districts = {
    "Ahmedabad": (23.0225, 72.5714),
    "Surat": (21.1702, 72.8311),
    "Rajkot": (22.3039, 70.8022),
    "Vadodara": (22.3072, 73.1812),
    "Bhavnagar": (21.7645, 72.1519),
    "Jamnagar": (22.4707, 70.0577),
    "Junagadh": (21.5222, 70.4579),
    "Anand": (22.5645, 72.9289),
    "Bharuch": (21.7051, 72.9959),
    "Gandhinagar": (23.2156, 72.6369)
}

@app.route("/")
def index():
    return render_template("welcome.html")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        return "Login form submitted successfully"

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":
        return "Signup form submitted successfully"

    return render_template("signup.html")


# @app.route("/signup", methods=["GET", "POST"])
# def signup():

#     if request.method == "POST":

#         fullname = request.form["fullname"].strip()
#         email = request.form["email"].strip().lower()
#         password = request.form["password"]

#         cursor = connection.cursor(pymysql.cursors.DictCursor)

#         cursor.execute(
#             "SELECT id FROM users WHERE email=%s",
#             (email,)
#         )

#         if cursor.fetchone():
#             return "Email already exists."

#         password = generate_password_hash(password)

#         cursor.execute(
#             """
#             INSERT INTO users(fullname,email,password)
#             VALUES(%s,%s,%s)
#             """,
#             (fullname,email,password)
#         )

#         connection.commit()

#         return redirect("/login")

#     return render_template("signup.html")


# @app.route("/login", methods=["GET", "POST"])
# def login():

#     if request.method == "POST":

#         email = request.form["email"].strip().lower()
#         password = request.form["password"]

#         cursor = connection.cursor(pymysql.cursors.DictCursor)

#         cursor.execute(
#             "SELECT * FROM users WHERE email=%s",
#             (email,)
#         )

#         user = cursor.fetchone()

#         if user and check_password_hash(user["password"], password):

#             session["user_id"] = user["id"]
#             session["user_name"] = user["fullname"]
#             session["user_email"] = user["email"]
#             print(user)
#             print(session["user_email"])

#             return redirect("/home")

#         return "Invalid Email or Password"

#     return render_template("login.html")


# @app.route("/logout")
# def logout():

#     session.clear()

#     return redirect("/")

@app.route("/search-page", methods=["POST"])
def search_page():

    search_type = request.form["search_type"]
    service = request.form["service"]
    radius = int(request.form["radius"])

    if search_type == "address":

        address = request.form["address"]

        geo_url = "https://nominatim.openstreetmap.org/search"

        response = requests.get(
            geo_url,
            params={
                "q": address,
                "format": "json",
                "limit": 1
            },
            headers={
                "User-Agent": "Nearby Services Finder"
            }
        )

        geo_data = response.json()

        if len(geo_data) == 0:
            return "Address not found"

        lat = float(geo_data[0]["lat"])
        lon = float(geo_data[0]["lon"])
        print("Address:", address)
        print("Latitude:", lat)
        print("Longitude:", lon)

        district = address

    else:

        district = request.form["district"]
        lat, lon = districts[district]

    return render_template(
        "result.html",
        district=district,
        lat=lat,
        lon=lon,
        service=service,
        radius=radius
    )


@app.route("/search", methods=["POST"])
def search():

    data = request.get_json()

    lat = data["lat"]
    lon = data["lon"]
    service = data["service"]
    radius = int(data["radius"])
    print("SEARCH LAT:", lat)
    print("SEARCH LON:", lon)
    print("SERVICE:", service)
    print("RADIUS:", radius)
   # ---------------- Hotel ----------------

    if service == "hotel":

        overpass_query = f"""
[out:json][timeout:25];
(
 nwr["tourism"="hotel"](around:{radius},{lat},{lon});
 nwr["tourism"="hostel"](around:{radius},{lat},{lon});
 nwr["tourism"="guest_house"](around:{radius},{lat},{lon});
 nwr["tourism"="motel"](around:{radius},{lat},{lon});
);
out center tags;
"""

    # ---------------- Cafe ----------------

    elif service == "cafe":

        overpass_query = f"""
[out:json][timeout:25];
(
 nwr["amenity"="cafe"](around:{radius},{lat},{lon});
 nwr["amenity"="restaurant"](around:{radius},{lat},{lon});
 nwr["amenity"="fast_food"](around:{radius},{lat},{lon});
);
out center tags;
"""

    # ---------------- Petrol Pump ----------------

    elif service == "fuel":

        overpass_query = f"""
[out:json][timeout:25];
(
 nwr["amenity"="fuel"](around:{radius},{lat},{lon});
);
out center tags;
"""

    # ---------------- Hospital ----------------

    elif service == "hospital":

        overpass_query = f"""
[out:json][timeout:25];
(
 nwr["amenity"="hospital"](around:{radius},{lat},{lon});
);
out center tags;
"""

    # ---------------- Default ----------------

    else:

        overpass_query = f"""
[out:json][timeout:25];
(
 nwr["amenity"="{service}"](around:{radius},{lat},{lon});
);
out center tags;
"""
    

       
    url = "https://overpass-api.de/api/interpreter"

    response = requests.get(
        url,
        params={"data": overpass_query},
        headers={"User-Agent": "Nearby Services Finder"}
    )

    places = response.json()

    results = []

    for place in places.get("elements", []):

        tags = place.get("tags", {})

        address = ", ".join(filter(None, [

            tags.get("addr:housenumber"),

            tags.get("addr:street"),

            tags.get("addr:city"),

            tags.get("addr:state")

        ]))

        if address == "":

            address = "Address Not Available"

        results.append({

            "name": tags.get("name", "Unknown"),

            "lat": place.get("lat") or place.get("center", {}).get("lat"),

            "lon": place.get("lon") or place.get("center", {}).get("lon"),

            "address": address

        })

    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)