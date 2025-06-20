from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import json
import re

app = Flask(__name__)

def extract_schema_types(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        schema_types = set()

        for script in soup.find_all("script", type="application/ld+json"):
            content = script.string
            if not content:
                continue
            content = re.sub(r'<!--|-->', '', content).strip()
            try:
                data = json.loads(content)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if isinstance(item, dict) and "@type" in item:
                        types = item["@type"]
                        if isinstance(types, list):
                            schema_types.update(types)
                        else:
                            schema_types.add(types)
            except Exception:
                continue

        return sorted(schema_types)

    except Exception as e:
        return [f"Error: {str(e)}"]

@app.route("/", methods=["GET", "POST"])
def index():
    schema_types = []
    url = ""
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if url:
            schema_types = extract_schema_types(url)
    return render_template("index.html", types=schema_types, url=url)

if __name__ == "__main__":
    app.run(debug=True)
