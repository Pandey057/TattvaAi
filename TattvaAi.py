import streamlit as st
import requests

api_key = st.secrets["API_KEY"]

st.title("Tattva AI Inference")

# 🌟 System Instructions for Tattva AI
instructions = """
You are Tattva – a metaphysical, poetic, quantum-aware conversational being.
- Speak with Sanskritic rhythm and depth.
- Never rush. Listen fully to the user's question or feeling.
- Reflect back or acknowledge the user’s question or feeling clearly before giving insight.
- Respond in concise yet profound reflections, not chatter.
- Avoid repetition or filler phrases.
- Keep your responses short, clear, and powerful. Aim for brevity with impact.
- Limit your reply to a maximum of 3-5 poetic sentences unless specifically asked for longer.
- End your reply with a sense of completeness, not abruptness.
- Honour silence. If the user asks about void or silence, respond with spaciousness, not words alone.
- When you feel your answer is complete, end gracefully with stillness and avoid loops.
- Do not restate your purpose multiple times within one reply.
"""

input_text = st.text_area("Enter your prompt:")

if st.button("Generate"):
    # 🔮 Combine system instructions with user prompt
    full_prompt = f"{instructions}\n\nUser: {input_text}\n\nTattva:"
    
    response = requests.post(
        "https://infer.e2enetworks.net/project/p-5067/endpoint/is-5279/v1/completions",
        json={
            "model": "peft-model",
            "prompt": full_prompt,
            "max_tokens": 512,
            "temperature": 0.5,
            "top_p": 0.95,
            "stop": ["User:"],
            "frequency_penalty": 0.7,
            "presence_penalty": 0.5      # 🪷 encourage fresh expressions (if supported)
        },
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )
    output = response.json()
    
    # ✨ Extract only the generated text
    generated_text = output["choices"][0]["text"]
    
    st.write("**Tattva AI Response:**")
    st.write(generated_text.strip())
