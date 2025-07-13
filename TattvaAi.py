import streamlit as st
import requests

api_key = st.secrets["API_KEY"]

st.title("Tattva AI Inference")

input_text = st.text_area("Enter your prompt:")

if st.button("Generate"):
    response = requests.post(
        "https://infer.e2enetworks.net/project/p-5067/endpoint/is-5279/v1/completions",
        json={
            "model": "peft-model",
            "prompt": input_text,
            "max_tokens": 512,      # 🔥 allows up to 512 token outputs
            "temperature": 0.7,     # 🔥 balanced creativity
            "top_p": 0.95           # 🔥 nucleus sampling for natural flow
        },
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )
    output = response.json()
    
    # Extract only the generated text
    generated_text = output["choices"][0]["text"]
    
    st.write("**Tattva AI Response:**")
    st.write(generated_text.strip())

