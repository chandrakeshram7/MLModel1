from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from fuzzywuzzy import fuzz
import numpy as np


app = Flask(__name__)
CORS(app, methods=['GET', 'POST', 'OPTIONS'])


# Load the scheme data
schemes_df = pd.read_csv("LastDataset.csv") 
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
        if score > 4:
            scheme_name = schemes_df.loc[scheme_id, "Scheme "]  
            scheme_link= schemes_df.loc[scheme_id, "Link"]
            recommended_schemes.append((scheme_id, score, scheme_name, scheme_link))

    # Sort recommendations by descending similarity score
    recommended_schemes.sort(key=lambda x: x[1], reverse=True)
    NUMBER_OF_RECOMMENDATIONS=5
    # Limit recommendations to a specific number
    recommended_schemes = recommended_schemes[:NUMBER_OF_RECOMMENDATIONS]


    print("Recommended schemes:", recommended_schemes)
    return jsonify({"recommendedSchemes": recommended_schemes})

def similarity_score(farmer_profile, scheme):
    score = 0
    for key in farmer_profile:
        if key in scheme and farmer_profile[key] == scheme[key]:
            score += 1  # Increment score for exact matches

    

    return score


# def recommend():
#     farmer_profile = request.get_json()
#     print("Received farmer profile:", farmer_profile)
#     recommended_schemes = []

#     for scheme_id, scheme_data in schemes_df.iterrows():
#         score = similarity_score(farmer_profile, scheme_data)
#         print(f"Scheme ID: {scheme_id}, Similarity Score: {score}")
#         if score > 0.5:  # Adjust the threshold as needed
#             scheme_name = schemes_df.loc[scheme_id, "scheme_name"] 
#             recommended_schemes.append((scheme_id, score, scheme_name))

#     # Sort recommendations by descending similarity score
#     recommended_schemes.sort(key=lambda x: x[1], reverse=True)

#     # Limit recommendations to a specific number
#     NUMBER_OF_RECOMMENDATIONS = 3
#     recommended_schemes = recommended_schemes[:NUMBER_OF_RECOMMENDATIONS]
#     print("Recommended schemes:", recommended_schemes)
#     return jsonify({"recommendedSchemes": recommended_schemes})


# def similarity_score(farmer_profile, scheme):
#     score = 0
#     total_score_possible = 0

#     for key in farmer_profile:
#         if key in scheme:
#             total_score_possible += 1

#             if farmer_profile[key] == scheme[key]:
#                 score += 1
#             elif key in ["cropName", "region", "district"]:
#                 partial_match_score = fuzz.token_sort_ratio(farmer_profile[key], scheme[key])
#                 score += partial_match_score / 100

#     normalized_score = score / total_score_possible if total_score_possible > 0 else 0
#     return normalized_score


