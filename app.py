import streamlit as st
import requests
import json
import pandas as pd
import time

# Function to generate search queries
def generate_search_queries(base_url, topics):
    queries = [f"site:{base_url} {topic.strip()}" for topic in topics]
    return queries

# Function to make search request to Serper API
def serper_search(query, api_key):
    url = "https://google.serper.dev/search"
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    payload = json.dumps({"q": query})
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error: {response.status_code}")
        return None

# Function to analyze URLs with Diffbot
def analyze_with_diffbot(urls, diffbot_token):
    results = []
    for i, url in enumerate(urls):
        if i > 0 and i % 2 == 0:
            st.write("Waiting for 15 seconds to comply with rate limit...")
            time.sleep(15)
        
        api_url = f"https://api.diffbot.com/v3/analyze?url={url}&token={diffbot_token}"
        response = requests.get(api_url)
        if response.status_code == 200:
            results.append(response.json())
        else:
            st.error(f"Diffbot Error: {response.status_code}")
    return results

# Function to save results to Excel
def save_to_excel(data, filename):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    st.success(f"Data saved to {filename}")

# Streamlit app
st.title("Custom Search and Analysis App")

# User inputs
base_url = st.text_input("Enter the base URL (e.g., graphy.com)")
topics = st.text_input("Enter topics to search (comma separated, e.g., locations,delhi,mumbai)")
serper_api_key = st.text_input("Enter your Serper API key", type="password")
diffbot_token = st.text_input("Enter your Diffbot token", type="password")

if st.button("Start Search"):
    if base_url and topics and serper_api_key and diffbot_token:
        topics_list = topics.split(',')
        queries = generate_search_queries(base_url, topics_list)
        
        # Display generated queries
        st.write("Generated Search Queries:")
        for query in queries:
            st.write(query)
        
        # User selects query to start with
        selected_query = st.selectbox("Select a query to start with", queries)
        
        # Make Serper API call
        search_results = serper_search(selected_query, serper_api_key)
        if search_results:
            # Extract first 5 URLs
            urls = [result['link'] for result in search_results['organic'][:5]]
            st.write("First 5 URLs:")
            for url in urls:
                st.write(url)
            
            # Analyze URLs with Diffbot
            analysis_results = analyze_with_diffbot(urls, diffbot_token)
            st.write("Analysis Results:")
            st.json(analysis_results)
            
            # Save results to Excel
            save_to_excel(analysis_results, "analysis_results.xlsx")
    else:
        st.error("Please fill in all the fields.")
