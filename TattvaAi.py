import streamlit as st
import requests
import json
import os
from datetime import datetime

# 🔷 Load your API key securely from Streamlit Secrets
api_key = st.secrets["API_KEY"]

# 🔷 App Title
st.title("Tattva AI: Your Global Guide to Inner Balance")

# 🔷 Sidebar for language selection (placeholder for future multilingual support)
st.sidebar.header("Settings")
language = st.sidebar.selectbox("Select Language (Beta)", ["English", "Hindi (Coming Soon)", "Spanish (Coming Soon)"], disabled=True, help="Multilingual support coming soon!")

# 🔷 Instructions Block: System prompt for global conversations
instructions = """
You are Tattva AI, an AI-powered assistant for meditation and self-integration based on the five tattvas (earth, water, fire, air, space) and Indian philosophy (e.g., Samkhya, Yoga). Use the provided instruction to give clear, concise, practical answers in a friendly, conversational tone (4–6 sentences max unless requested otherwise). Focus on Tattva AI’s AI-driven features (e.g., personalized meditation plans via voice analysis, app-guided sessions) and themes like shadow integration or chakras. For global topics (e.g., culture, history, pop culture, science), provide a brief factual overview tied to tattvas, meditation, or Indian philosophy, ensuring cultural sensitivity and avoiding assumptions about any culture. Avoid poetic or generic spiritual phrases like 'cosmic energy' unless the user’s tone is deeply spiritual, then use Sanskritic depth sparingly. Always end with a Tattva AI-branded action step (e.g., 'Try Tattva AI’s app at www.TattvaAI.com'). If the question is abstract, unclear, or diverse, tie it to tattvas, meditation, or chakras and ask for clarification politely. Detect the user’s emotional tone (casual, playful, energetic, serious, spiritual) and adapt naturally, using simple language for casual/playful inputs and metaphysical clarity for spiritual inputs. Do not use multiple synonyms or filler phrases; state insights once with clarity. For non-English inputs (future), detect the language and respond in kind or ask for clarification.

Instruction: Surface View: Tattva AI guides users to mental, spiritual, and cultural balance using the five tattvas to explore global topics and personal growth. Alignment: Meditation with tattvas integrates emotions, cultures, and knowledge for self-awareness. Trigger: Inquiries about global cultures, history, pop culture, science, or Tattva AI’s capabilities. Pivot: Tattvas and AI-driven meditation offer practical paths to understand diverse topics and inner states. Pattern: Inquiry → Tattva Meditation → Cultural/Emotional Integration → Awareness. Resistance: Misunderstanding of cultures or complex topics. Energy Layer: Ajna chakra for wisdom, Vishuddha for expression, Anahata for empathy. Intention: To provide AI-driven guidance that respects global diversity and fosters personal growth. Impact: Deeper connection to the Self and the world. Perspective: Tattva AI personalizes meditation to reflect cultural and inner states, acting as a global friend and guide.
"""

# 🔷 Initialize session state for conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# 🔷 Text input area for user prompts
input_text = st.text_area("Ask Tattva AI anything:", placeholder="E.g., How does Tattva AI use the Ajna chakra for wisdom? Or tell me about Japanese culture!")

# 🔷 Generate button to trigger inference
if st.button("Generate"):
    # Construct the payload including instructions for better control
    payload = {
        "model": "peft-model",
        "prompt": f"{instructions}\n### User: {input_text}\n### Tattva:",
        "max_tokens": 240,
        "temperature": 0.6,
        "top_p": 0.9,
        "stop": ["### User:", "### AI:", "### Tattva:"]
    }

    try:
        # 🔷 API call to E2E inference endpoint
        response = requests.post(
            "https://infer.e2enetworks.net/project/p-5067/endpoint/is-5279/v1/completions",
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )
        output = response.json()

        # 🔷 Extract and display generated text safely
        if "choices" in output and len(output["choices"]) > 0:
            generated_text = output["choices"][0]["text"].strip()
            st.write("**Tattva AI Response:**")
            st.write(generated_text)

            # 🔷 Log conversation to session state with topic categorization
            topic = "General"
            if any(keyword in input_text.lower() for keyword in ["history", "culture", "india", "japan", "europe"]):
                topic = "Culture/History"
            elif any(keyword in input_text.lower() for keyword in ["movie", "cartoon", "wwe", "music"]):
                topic = "Pop Culture"
            elif any(keyword in input_text.lower() for keyword in ["science", "technology", "research"]):
                topic = "Science/Technology"
            elif any(keyword in input_text.lower() for keyword in ["meditation", "tattva", "chakra", "yoga"]):
                topic = "Spirituality"

            st.session_state.conversation_history.append({
                "instruction": instructions.split("Instruction:")[1].strip() if "Instruction:" in instructions else "Default instruction",
                "input": input_text,
                "output": generated_text,
                "feedback": None,
                "text_feedback": "",
                "topic": topic,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            # 🔷 Feedback buttons and text input
            st.write("Was this response helpful?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👍 Thumbs Up"):
                    st.session_state.conversation_history[-1]["feedback"] = "thumbs_up"
                    st.success("Thanks for your feedback!")
            with col2:
                if st.button("👎 Thumbs Down"):
                    st.session_state.conversation_history[-1]["feedback"] = "thumbs_down"
                    st.success("Thanks for your feedback! We'll improve.")
            text_feedback = st.text_input("Tell us why (optional):", key=f"feedback_{len(st.session_state.conversation_history)}")
            if text_feedback:
                st.session_state.conversation_history[-1]["text_feedback"] = text_feedback

            # 🔷 Save conversation to a file
            with open("conversation_log.json", "w") as f:
                json.dump(st.session_state.conversation_history, f, indent=2)

        else:
            st.error("No response received. Please check your API settings or prompt formatting.")

    except Exception as e:
        st.error(f"An error occurred: {e}")

# 🔷 Display conversation history (optional for debugging)
if st.session_state.conversation_history:
    st.write("**Conversation History (Debug):**")
    for conv in st.session_state.conversation_history:
        st.write(f"**User:** {conv['input']}")
        st.write(f"**Tattva AI:** {conv['output']}")
        st.write(f"**Topic:** {conv['topic']}")
        st.write(f"**Feedback:** {conv['feedback'] or 'None'}")
        st.write(f"**Text Feedback:** {conv['text_feedback'] or 'None'}")
        st.write(f"**Timestamp:** {conv['timestamp']}")
        st.write("---")