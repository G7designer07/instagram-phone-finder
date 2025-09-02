from flask import Flask, request, render_template, send_file
import csv
import io
from instagrapi import Client

app = Flask(__name__)

# login fixo (pode usar variáveis de ambiente no Render para segurança)
INSTAGRAM_USER = "seu_usuario"
INSTAGRAM_PASS = "sua_senha"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/export", methods=["POST"])
def export():
    profile = request.form["profile"].strip().replace("https://instagram.com/", "").replace("/", "")

    cl = Client()
    cl.login(INSTAGRAM_USER, INSTAGRAM_PASS)

    user_id = cl.user_id_from_username(profile)
    followers = cl.user_followers(user_id)

    # cria CSV em memória
    output = io.StringIO()
    writer = csv.writer(output, delimiter=",")
    writer.writerow(["nome", "username", "telefone"])

    for follower in followers.values():
        nome = follower.full_name
        username = follower.username
        info = cl.user_info(follower.pk).dict()
        telefone = info.get("public_phone_number", "")
        writer.writerow([nome, username, telefone])

    output.seek(0)

    return send_file(io.BytesIO(output.getvalue().encode("utf-8")),
                     mimetype="text/csv",
                     as_attachment=True,
                     download_name=f"{profile}_seguidores.csv")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
