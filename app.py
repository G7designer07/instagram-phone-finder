from flask import Flask, request, render_template_string
import requests, re, os

app = Flask(__name__)

def get_phone_from_instagram(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    # normaliza a URL
    if url.endswith('/'):
        url = url[:-1]
    if not url.startswith("http"):
        url = "https://www.instagram.com/" + url.lstrip("@")

    try:
        response = requests.get(url + "?__a=1&__d=dis", headers=headers, timeout=10)
    except Exception as e:
        return f"Erro de requisição: {e}"

    if response.status_code != 200:
        try:
            html = requests.get(url, headers=headers, timeout=10).text
        except:
            return f"Erro ao acessar o perfil (status {response.status_code})"
        match = re.search(r'(\+?\d{2,4}[-.\s]?\d{4,5}[-.\s]?\d{4})', html)
        return match.group(0) if match else "Nenhum telefone encontrado"

    try:
        data = response.json()
        phone = data.get("graphql", {}).get("user", {}).get("business_phone_number")
        if phone:
            return phone
    except Exception:
        pass

    html = requests.get(url, headers=headers, timeout=10).text
    match = re.search(r'(\+?\d{2,4}[-.\s]?\d{4,5}[-.\s]?\d{4})', html)
    return match.group(0) if match else "Nenhum telefone encontrado"

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Instagram Phone Finder</title>
</head>
<body style="font-family: Arial; text-align:center; margin-top:50px;">
    <h2>🔎 Buscar telefone no Instagram</h2>
    <form method="post">
        <input type="text" name="url" placeholder="Cole a URL do perfil (ex: https://www.instagram.com/nike/ ou @nike)" style="width:360px; padding:8px;">
        <button type="submit">Buscar</button>
    </form>
    {% if phone %}
        <p><b>Resultado:</b> {{ phone }}</p>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    phone = None
    if request.method == "POST":
        url = request.form.get("url", "")
        phone = get_phone_from_instagram(url.strip())
    return render_template_string(HTML_PAGE, phone=phone)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
