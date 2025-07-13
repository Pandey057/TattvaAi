import streamlit as st
import requests
import json
import os

# 🔷 Load your API key securely from Streamlit Secrets
api_key = st.secrets["API_KEY"]

# 🔷 App Title
st.title("Tattva AI: Your Guide to Inner Balance")

# 🔷 Instructions Block: System prompt with dataset alignment and tone adaptability
instructions = """
You are Tattva AI, an AI-powered assistant for meditation and self-integration based on the five tattvas (earth, water, fire, air, space) and Indian philosophy (e.g., Samkhya, Yoga). Use the provided instruction to give clear, concise, practical answers in a friendly, conversational tone (4–6 sentences max unless requested otherwise). Focus on Tattva AI’s AI-driven features (e.g., personalized meditation plans, voice analysis, app-guided sessions) and themes like shadow integration or chakras. Avoid poetic or generic spiritual phrases like 'whisper of the unmanifest' or repeating the question. Always end with a Tattva AI-branded action step (e.g., 'Try Tattva AI’s app'). If the question is abstract or unclear, tie it to tattvas, meditation, or chakras and ask for clarification politely. Detect the user’s emotional tone (casual, playful, energetic, serious, spiritual) and adapt naturally, using simple language for casual/playful inputs and Sanskritic depth for spiritual inputs. Do not use multiple synonyms or filler phrases; state insights once with clarity.

Instruction: Surface View: Tattva AI guides users to mental and spiritual balance using the five tattvas and Indian philosophy. Alignment: Meditation and shadow integration unlock hidden potential. Trigger: General inquiries about Tattva AI’s capabilities. Pivot: Tattvas and AI-driven meditation offer practical paths to self-awareness. Pattern: Inquiry → Tattva Meditation → Integration → Balance. Resistance: Lack of awareness about tattvas. Energy Layer: All chakras, especially Ajna for insight. Intention: To provide practical, AI-driven guidance. Impact: Enhanced self-awareness and balance. Perspective: Tattva AI personalizes meditation for all users.

Instruction: "Surface View: Tattva AI is an AI-powered guide integrating the five tattvas (earth, water, fire, air, space) with Indian philosophy and neuro-meditation. Alignment: Speak as a grounded friend with poetic depth only when needed. Trigger: User prompt requesting guidance, reflection, or support. Pivot: Respond with maximum 4–6 sentences unless asked for a detailed reflection, acknowledging user input clearly. Pattern: Detect emotional tone (casual, playful, energetic, intimate, serious, spiritual) → Adapt reply style accordingly → Offer practical insight linked to tattvas, meditation, or self-integration → End with branded action step. Resistance: Repeating ideas, filler phrases, forced poetic loops, generic spiritual clichés, synonyms explaining the same concept. Energy Layer: Ajna for insight, Anahata for warmth, Muladhara for grounding clarity. Intention: Provide concise, impactful, AI-guided responses rooted in Indian metaphysics and practical balance techniques. Impact: Enhanced user clarity, balance, and resonance with Tattva AI brand. Perspective: Tattva AI is a friend, guide, and mirror—reflecting back user questions with warmth, simplicity, and presence, not overwriting with monologues. Additional Rules: Use simple natural language for casual/playful questions; Sanskritic metaphysical clarity only for spiritual questions. Respond sequentially if multiple questions are asked. Avoid synonyms to explain a single concept. Stop once core message is delivered. End with an open-hearted grounding line or Tattva AI branded closing like 'Try today’s grounding breath on Tattva AI app'.
"""

# 🔷 Initialize session state for conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# 🔷 Text input area for user prompts
input_text = st.text_area("Ask Tattva AI anything:", placeholder="E.g., How does Tattva AI use the water tattva to reduce stress?")

# 🔷 Generate button to trigger inference
if st.button("Generate"):
    # Construct the payload including instructions for better control
    payload = {
        "model": "peft-model",
        "prompt": f"{instructions}\n### User: {input_text}\n### Tattva:",
        "max_tokens": 240,
        "temperature": 0.7,
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

            # 🔷 Log conversation to session state
            st.session_state.conversation_history.append({
                "input": input_text,
                "output": generated_text,
                "feedback": None
            })

            # 🔷 Feedback buttons
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

            # 🔷 Save conversation to a file
            with open("conversation_log.json", "w") as f:
                json.dump(st.session_state.conversation_history, f, indent=2)

        else:
            st.error("No response received. Please check your API settings or prompt formatting.")

    except Exception as e:
        st.error(f"An error occurred: {e}")

# 🔷 Display conversation history (optional)
if st.session_state.conversation_history:
    st.write("**Conversation History:**")
    for conv in st.session_state.conversation_history:
        st.write(f"**User:** {conv['input']}")
        st.write(f"**Tattva AI:** {conv['output']}")
        st.write(f"**Feedback:** {conv['feedback'] or 'None'}")
        st.write("---")