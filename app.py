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
        if i > 0 and i % 4 == 0:
            st.write("Waiting for 15 seconds to comply with rate limit...")
            time.sleep(15)
        
        api_url = f"https://api.diffbot.com/v3/analyze?url={url}&token={diffbot_token}"
        response = requests.get(api_url)
        if response.status_code == 200:
            results.append(response.json())
        else:
            st.error(f"Diffbot Error: {response.status_code}")
    return results

# Function to convert Diffbot JSON to CSV
def convert_json_to_csv(json_data):
    # Extract relevant information from JSON
    data_to_save = []
    for item in json_data:
        if 'objects' in item:
            for obj in item['objects']:
                flat_data = flatten_json(obj)
                data_to_save.append(flat_data)
        else:
            flat_data = flatten_json(item)
            data_to_save.append(flat_data)

    # Convert to DataFrame
    df = pd.DataFrame(data_to_save)
    return df

# Helper function to flatten JSON
def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

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
            
            # Convert JSON to CSV
            df = convert_json_to_csv(analysis_results)
            csv_data = df.to_csv(index=False).encode('utf-8')

            # Provide download button
            st.download_button(
                label="Download data as CSV",
                data=csv_data,
                file_name='analysis_results.csv',
                mime='text/csv',
            )
    else:
        st.error("Please fill in all the fields.")


    
  
