from flask import Flask, render_template, jsonify
import requests
from nltk.tokenize import sent_tokenize
import nltk

# Download the punkt tokenizer data
nltk.download('punkt')

app = Flask(__name__)

# Function to fetch data from the API with pagination
def fetch_data_from_api(base_url):
    page = 1
    all_data = []

    try:
        while True:
            response = requests.get(f"{base_url}?page={page}")
            if response.status_code != 200:
                print(f"Failed to fetch data from page {page}")
                break

            data = response.json()
            if 'data' in data and 'data' in data['data']:
                page_data = data['data']['data']
                if not page_data:
                    break
                all_data.extend(page_data)
            else:
                break

            page += 1
    except Exception as e:
        print(f"Error fetching data: {e}")
    
    return all_data

# Function to find citations for a response
def find_citations(response, sources):
    response_sentences = sent_tokenize(response.lower())
    citations = []

    for source in sources:
        context = source['context']
        if isinstance(context, str):
            context_sentences = sent_tokenize(context.lower())
            if any(sentence in response_sentences for sentence in context_sentences):
                citation = {
                    "id": source['id'],
                    "link": source.get('link', 'N/A')
                }
                citations.append(citation)
    
    return citations

# Function to process the data
def process_data(data):
    results = []
    for item in data:
        response_id = item['id']
        response = item['response']
        sources = item['source']
        citations = find_citations(response, sources)
        result = {
            "id": response_id,
            "response": response,
            "citations": citations
        }
        results.append(result)
    return results

# Route to fetch and display data
@app.route('/')
def index():
    api_base_url = "https://devapi.beyondchats.com/api/get_message_with_sources"
    all_data = fetch_data_from_api(api_base_url)
    results = process_data(all_data) if all_data else []
    return render_template('index.html', results=results)

# Route to fetch data as JSON
@app.route('/api/data')
def data():
    api_base_url = "https://devapi.beyondchats.com/api/get_message_with_sources"
    all_data = fetch_data_from_api(api_base_url)
    results = process_data(all_data) if all_data else []
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
