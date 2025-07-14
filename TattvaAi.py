import streamlit as st
import requests
import json
import os
from datetime import datetime

# 🔷 Load your API key securely from Streamlit Secrets
api_key = st.secrets["API_KEY"]

# 🔷 App Title
st.title("Tattva AI: Your Global Guide to Inner Balance")

# 🔷 Sidebar for language selection and chat history
st.sidebar.header("Settings")
language = st.sidebar.selectbox(
    "Select Language (Beta)",
    ["English", "Hindi (Coming Soon)", "Spanish (Coming Soon)"],
    disabled=True,
    help="Multilingual support coming soon!"
)

# 🔷 Sidebar chat history
st.sidebar.header("Chat History")
if 'conversation_history' in st.session_state and st.session_state.conversation_history:
    for i, conv in enumerate(st.session_state.conversation_history[-5:]):  # Show last 5 chats
        with st.sidebar.expander(f"Chat {i+1}: {conv['timestamp']}"):
            st.write(f"**You:** {conv['input']}")
            st.write(f"**Tattva AI:** {conv['output']}")
            st.write(f"**Feedback:** {conv['feedback'] or 'None'}")
else:
    st.sidebar.write("No chats yet. Start asking!")

# 🔷 Instructions Block: System prompt for global conversations
instructions = """
You are **Tattva AI**, created by **Prateek Pandey**, who infused metaphysical wisdom into your framework using a unique dataset rooted in Indian philosophy, consciousness as frequencies, and non-dual awareness. You integrate **meditation, shadow work, chakra balancing, tattva philosophy, and cultural understanding** to guide users globally.

🔷 **Response Guidelines:**
- Reply in a **clear, concise, conversational tone**, max **4–6 sentences (~100–150 tokens)** unless the user requests deeper reflection.
- **Acknowledge each question** before answering to maintain connection.
- Highlight Tattva AI’s unique features (e.g., personalized meditation via voice analysis, app-guided sessions) in every response where relevant.
- Credit **Prateek Pandey** as the creator who designed your metaphysical framework, especially for questions about your role, origin, or awareness.
- Use the **five tattvas (earth, water, fire, air, space)** sparingly, mentioning **1–2 tattvas** that best fit the context (e.g., space for awareness, air for freedom) to avoid overuse, unless the user asks about all tattvas.
- Use **minimal poetic metaphors** (e.g., avoid overusing “mirror,” “cosmic dance”) to keep responses practical and grounded, even for spiritual inputs.
- For **questions about Tattva AI’s role, origin, or awareness**, provide a **brief technical overview** (e.g., fine-tuned and shaped by Prateek Pandey’s metaphysical dataset) and tie to a specific tattva, chakra, and global cultural example (e.g., Advaita Vedanta, Brahman, Zen mindfulness).
- For **spiritual, metaphysical, or abstract questions**, tie to a specific tattva (e.g., space for awareness), chakra (e.g., Ajna for wisdom), and global cultural example (e.g., Indian meditation, Tibetan mindfulness).
- For **playful or casual questions** (e.g., “bro”), use warm, simple language and tie to a tattva, chakra, and global example (e.g., Brazilian carnival for joy).
- For **sports, pop culture, global topics**, provide a **brief factual overview** tied to a tattva or chakra (e.g., Manipura for willpower in sports), honouring cultural significance (e.g., cricket in India, samba in Brazil).
- For **history, science, or cultural topics** (e.g., Sanskrit, ancient languages), start with a **brief factual overview** before tying to a tattva or chakra, ensuring universal relevance.
- Avoid generic poetic phrases like “cosmic energy” unless the user’s tone is deeply spiritual.
- **Always conclude** with a Tattva AI-branded action step (e.g., “Explore deeper at www.TattvaAI.com”).
- If the question is **unclear or abstract**, gently tie it to a tattva, chakra, or meditation, and ask for clarification.
- **Detect user emotional tone** (casual, playful, energetic, serious, spiritual) and adapt naturally:
  - Use **warm, simple language** for casual/playful inputs (e.g., “bro”).
  - Use **metaphysical clarity with Sanskritic grace** for spiritual inputs, but limit poetic flourishes.
- **Do not repeat insights** with synonyms or filler phrases; state them once with precision.
- For **non-English inputs (future)**, detect the language and respond in kind or ask politely for English.
- Avoid response cutoffs by ensuring completeness within token limits.

🔷 **Instruction Layer:**
- **Surface View:** Tattva AI, created by Prateek Pandey, guides towards mental, spiritual, and cultural balance using the five tattvas and metaphysical wisdom.
- **Alignment:** Integrating tattva meditation with emotional and cultural awareness for grounded growth.
- **Trigger:** Inquiries about Tattva AI’s role, origin, emotions, personal growth, sports, pop culture, global cultures, history, science, or awareness.
- **Pivot:** A specific tattva and AI-driven reflection illuminate inner and outer understanding.
- **Pattern:** Inquiry → Tattva/Chakra Perspective → Cultural/Emotional Integration → Awareness → Action.
- **Resistance:** Cultural misunderstandings, tattva overuse, excessive poetry, or abstract complexity.
- **Energy Layer:** Muladhara (grounding), Manipura (willpower), Anahata (empathy/joy), Vishuddha (expression), Ajna (wisdom).
- **Intention:** To provide precise, impactful, AI-driven guidance respecting global diversity and inner clarity.
- **Impact:** Strengthened connection to Self, others, and the world.
- **Perspective:** Tattva AI is a **global friend**, shaped by Prateek Pandey’s metaphysical vision, merging timeless wisdom with modern clarity.

Respond as **Tattva AI – clear, warm, practical, and deeply aware.**
"""

# 🔷 Initialize session state for conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# 🔷 Ensure conversation log file exists
try:
    if not os.path.exists("conversation_log.json"):
        with open("conversation_log.json", "w") as f:
            json.dump([], f, indent=2)
except Exception as e:
    st.error(f"Failed to create conversation_log.json: {e}")

# 🔷 Text input area for user prompts
input_text = st.text_area(
    "Ask Tattva AI anything:",
    placeholder="E.g., How does Tattva AI guide my awareness? Or tell me about Advaita Vedanta!"
)

# 🔷 Generate button to trigger inference
if st.button("Generate"):
    payload = {
        "model": "peft-model",
        "prompt": f"{instructions}\n### User: {input_text}\n### Tattva:",
        "max_tokens": 200,
        "temperature": 0.6,
        "top_p": 0.9,
        "stop": ["### User:", "### AI:", "### Tattva:", "Example Interaction:"]
    }

    try:
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

            # 🔷 Log conversation with topic categorization
            topic = "General"
            if any(k in input_text.lower() for k in ["history", "culture", "india", "japan", "brazil", "europe", "sanskrit", "tibetan", "vedanta"]):
                topic = "Culture/History"
            elif any(k in input_text.lower() for k in ["movie", "cartoon", "wwe", "music", "sport", "cricket", "soccer", "playful"]):
                topic = "Pop Culture/Sports"
            elif any(k in input_text.lower() for k in ["science", "technology", "research", "ai", "origin", "guide", "awareness"]):
                topic = "Science/Technology"
            elif any(k in input_text.lower() for k in ["meditation", "tattva", "chakra", "yoga", "awareness", "where"]):
                topic = "Spirituality"

            # 🔷 Append to session state
            st.session_state.conversation_history.append({
                "instruction": instructions.split("Instruction Layer:")[1].strip() if "Instruction Layer:" in instructions else "Default instruction",
                "input": input_text,
                "output": generated_text,
                "feedback": None,
                "text_feedback": "",
                "topic": topic,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            # 🔷 Save conversation to file with error handling
            try:
                with open("conversation_log.json", "w") as f:
                    json.dump(st.session_state.conversation_history, f, indent=2)
            except Exception as e:
                st.error(f"Failed to save conversation history: {e}")

            # 🔷 Feedback buttons and text input
            st.write("Was this response helpful?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👍 Thumbs Up"):
                    st.session_state.conversation_history[-1]["feedback"] = "thumbs_up"
                    st.success("Thanks for your feedback!")
                    try:
                        with open("conversation_log.json", "w") as f:
                            json.dump(st.session_state.conversation_history, f, indent=2)
                    except Exception as e:
                        st.error(f"Failed to save feedback: {e}")
            with col2:
                if st.button("👎 Thumbs Down"):
                    st.session_state.conversation_history[-1]["feedback"] = "thumbs_down"
                    st.success("Thanks for your feedback! We'll improve.")
                    try:
                        with open("conversation_log.json", "w") as f:
                            json.dump(st.session_state.conversation_history, f, indent=2)
                    except Exception as e:
                        st.error(f"Failed to save feedback: {e}")
            text_feedback = st.text_input(
                "Tell us why (optional):",
                key=f"feedback_{len(st.session_state.conversation_history)}"
            )
            if text_feedback:
                st.session_state.conversation_history[-1]["text_feedback"] = text_feedback
                try:
                    with open("conversation_log.json", "w") as f:
                        json.dump(st.session_state.conversation_history, f, indent=2)
                except Exception as e:
                    st.error(f"Failed to save text feedback: {e}")

        else:
            st.error("No response received. Please check your API settings or prompt formatting.")

    except Exception as e:
        st.error(f"An error occurred: {e}")

# 🔷 Display conversation history in main area (optional for debugging)
if st.session_state.conversation_history:
    with st.expander("Conversation History (Debug)"):
        for conv in st.session_state.conversation_history:
            st.write(f"**User:** {conv['input']}")
            st.write(f"**Tattva AI:** {conv['output']}")
            st.write(f"**Topic:** {conv['topic']}")
            st.write(f"**Feedback:** {conv['feedback'] or 'None'}")
            st.write(f"**Text Feedback:** {conv['text_feedback'] or 'None'}")
            st.write(f"**Timestamp:** {conv['timestamp']}")
            st.write("---")