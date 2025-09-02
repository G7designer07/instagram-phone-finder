from flask import Flask, request, render_template, send_file
import os
import io
import csv
import time
from instagrapi import Client

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change-me")

INSTAGRAM_USER = os.environ.get("INSTAGRAM_USER")
INSTAGRAM_PASS = os.environ.get("INSTAGRAM_PASS")
SESSION_FILE = f"session_{INSTAGRAM_USER}.json" if INSTAGRAM_USER else "session.json"

def get_client():
    if not INSTAGRAM_USER or not INSTAGRAM_PASS:
        raise RuntimeError("Credenciais do Instagram não configuradas. Defina INSTAGRAM_USER e INSTAGRAM_PASS nas variáveis de ambiente.")
    cl = Client()
    # tenta carregar sessão salva
    if os.path.exists(SESSION_FILE):
        try:
            cl.load_settings(SESSION_FILE)
        except Exception:
            pass
    try:
        cl.login(INSTAGRAM_USER, INSTAGRAM_PASS)
    except Exception:
        # tenta login "limpo" se algo falhar
        cl = Client()
        cl.login(INSTAGRAM_USER, INSTAGRAM_PASS)
    try:
        cl.dump_settings(SESSION_FILE)
    except Exception:
        pass
    return cl

def normalize_profile(profile):
    profile = (profile or "").strip()
    profile = profile.rstrip('/')
    if profile.startswith('http'):
        profile = profile.rstrip('/').split('/')[-1]
    if profile.startswith('@'):
        profile = profile[1:]
    return profile

def fetch_followers(profile, limit=500):
    profile = normalize_profile(profile)
    cl = get_client()
    user_id = cl.user_id_from_username(profile)
    followers_dict = cl.user_followers(user_id)
    results = []
    count = 0
    for follower in followers_dict.values():
        if count >= limit:
            break
        try:
            info = cl.user_info(follower.pk)
            data = info.dict()
            name = data.get("full_name") or data.get("username") or getattr(follower, "username", "")
            username = data.get("username") or getattr(follower, "username", "")
            phone = data.get("public_phone_number") or data.get("business_phone_number") or ""
        except Exception:
            name = getattr(follower, "full_name", "") or getattr(follower, "username", "")
            username = getattr(follower, "username", "")
            phone = ""
        results.append({"name": name, "username": username, "phone": phone})
        count += 1
        # pequeno delay para reduzir chance de bloqueio
        time.sleep(0.25)
    return results

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/export", methods=["POST"])
def export():
    profile = request.form.get("profile", "")
    try:
        limit = int(request.form.get("limit", 500))
    except:
        limit = 500
    limit = max(1, min(limit, 2000))  # garante valor entre 1 e 2000
    try:
        results = fetch_followers(profile, limit)
    except Exception as e:
        # mostra erro amigável na página inicial
        return render_template("index.html", error=str(e))
    return render_template("results.html", profile=profile, results=results, limit=limit)

@app.route("/download", methods=["POST"])
def download():
    profile = request.form.get("profile", "")
    try:
        limit = int(request.form.get("limit", 500))
    except:
        limit = 500
    limit = max(1, min(limit, 2000))
    results = fetch_followers(profile, limit)

    output = io.StringIO()
    writer = csv.writer(output, delimiter=",", lineterminator="\n")
    writer.writerow(["name", "username", "phone"])
    for r in results:
        writer.writerow([r["name"], r["username"], r["phone"]])
    output.seek(0)

    filename = f"{normalize_profile(profile)}_followers.csv"
    return send_file(io.BytesIO(output.getvalue().encode("utf-8")),
                     mimetype="text/csv",
                     as_attachment=True,
                     download_name=filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
