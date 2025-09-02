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
    # Pega título da página (contém nome público)
    title = soup.title.text if soup.title else ""
    # Bio pública aparece em meta description
    bio_tag = soup.find("meta", attrs={"name": "description"})
    bio = bio_tag["content"] if bio_tag else ""
    
    return {
        "username": username,
        "public_name": title.split("•")[0].strip(),_
