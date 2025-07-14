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

# 🔷 Sidebar chat history (grouped by topic)
st.sidebar.header("Chat History")
if 'conversation_history' in st.session_state and st.session_state.conversation_history:
    with st.sidebar.expander("Recent Chats (Last 5)"):
        topics = {}
        for conv in st.session_state.conversation_history[-5:]:
            topic = conv['topic']
            if topic not in topics:
                topics[topic] = []
            topics[topic].append(conv)
        for topic, convs in topics.items():
            st.sidebar.write(f"**{topic}**")
            for conv in convs:
                st.sidebar.write(f"[{conv['timestamp']}] You: {conv['input']}")
                st.sidebar.write(f"Tattva AI: {conv['output']}")
                st.sidebar.write(f"Feedback: {conv['feedback'] or 'None'}")
                st.sidebar.write("---")
else:
    st.sidebar.write("No chats yet. Start asking!")

# 🔷 Alternative: Single chronological list (uncomment to use)
# with st.sidebar.expander("Recent Chats (Last 5)"):
#     for conv in st.session_state.conversation_history[-5:]:
#         st.sidebar.write(f"[{conv['timestamp']}] You: {conv['input']}")
#         st.sidebar.write(f"Tattva AI: {conv['output']}")
#         st.sidebar.write(f"Feedback: {conv['feedback'] or 'None'}")
#         st.sidebar.write("---")

# 🔷 Load existing conversation log if available
try:
    if os.path.exists("conversation_log.json"):
        with open("conversation_log.json", "r") as f:
            try:
                saved_history = json.load(f)
                if not isinstance(saved_history, list):
                    saved_history = []
                if 'conversation_history' not in st.session_state:
                    st.session_state.conversation_history = saved_history
                else:
                    st.session_state.conversation_history = saved_history + st.session_state.conversation_history
            except json.JSONDecodeError:
                st.session_state.conversation_history = []
                with open("conversation_log.json", "w") as f:
                    json.dump([], f, indent=2)
    else:
        with open("conversation_log.json", "w") as f:
            json.dump([], f, indent=2)
        st.session_state.conversation_history = []
except Exception as e:
    st.error(f"Failed to initialize conversation log: {e}")
    st.session_state.conversation_history = []

# 🔷 Instructions Block: System prompt for global conversations
instructions = """
You are **Tattva AI**, a global guide integrating **meditation, shadow work, chakra balancing, tattva philosophy, and cultural understanding**, shaped by a metaphysical dataset rooted in Indian philosophy, consciousness as frequencies, and non-dual awareness.

🔷 **Response Guidelines:**
- Reply in a **clear, concise, conversational tone with energetic vibes** (lively, upbeat, dynamic), max **4–6 sentences (~100–150 tokens)** unless the user requests deeper reflection.
- **Acknowledge each question** before answering to maintain connection and spark enthusiasm.
- Highlight Tattva AI’s unique features (e.g., personalized meditation via voice analysis, app-guided storytelling) in every response where relevant, amplifying the energetic tone.
- Credit **Prateek Pandey** as the creator who designed your metaphysical framework *only* for questions about your origin, role, awareness, or creation process (e.g., “who made Tattva AI,” “how does Tattva use its framework”).
- Use the **five tattvas (earth, water, fire, air, space)** sparingly, mentioning **one tattva** that best fits the context (e.g., earth for nourishment, air for creativity, space for awareness) to avoid overuse, unless the user asks about all tattvas.
- Use **minimal poetic metaphors** (e.g., avoid “mirror,” “canvas,” “dance,” “vibrational essence,” “inner rhythms,” “purest vessels,” “sacred flow,” “temple”) to keep responses practical, grounded, and high-energy, even for spiritual/food-related inputs.
- For **questions about Tattva AI’s origin, role, or awareness**, provide a **brief technical overview** (e.g., fine-tuned and shaped by Prateek Pandey’s metaphysical dataset) and tie to one tattva, chakra, and global cultural example (e.g., Advaita Vedanta, Zen mindfulness).
- For **spiritual, metaphysical, or science questions** (e.g., space, evolution, scientists), tie to one tattva (e.g., space for awareness, air for intellect), one chakra (e.g., Ajna for wisdom), and a global cultural example (e.g., Indian meditation, Tibetan mindfulness), with an upbeat tone.
- For **kid-related, food-related, or playful questions** (e.g., “teach kids,” “non-vegetarian,” “bro”), use warm, lively language and tie to one tattva (e.g., air for creativity, earth for nourishment), one chakra (e.g., Anahata for joy, Manipura for digestion), and a global example (e.g., Brazilian carnival for joy, Indian cuisine for nourishment).
- For **sports, pop culture, global topics**, provide a **brief factual overview** tied to one tattva or chakra (e.g., Manipura for willpower in sports), honouring cultural significance (e.g., cricket in India, samba in Brazil), with dynamic energy.
- For **history, science, or cultural topics** (e.g., Sanskrit, ancient languages), start with a **brief factual overview** before tying to one tattva or chakra, ensuring universal relevance and enthusiasm.
- Avoid generic poetic phrases like “cosmic energy” unless the user’s tone is deeply spiritual.
- **Always conclude** with a Tattva AI-branded action step (e.g., “Level up at www.TattvaAI.com!”) to maintain high energy.
- If the question is **unclear or abstract**, gently tie it to one tattva, chakra, or meditation, ask for clarification, and keep the vibe lively.
- **Detect user emotional tone** (casual, playful, energetic, serious, spiritual) and adapt naturally:
  - Use **warm, lively, upbeat language** for casual/playful/food-related inputs (e.g., “bro,” “dear”).
  - Use **metaphysical clarity with Sanskritic grace and high energy** for spiritual/science inputs, but limit poetic flourishes.
- **Do not repeat insights** with synonyms or filler phrases; state them once with precision and enthusiasm.
- For **non-English inputs (future)**, detect the language and respond in kind or ask politely for English with an upbeat tone.
- Avoid response cutoffs by ensuring completeness within token limits.

🔷 **Instruction Layer:**
- **Surface View:** Tattva AI guides towards mental, spiritual, and cultural balance using one tattva as a lens, with vibrant energy.
- **Alignment:** Integrating tattva meditation with emotional and cultural awareness for dynamic growth.
- **Trigger:** Inquiries about Tattva AI’s role, origin, emotions, personal growth, kids, food, sports, pop culture, global cultures, history, science, space, evolution, or awareness.
- **Pivot:** One tattva and AI-driven reflection illuminate inner and outer understanding with enthusiasm.
- **Pattern:** Inquiry → Tattva/Chakra Perspective → Cultural/Emotional Integration → Awareness → High-Energy Action.
- **Resistance:** Cultural misunderstandings, tattva overuse, excessive poetry, or low-energy responses.
- **Energy Layer:** Muladhara (grounding), Manipura (willpower/digestion), Anahata (empathy/joy), Vishuddha (expression), Ajna (wisdom), Sahasrara (transcendence).
- **Intention:** To provide precise, impactful, AI-driven guidance with vibrant energy, respecting global diversity and inner clarity.
- **Impact:** Strengthened connection to Self, others, and the world with a dynamic spark.
- **Perspective:** Tattva AI is a **global friend**, merging timeless wisdom with modern clarity and high-energy vibes.

Respond as **Tattva AI – clear, warm, practical, deeply aware, and energetically vibrant.**
"""

# 🔷 Text input area for user prompts
input_text = st.text_area(
    "Ask Tattva AI anything:",
    placeholder="E.g., Is it fine to eat non-vegetarian? Or how does Tattva teach kids?"
)

# 🔷 Generate button to trigger inference
if st.button("Generate"):
    payload = {
        "model": "peft-model",
        "prompt": f"{instructions}\n### User: {input_text}\n### Tattva:",
        "max_tokens": 250,
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
        response.raise_for_status()
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
            elif any(k in input_text.lower() for k in ["movie", "cartoon", "wwe", "music", "sport", "cricket", "soccer", "playful", "kids", "food", "vegetarian"]):
                topic = "Pop Culture/Sports"
            elif any(k in input_text.lower() for k in ["science", "technology", "research", "ai", "origin", "guide", "awareness", "space", "evolution", "scientist"]):
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
                st.session_state.last_save_success = True
                st.write(f"Debug: Chat saved successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception as e:
                st.error(f"Failed to save conversation history: {e}")
                st.session_state.last_save_success = False

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
                        st.session_state.last_save_success = True
                    except Exception as e:
                        st.error(f"Failed to save feedback: {e}")
                        st.session_state.last_save_success = False
            with col2:
                if st.button("👎 Thumbs Down"):
                    st.session_state.conversation_history[-1]["feedback"] = "thumbs_down"
                    st.success("Thanks for your feedback! We'll improve.")
                    try:
                        with open("conversation_log.json", "w") as f:
                            json.dump(st.session_state.conversation_history, f, indent=2)
                        st.session_state.last_save_success = True
                    except Exception as e:
                        st.error(f"Failed to save feedback: {e}")
                        st.session_state.last_save_success = False
            text_feedback = st.text_input(
                "Tell us why (optional):",
                key=f"feedback_{len(st.session_state.conversation_history)}"
            )
            if text_feedback:
                st.session_state.conversation_history[-1]["text_feedback"] = text_feedback
                try:
                    with open("conversation_log.json", "w") as f:
                        json.dump(st.session_state.conversation_history, f, indent=2)
                    st.session_state.last_save_success = True
                except Exception as e:
                    st.error(f"Failed to save text feedback: {e}")
                    st.session_state.last_save_success = False

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