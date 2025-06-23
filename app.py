from flask import Flask, request, render_template
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import json

app = Flask(__name__)

def detect_jsonld_dynamic(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        jsonld_blocks = soup.find_all('script', type='application/ld+json')

        result = []
        for block in jsonld_blocks:
            if block.string:
                raw_json = block.string.strip()
                try:
                    parsed = json.loads(raw_json)
                    if isinstance(parsed, list):
                        schema_types = ', '.join(item.get('@type', 'Unknown') for item in parsed if isinstance(item, dict))
                    else:
                        schema_types = parsed.get('@type', 'Unknown')
                except json.JSONDecodeError:
                    schema_types = 'Invalid JSON'
                result.append({
                    'type': schema_types,
                    'content': raw_json
                })

        if result:
            return f"Found {len(result)} JSON-LD schema block(s).", result
        else:
            return "No JSON-LD schema found on the page.", []
    except Exception as e:
        return f"Error: {e}", []
    finally:
        driver.quit()

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    blocks = []

    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            message, blocks = detect_jsonld_dynamic(url)
        else:
            message = "Please enter a valid URL."

    return render_template('index.html', message=message, blocks=blocks)

if __name__ == '__main__':
    app.run(debug=True)
