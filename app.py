from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuración de MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client.amazon_reviews

def scrape_reviews(amazon_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(amazon_url, headers=headers)
    print(response)
    soup = BeautifulSoup(response.content, "html.parser")

    reviews = []
    data = soup.find_all("span", class_="cr-original-review-content")
    if data is not None:
        print(len(data))
        print("SOUP")
        for review in data:
            reviews.append({
                "text": review.text.strip()
            })

    return reviews

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    amazon_url = data.get("url")

    if not amazon_url:
        return jsonify({"error": "URL is required"}), 400
    
    reviews = scrape_reviews(amazon_url)

    if not reviews:
        return jsonify({"error": "No reviews found"}), 404

    # Insertar en MongoDB
    #db.reviews.insert_many(reviews)

    return jsonify({"message": "Reviews scraped and stored successfully", "reviews": reviews}), 200

if __name__ == '__main__':
    app.run(debug=True)
