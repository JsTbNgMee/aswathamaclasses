from flask import Flask, render_template, jsonify
import requests
import os

app = Flask(__name__)

# 🔑 Put your NASA API key here (or set in Replit secrets)
NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/asteroids")
def asteroids():
    # Example: fetch near earth objects from NASA API
    url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date=2025-09-20&end_date=2025-09-22&api_key={NASA_API_KEY}"
    try:
        res = requests.get(url)
        data = res.json()

        asteroid_list = []
        for date in data["near_earth_objects"]:
            for asteroid in data["near_earth_objects"][date]:
                name = asteroid["name"]
                est_diameter = asteroid["estimated_diameter"]["meters"]["estimated_diameter_max"]
                orbit = asteroid.get("orbital_data", {})

                asteroid_list.append({
                    "name": name,
                    "diameter": est_diameter,
                    "orbit": {
                        "semi_major_axis": float(orbit.get("semi_major_axis", 1.5)),
                        "eccentricity": float(orbit.get("eccentricity", 0.1)),
                        "inclination": float(orbit.get("inclination", 0.0))
                    }
                })

        return jsonify(asteroid_list)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
