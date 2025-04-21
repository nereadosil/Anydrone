from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import firebase_admin
from firebase_admin import credentials, firestore
from werkzeug.security import generate_password_hash, check_password_hash
import math
import requests
from datetime import datetime

# --- Flask Setup ---
app = Flask(__name__)
app.secret_key = "supersecretkey"

# --- Firebase Init ---
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# --- Utils ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# --- Routes ---

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)

        existing = list(db.collection("users").where("user_email_address", "==", email).stream())
        if existing:
            flash("Email already registered.", "warning")
            return redirect(url_for("register"))

        db.collection("users").add({
            "user_name": name,
            "user_email_address": email,
            "user_password": hashed_password
        })

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        users = list(db.collection("users").where("user_email_address", "==", email).stream())
        if users and check_password_hash(users[0].to_dict()["user_password"], password):
            user = users[0]
            session["user_id"] = user.id
            session["name"] = user.to_dict()["user_name"]
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials", "danger")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    drones_query = db.collection("drones").where("owner_id", "==", session["user_id"]).stream()
    drone_list = []
    for drone_doc in drones_query:
        drone = drone_doc.to_dict()
        drone["drone_id"] = drone_doc.id
        services_query = db.collection("services").where("drone_id", "==", drone_doc.id).stream()
        drone["services"] = [s.to_dict() | {"service_id": s.id} for s in services_query]
        drone_list.append(drone)

    return render_template("dashboard.html", name=session["name"], drones=drone_list)


@app.route("/add_drone", methods=["GET", "POST"])
def add_drone():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        data = {
            "owner_id": session["user_id"],
            "model": request.form["model"],
            "manufacturer": request.form["manufacturer"],
            "camera_quality": request.form["camera_quality"],
            "max_load": float(request.form["max_load"]),
            "flight_time": int(request.form["flight_time"]),
            "latitude": float(request.form["latitude"]),
            "longitude": float(request.form["longitude"])
        }

        db.collection("drones").add(data)
        flash("Drone added successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("add_drone.html")


@app.route("/add_service/<drone_id>", methods=["GET", "POST"])
def add_service(drone_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        data = {
            "drone_id": drone_id,
            "service_name": request.form["service_name"],
            "service_description": request.form["service_description"],
            "price": float(request.form["price"]),
            "is_available": request.form.get("is_available") == "on",
            "stream_url": request.form["stream_url"]  # 👈 nuevo campo
        }

        db.collection("services").add(data)
        flash("Service added successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("add_service.html", drone_id=drone_id)


@app.route("/all_drones")
def all_drones():
    drones_query = db.collection("drones").stream()
    drones = {}

    for d in drones_query:
        drone = d.to_dict()
        drone_id = d.id
        services = db.collection("services").where("drone_id", "==", drone_id).stream()

        drones[drone_id] = drone | {
            "services": [s.to_dict() | {"service_id": s.id} for s in services]
        }

    return render_template("all_drones.html", drones=drones)



@app.route("/contract/<service_id>", methods=["GET", "POST"])
def contract_service(service_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        data = {
            "user_id": session["user_id"],
            "service_id": service_id,
            "start_time": request.form["start_time"],
            "duration_hours": float(request.form["duration"]),
            "notes": request.form.get("notes", ""),
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }

        db.collection("contracts").add(data)
        flash("Service contracted successfully!", "success")
        return redirect(url_for("all_drones"))

    service_doc = db.collection("services").document(service_id).get()
    service = service_doc.to_dict()
    drone = db.collection("drones").document(service["drone_id"]).get().to_dict()

    service["model"] = drone["model"]
    service["manufacturer"] = drone["manufacturer"]
    return render_template("contract_service.html", service=service)

@app.route("/my_contracts")
def my_contracts():
    if "user_id" not in session:
        return redirect(url_for("login"))

    contracts = []
    query = db.collection("contracts").where("user_id", "==", session["user_id"]).stream()
    for c in query:
        contract = c.to_dict()

        service = db.collection("services").document(contract["service_id"]).get().to_dict()
        drone = db.collection("drones").document(service["drone_id"]).get().to_dict()
        owner = db.collection("users").document(drone["owner_id"]).get().to_dict()

        contract.update({
            "service_name": service["service_name"],
            "drone_model": drone["model"],
            "owner_name": owner["user_name"],
            "stream_url": service.get("stream_url", ""),  # ✅ clave para el botón
            "status": contract.get("status", "pending"),  # por si no tiene estado aún
            "contract_id": c.id  # útil para otras acciones futuras
        })

        contracts.append(contract)

    return render_template("my_contracts.html", contracts=contracts)


@app.route("/my_requests")
def my_requests():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # 1. Obtener todos los drones del usuario
    drone_docs = db.collection("drones").where("owner_id", "==", session["user_id"]).stream()
    drone_ids = [d.id for d in drone_docs]

    # 2. Obtener los servicios de esos drones
    requests = []

    if drone_ids:
        service_docs = db.collection("services").where("drone_id", "in", drone_ids).stream()
        service_ids = [s.id for s in service_docs]

        # 3. Si hay servicios, obtener los contratos
        if service_ids:
            contracts = db.collection("contracts").where("service_id", "in", service_ids).stream()

            for c in contracts:
                contract = c.to_dict()

                # Obtener datos relacionados
                service = db.collection("services").document(contract["service_id"]).get().to_dict()
                drone = db.collection("drones").document(service["drone_id"]).get().to_dict()
                client = db.collection("users").document(contract["user_id"]).get().to_dict()

                # Enriquecer contrato
                contract.update({
                    "service_name": service["service_name"],
                    "drone_model": drone["model"],
                    "client_name": client["user_name"],
                    "contract_id": c.id
                })

                requests.append(contract)

    return render_template("my_requests.html", requests=requests)



@app.route("/approve_request/<contract_id>")
def approve_request(contract_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    contract_ref = db.collection("contracts").document(contract_id)
    contract = contract_ref.get().to_dict()
    service = db.collection("services").document(contract["service_id"]).get().to_dict()
    drone = db.collection("drones").document(service["drone_id"]).get().to_dict()

    if drone["owner_id"] == session["user_id"]:
        contract_ref.update({"status": "confirmed"})
        flash("Contract approved successfully", "success")
    else:
        flash("Unauthorized action", "danger")

    return redirect(url_for("my_requests"))


@app.route("/reject_request/<contract_id>")
def reject_request(contract_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    contract_ref = db.collection("contracts").document(contract_id)
    contract = contract_ref.get().to_dict()
    service = db.collection("services").document(contract["service_id"]).get().to_dict()
    drone = db.collection("drones").document(service["drone_id"]).get().to_dict()

    if drone["owner_id"] == session["user_id"]:
        contract_ref.update({"status": "cancelled"})
        flash("Contract rejected", "warning")
    else:
        flash("Unauthorized action", "danger")

    return redirect(url_for("my_requests"))


@app.route("/search_drones", methods=["GET", "POST"])
def search_drones():
    drones = []
    if request.method == "POST":
        place_name = request.form["place_name"]
        radius = float(request.form["radius"])

        geo_url = f"https://nominatim.openstreetmap.org/search?q={place_name}&format=json&limit=1"
        response = requests.get(geo_url, headers={"User-Agent": "AnyDroneApp/1.0"})
        results = response.json()

        if not results:
            flash("Location not found. Please try a more specific name.", "warning")
            return render_template("search_drones.html", drones=[])

        lat = float(results[0]["lat"])
        lon = float(results[0]["lon"])

        all_drones = db.collection("drones").stream()
        for d in all_drones:
            drone = d.to_dict()
            if "latitude" in drone and "longitude" in drone:
                dist = haversine(lat, lon, drone["latitude"], drone["longitude"])
                if dist <= radius:
                    drone["drone_id"] = d.id
                    services = db.collection("services").where("drone_id", "==", d.id).stream()
                    drone["services"] = [s.to_dict() | {"service_id": s.id} for s in services]
                    drones.append(drone)

    return render_template("search_drones.html", drones=drones)


@app.route("/map")
def drone_map():
    drone_data = []
    drones = db.collection("drones").stream()
    for d in drones:
        drone = d.to_dict()
        if drone.get("latitude") is not None and drone.get("longitude") is not None:
            services = db.collection("services").where("drone_id", "==", d.id).stream()
            drone["services"] = [s.to_dict() | {"service_id": s.id} for s in services]
            drone_data.append(drone)
    return render_template("drone_map.html", drones=drone_data)


@app.route("/delete_drone/<drone_id>", methods=["POST"])
def delete_drone(drone_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    drone_ref = db.collection("drones").document(drone_id)
    drone = drone_ref.get().to_dict()

    if not drone or drone["owner_id"] != session["user_id"]:
        flash("Unauthorized or drone not found.", "danger")
        return redirect(url_for("dashboard"))

    # Delete contracts linked to services under this drone
    services = db.collection("services").where("drone_id", "==", drone_id).stream()
    for service in services:
        service_id = service.id
        contracts = db.collection("contracts").where("service_id", "==", service_id).stream()
        for contract in contracts:
            db.collection("contracts").document(contract.id).delete()

        db.collection("services").document(service_id).delete()

    drone_ref.delete()
    flash("Drone deleted successfully.", "success")
    return redirect(url_for("dashboard"))

@app.route("/sync_drones", methods=["POST"])
def sync_drones():
    data = request.get_json()

    if not data or "drones" not in data:
        return jsonify({"error": "Formato inválido o sin datos"}), 400

    try:
        for drone in data["drones"]:
            drone_id = drone.get("drone_id")

            if not drone_id:
                continue  # ignorar si no hay ID

            # Referencia al documento en Firestore
            drone_ref = db.collection("drones").document(drone_id)

            # Actualizar o crear con merge
            drone_ref.set({
                "model": drone.get("model", "Unknown"),
                "manufacturer": drone.get("manufacturer", "Unknown"),
                "camera_quality": drone.get("camera_quality", "Unknown"),
                "max_load": drone.get("max_load", 0),
                "flight_time": drone.get("flight_time", 0),
                "latitude": drone.get("latitude"),
                "longitude": drone.get("longitude"),
                "owner_id": drone.get("owner_id", "local_user"),
                "last_updated": firestore.SERVER_TIMESTAMP  # opcional: para seguimiento
            }, merge=True)

            print(f"🛰️ Drone {drone_id} actualizado en Firestore.")

        return jsonify({"message": "Drones sincronizados correctamente"}), 200

    except Exception as e:
        print("❌ Error en /sync_drones:", e)
        return jsonify({"error": str(e)}), 500



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
