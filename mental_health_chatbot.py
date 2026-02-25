import google.generativeai as genai
import streamlit as st

# Configure the app page
st.set_page_config(
    page_title="Mental Health Support Chatbot",
    page_icon="🧠",
    layout="centered"
)

# App title and description
st.title("🧠 Mental Health Support Chatbot")
st.markdown("""
A compassionate AI assistant here to listen and provide support.
Remember: This is not a replacement for professional help.
If you're in crisis, please contact your local emergency services.
""")

# Initialize Gemini model
def setup_model():
    try:
        genai.configure(api_key="AIzaSyCOLGjrOYYchyirKsL4KS380sjZv_mChxs")
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Failed to initialize model: {str(e)}")
        return None

model = setup_model()

# Enhanced safety settings
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
]

# System prompt to keep the conversation focused on mental health
SYSTEM_PROMPT = """You are a compassionate mental health support assistant. Your role is to:
1. Listen actively and provide emotional support
2. Help users process their feelings
3. Offer general coping strategies
4. Suggest professional resources when appropriate

You are NOT a licensed therapist and cannot:
- Diagnose conditions
- Provide medical advice
- Replace professional help

Keep responses focused on mental health and emotional wellbeing. If users ask about unrelated topics, gently steer the conversation back to mental health or explain that you specialize in emotional support.

For crisis situations, immediately provide crisis hotline information."""

if "chat" not in st.session_state:
    if model:
        st.session_state.chat = model.start_chat(history=[])
        # Initialize with system prompt
        st.session_state.chat.send_message(SYSTEM_PROMPT)
    else:
        st.session_state.chat = None

# Display chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello, I'm here to listen and provide mental health support. How are you feeling today?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 1.User input
if prompt := st.chat_input("How are you feeling?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 4.Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Add context to keep responses focused
                mental_health_prompt = f"[Mental Health Support Context] {prompt}. Please respond with mental health support in mind."
                
                response = st.session_state.chat.send_message(
                    mental_health_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,  # Slightly less creative for more focused responses
                        top_p=0.9,
                        max_output_tokens=1024  # Keep responses concise
                    ),
                    safety_settings=safety_settings
                )
                
                # Add crisis resources if detecting urgent needs
                response_text = response.text
                if any(word in prompt.lower() for word in ["suicide", "kill myself","die", "end it all", "crisis", "emergency"]):
                    response_text += "\n\nIf you're in crisis, please contact your local emergency services or a crisis hotline immediately. Remember that you're not alone."
                
                message = {"role": "assistant", "content": response_text}
                st.markdown(message["content"])
                st.session_state.messages.append(message)
                
            except Exception as e:
                st.error("I'm having trouble responding. Please try again with a mental health-related concern.")
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "Sorry, I encountered an error. Please try rephrasing your mental health concern."
                })

# streamlit run mental_health_chatbot.py