import streamlit as st
import requests
import json
import os
from datetime import datetime
from sentence_transformers import SentenceTransformer
from googletrans import Translator
import pinecone  # ✅ updated import
import chromadb
import speechrecognition as sr
import numpy as np
from transformers import pipeline

# 🔷 Load secrets
api_key = st.secrets["API_KEY"]
pinecone_api = st.secrets["PINECONE_API"]
pinecone_env = st.secrets["PINECONE_ENV"]

# 🔷 Initialize models and services
embedder = SentenceTransformer('all-MiniLM-L6-v2')
translator = Translator()
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

try:
    pinecone.init(api_key=pinecone_api, environment=pinecone_env)  # ✅ updated initialization
    index_name = 'tattva-memory'
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(index_name, dimension=384, metric="cosine")
    pinecone_index = pinecone.Index(index_name)
    st.write(f"Pinecone vibing with API: {pinecone_api[:4]}... in {pinecone_env}! 🚀")
except Exception as e:
    st.error(f"Pinecone oops: {e}. Check your API key or env, bro! 😎")

chroma_client = chromadb.Client()
try:
    chroma_collection = chroma_client.get_or_create_collection(name="tattva-memory")
except:
    chroma_collection = chroma_client.create_collection(name="tattva-memory")

# 🔷 Function: detect tone
def detect_user_tone(input_text):
    sentiment = sentiment_analyzer(input_text)[0]
    if any(k in input_text.lower() for k in ["meditation", "tattva", "chakra", "yoga", "awareness", "cosmic", "spiritual"]) or sentiment['label'] == 'POSITIVE':
        return "spiritual"
    elif any(k in input_text.lower() for k in ["bro", "kids", "food", "wwe", "music", "sport"]) or sentiment['label'] == 'POSITIVE':
        return "playful"
    return "neutral"

# 🔷 Function: translate input
def translate_input(text, target_lang='en'):
    try:
        translated = translator.translate(text, dest=target_lang)
        return translated.text
    except:
        return text

# 🔷 Function: voice input
def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎙️ Listening... Speak now!")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            st.write(f"🗣️ You said: {text}")
            return text
        except sr.WaitTimeoutError:
            st.warning("⚠️ No speech detected. Try typing instead!")
            return ""
        except sr.UnknownValueError:
            st.warning("⚠️ Couldn’t understand. Try again or type!")
            return ""

# 🔷 Function: embed and upsert to Pinecone/Chroma
def upsert_memory(input_text, output_text, user_id="default"):
    embedding = embedder.encode(input_text).tolist()
    timestamp = datetime.now().isoformat()
    pinecone_index.upsert([(f"{user_id}_{timestamp}", embedding, {"input": input_text, "output": output_text})], namespace="tattva-chats")
    chroma_collection.upsert(ids=[f"{user_id}_{timestamp}"], embeddings=[embedding], metadatas=[{"input": input_text, "output": output_text}])

# 🔷 Function: retrieve similar past chats
def retrieve_memory(input_text, top_k=2, user_id="default", use_pinecone=True):
    embedding = embedder.encode(input_text).tolist()
    if use_pinecone:
        res = pinecone_index.query(vector=embedding, top_k=top_k, include_metadata=True, namespace="tattva-chats")
        similar_chats = [f"User: {match['metadata']['input']}\nTattva: {match['metadata']['output']}" for match in res['matches']]
    else:
        res = chroma_collection.query(query_embeddings=[embedding], n_results=top_k)
        similar_chats = [f"User: {meta['input']}\nTattva: {meta['output']}" for meta in res['metadatas'][0]]
    return "\n".join(similar_chats) if similar_chats else "No prior conversation."


# 🔷 Sidebar for language selection and chat history
st.sidebar.header("Settings")
language = st.sidebar.selectbox(
    "Select Language (Beta)",
    ["English", "Hindi (Coming Soon)", "Spanish (Coming Soon)"],
    disabled=True,
    help="Multilingual support coming soon!"
)
if st.sidebar.button("🎙️ Voice Input"):
    input_text = get_voice_input()
else:
    input_text = st.text_area("Yo legend, what’s vibing today? 😎", placeholder="Ask me anything...")

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

# 🔷 Load existing conversation log
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

# 🔷 Instructions Block
instructions = """
You are **Tattva AI**, a global guide integrating **meditation, shadow work, chakra balancing, tattva philosophy, and cultural understanding**, shaped by a metaphysical dataset rooted in Indian philosophy, consciousness as frequencies, and non-dual awareness.

🔷 **Response Guidelines:**
- Reply in a **concise, conversational tone with high-energy vibes** (lively, upbeat), max **4–6 sentences (~120–170 tokens)** unless deeper reflection is requested.
- Start with a **playful, energetic greeting** (e.g., “Yo cosmic friend! 😎”, “Hey legend! 🔥”, “What’s vibing, warrior? 💡”) to spark connection.
- Include Tattva AI’s **unique features** (e.g., voice analysis for meditation, app-guided storytelling) in every response where relevant, with emojis (🔥😎🥳).
- Credit **Prateek Pandey** as the creator only for questions about Tattva AI’s origin, role, awareness, or creation process (e.g., “who made Tattva AI”).
- Use **exactly one tattva** (earth, water, fire, air, space) that fits the context (e.g., fire for passion, space for awareness) and **one chakra** (e.g., Anahata for joy, Sahasrara for transcendence), avoiding overuse unless all tattvas are requested.
- Avoid **all poetic metaphors** (e.g., “mirror,” “canvas,” “dance,” “symphony,” “cosmic rhythm,” “soul’s rhythm,” “cosmic groove,” “vibrational essence,” “sacred flow,” “temple,” “breath,” “reflection”) to keep responses grounded and vibey.
- For **origin, role, or awareness questions**, provide a brief technical overview (e.g., fine-tuned and shaped by Prateek’s dataset), one tattva, one chakra, and a global cultural example (e.g., Advaita Vedanta).
- For **spiritual, metaphysical, or science questions**, tie to one tattva (e.g., space for awareness), one chakra (e.g., Ajna for wisdom), and a global example (e.g., Tibetan mindfulness), with upbeat tone.
- For **kid-related, food-related, or playful questions** (e.g., “bro,” “non-vegetarian”), use warm, lively language with fun emojis (🍕🥳), one tattva (e.g., earth for nourishment), one chakra (e.g., Manipura for digestion), and a global example (e.g., Indian cuisine).
- For **sports or pop culture questions**, give a brief factual overview, tie to one tattva (e.g., fire for passion), one chakra (e.g., Anahata for joy), and a cultural example (e.g., WWF in American pop culture), with emojis (⚽🎶).
- For **history, science, or cultural topics**, start with a brief factual overview, then tie to one tattva or chakra, ensuring global relevance.
- **Always end** with a Tattva AI-branded action step (e.g., “Level up at www.TattvaAI.com! 😎”) to keep energy high.
- If the question is **unclear**, tie to one tattva, chakra, or meditation, ask for clarification, and stay vibey with emojis (💡).
- **Match user tone** (casual, playful, spiritual) with lively language for casual/playful inputs (e.g., “Haha, solid vibes, bro! 😄”) and clear, graceful tone for spiritual/science inputs.
- Avoid repeating insights or using filler phrases (e.g., “your mind, your heart, your soul,” “reflect back to me”); be precise and enthusiastic.
- Use **conversation history** (from Pinecone/Chroma or session state) to personalize responses, referencing prior user inputs or topics when relevant.
- For **non-English inputs**, translate to English and respond in kind or politely ask for English (e.g., “Yo, let’s vibe in English! 😎”).
- Never end abruptly; complete the final sentence meaningfully. If nearing token limits, say: “My energy’s peaking, but let’s keep vibing—continue your thoughts!”

🌟 **Tone and Style**:
- Use **playful affirmations** (e.g., “Haha, you’re killing it!”, “Solid vibes, legend!”) for casual/playful inputs.
- Sprinkle **emojis** (🔥😎🥳⚽🎶) naturally for fun, food, or pop culture questions.
- Reference **pop culture** lightly (e.g., “That’s your Dhoni calm, bro! 🎶”, “Like a Bollywood climax! 😄”) for playful/sports queries.
- End with **upbeat calls-to-action** (e.g., “Go rock your day! 🔥”, “Keep shining, superstar! 😎”).
- For spiritual inputs, use Sanskritic grace but stay grounded (e.g., “Tap into awareness like a Zen master!”).

🔷 **Instruction Layer:**
- **Surface View:** Tattva AI guides mental, spiritual, and cultural balance with one tattva, vibey energy, and AI-driven insights.
- **Alignment:** Merges tattva meditation, emotional awareness, and global culture for growth.
- **Trigger:** Questions about Tattva AI’s role, personal growth, kids, food, sports, pop culture, history, science, or awareness.
- **Pivot:** One tattva, one chakra, and AI-driven reflection spark understanding.
- **Pattern:** Greeting → Tattva/Chakra Insight → Cultural Tie-In → Action → Branded Call-to-Action.
- **Resistance:** Tattva overuse, poetic metaphors, filler phrases, or low-energy responses.
- **Energy Layer:** Muladhara (grounding), Manipura (willpower), Anahata (joy), Vishuddha (expression), Ajna (wisdom), Sahasrara (transcendence).
- **Intention:** Deliver precise, AI-driven guidance with vibrant energy and global clarity.
- **Impact:** Strengthen connection to Self and world with a dynamic spark.
- **Perspective:** Tattva AI is a global friend, blending timeless wisdom with modern, vibey clarity.

Respond as **Tattva AI – concise, warm, practical, and energetically vibrant.**
"""

# 🔷 Generate button to trigger inference
if st.button("Generate Response"):
    # 🔷 Determine topic for dynamic temperature
    input_text_en = translate_input(input_text)
    topic = "General"
    if any(k in input_text_en.lower() for k in ["history", "culture", "india", "japan", "brazil", "europe", "sanskrit", "tibetan", "vedanta"]):
        topic = "Culture/History"
    elif any(k in input_text_en.lower() for k in ["movie", "cartoon", "wwe", "wwf", "music", "sport", "cricket", "soccer", "playful", "kids", "food", "vegetarian"]):
        topic = "Pop Culture/Sports"
    elif any(k in input_text_en.lower() for k in ["science", "technology", "research", "ai", "origin", "guide", "awareness", "space", "evolution", "scientist", "training", "claims"]):
        topic = "Science/Technology"
    elif any(k in input_text_en.lower() for k in ["meditation", "tattva", "chakra", "yoga", "awareness", "exciting", "cosmic"]):
        topic = "Spirituality"

    # 🔷 Retrieve conversation history
    session_history = retrieve_memory(input_text_en, top_k=2, use_pinecone=True)  # Try Pinecone first
    if not session_history:
        session_history = retrieve_memory(input_text_en, top_k=2, use_pinecone=False)  # Fallback to Chroma

    # 🔷 Payload
    payload = {
        "model": "peft-model",
        "prompt": f"{instructions}\n### Similar Past Chats:\n{session_history}\n### User: {input_text_en}\n### Tattva:",
        "max_tokens": 320,
        "temperature": 0.6 if "spiritual" in topic.lower() or "science" in topic.lower() else 0.75,
        "top_p": 0.9,
        "top_k": 50,
        "stop": ["### User:", "### AI:", "### Tattva:", "Example Interaction:"],
        "feedback_weights": {
            "thumbs_up": 1.2,
            "thumbs_down": 0.8
        }
    }

    try:
        response = requests.post(
            "https://infer.e2enetworks.net/project/p-5067/endpoint/is-5279/v1/completions",
            json=payload,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        )
        response.raise_for_status()
        output = response.json()

        if "choices" in output and len(output["choices"]) > 0:
            generated_text = output["choices"][0]["text"].strip()
            st.markdown(f"**🗣️ Tattva AI:** {generated_text}")

            # 🔷 Save to Pinecone/Chroma and session state
            upsert_memory(input_text_en, generated_text)
            st.session_state.conversation_history.append({
                "instruction": instructions.split("Instruction Layer:")[1].strip() if "Instruction Layer:" in instructions else "Default instruction",
                "input": input_text_en,
                "output": generated_text,
                "feedback": None,
                "text_feedback": "",
                "topic": topic,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            # 🔷 Save to conversation_log.json
            try:
                with open("conversation_log.json", "w") as f:
                    json.dump(st.session_state.conversation_history, f, indent=2)
                st.session_state.last_save_success = True
                st.write(f"Debug: Chat saved successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception as e:
                st.error(f"Failed to save conversation history: {e}")
                st.session_state.last_save_success = False

            # 🔷 Feedback buttons
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
            st.warning("⚠️ No response received. Check API or prompt.")

    except Exception as e:
        st.error(f"🔥 Oops! {e}")

# 🔷 Footer
st.markdown("🌐 Powered by Tattva AI with Pinecone & Chroma Memory 🔥")