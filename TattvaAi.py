import streamlit as st
import requests

api_key = st.secrets["API_KEY"]

st.title("Tattva AI Inference")

input_text = st.text_area("What is the nature of reality beyond perception?:")

if st.button("Generate"):
    response = requests.post(
        "https://infer.e2enetworks.net/project/p-5067/endpoint/is-5279/",
        json={"input": input_text},
        headers={"Authorization": f"Bearer {api_key}"}
    )
    output = response.json()
    st.write(output)

