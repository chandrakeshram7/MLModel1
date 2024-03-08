from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from fuzzywuzzy import fuzz
import requests
app = Flask(__name__)
CORS(app, methods=['GET', 'POST', 'OPTIONS'])
api_key = '0c8920ac69504b628c83d70f18a87c35'
news_api_url = 'https://newsapi.org/v2/top-headlines'
country_code = 'in' 
express_endpoint = 'https://farm-assist-github-io.vercel.app/news'

# Load the scheme data
schemes_df = pd.read_csv("FarmAssistDataset.csv")
@app.route('/')
def start():
    return "Flask Server is Running"
@app.route('/getschemes', methods=['POST'])
def recommend():
    farmer_profile = request.get_json()
    print("Received farmer profile:", farmer_profile)
    recommended_schemes = []

    for scheme_id, scheme_data in schemes_df.iterrows():
        score = similarity_score(farmer_profile, scheme_data)
        print(f"Scheme ID: {scheme_id}, Similarity Score: {score}")
        if score > 0.5:  # Adjust the threshold as needed
            scheme_name = schemes_df.loc[scheme_id, "scheme_name"] 
            recommended_schemes.append((scheme_id, score, scheme_name))

    # Sort recommendations by descending similarity score
    recommended_schemes.sort(key=lambda x: x[1], reverse=True)

    # Limit recommendations to a specific number
    NUMBER_OF_RECOMMENDATIONS = 3
    recommended_schemes = recommended_schemes[:NUMBER_OF_RECOMMENDATIONS]
    print("Recommended schemes:", recommended_schemes)
    return jsonify({"recommendedSchemes": recommended_schemes})


def similarity_score(farmer_profile, scheme):
    score = 0
    total_score_possible = 0

    for key in farmer_profile:
        if key in scheme:
            total_score_possible += 1

            if farmer_profile[key] == scheme[key]:
                score += 1
            elif key in ["cropName", "region", "district"]:
                partial_match_score = fuzz.token_sort_ratio(farmer_profile[key], scheme[key])
                score += partial_match_score / 100

    normalized_score = score / total_score_possible if total_score_possible > 0 else 0
    return normalized_score


@app.route('/news')
def get_news():
    params = {
        'country': country_code,
        'apiKey': api_key,
    }

    try:
        response = requests.get(news_api_url, params=params)

        if response.status_code == 200:
            news_data = response.json()

            # Send the news data to the Express app
            express_response = requests.post(express_endpoint, json=news_data)

            if express_response.status_code == 200:
                return jsonify(news_data)
            else:
                return jsonify({'error': f'Failed to send news data to Express. Status: {express_response.status_code}'})

        else:
            return jsonify({'error': f'Failed to fetch news data. Status: {response.status_code}'})

    except Exception as e:
        return jsonify({'error': f'Error fetching news data: {str(e)}'})

from app import app
if __name__ == '__main__':
    app.run(debug=True, port=5000)