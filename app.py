from flask import Flask, request, render_template, send_file
import requests
from bs4 import BeautifulSoup
import csv
import io

app = Flask(__name__)

def fetch_public_info(username):
    url = f"https://www.instagram.com/{username}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    
    if res.status_code != 200:
        return None
    
    soup = BeautifulSoup(res.text, "html.parser")
    title = soup.title.text if soup.title else ""
    bio_tag = soup.find("meta", attrs={"name": "description"})
    bio = bio_tag["content"] if bio_tag else ""
    
    return {
        "username": username,
        "public_name": title.split("•")[0].strip(),
        "bio": bio
    }

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/export", methods=["POST"])
def export():
    profile = request.form.get("profile", "").strip()
    if profile.startswith("http"):
        profile = profile.rstrip('/').split("/")[-1]
    if profile.startswith("@"):
        profile = profile[1:]
    
    info = fetch_public_info(profile)
    if not info:
        return render_template("index.html", error="Perfil não encontrado ou privado.")
    
    # Exibe os dados na página antes de baixar
    return render_template("results.html", info=info)
    
@app.route("/download", methods=["POST"])
def download():
    username = request.form.get("username")
    info = fetch_public_info(username)
    if not info:
        return "Erro: perfil não encontrado", 404

    output = io.StringIO()
    writer = csv.writer(output, delimiter=",", lineterminator="\n")
    writer.writerow(["username", "public_name", "bio"])
    writer.writerow([info["username"], info["public_name"], info["bio"]])
    output.seek(0)

    filename = f"{username}_public.csv"
    return send_file(io.BytesIO(output.getvalue().encode("utf-8")),
                     mimetype="text/csv",
                     as_attachment=True,
                     download_name=filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
