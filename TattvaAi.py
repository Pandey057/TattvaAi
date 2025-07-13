 import streamlit as st
 import requests

 st.title("Tattva AI Inference")

 input_text = st.text_area("Enter your prompt:")

 if st.button("Generate"):
    response = requests.post(
        "https://infer.e2enetworks.net/project/p-5067/endpoint/is-5279/",
        json={"input": input_text}
        # If your endpoint needs headers or API key, add headers={"Authorization": "..."}
    )
    output = response.json()
    st.write(output)
