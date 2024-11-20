from flask import Flask, jsonify, request
import requests
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# URL API Google Apps Script
API_URL = 'https://script.google.com/macros/s/AKfycbxoDiwnAM-zTBmVOfnKb-Ihx_x-i6KLXPL-HRF--WCDbSkEUorKKbN303nSGtRRZ7nB/exec'

def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        return date_str

def get_books_from_sheets():
    response = requests.get(API_URL)
    if response.status_code == 200:
        books = response.json()['data']
        for index, book in enumerate(books, start=1):
            book['id'] = index
        return books
    else:
        return []

@app.route('/api/books', methods=['GET'])
def get_books():
    books = get_books_from_sheets()
    return jsonify({"message": "Books retrieved successfully", "data": books}), 200


@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    books = get_books_from_sheets()
    book = next((b for b in books if b["id"] == book_id), None)
    if book:
        return jsonify({"message": "Book retrieved successfully", "data": book}), 200
    return jsonify({"message": "Book not found"}), 404

@app.route('/api/books', methods=['POST'])
def add_book():
    data = request.json
    if not all(k in data for k in ('title', 'author', 'published_at')):
        return jsonify({"error": "Missing fields"}), 400
    response = requests.post(API_URL, json={"action": "add", "book": data})
    return response.json(), response.status_code

@app.route('/api/books/<int:id>', methods=['PUT'])
def update_book(id):
    data = request.json
    response = requests.post(API_URL, json={
        "action": "update",
        "book_id": id,
        "updated_book": data
    })
    return response.json(), response.status_code

@app.route('/api/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    response = requests.post(API_URL, json={"action": "delete", "book_id": id})
    return response.json(), response.status_code

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 4000))
    app.run(host="0.0.0.0", port=port)
