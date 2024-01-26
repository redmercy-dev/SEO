import streamlit as st
from llama_index.agent import OpenAIAssistantAgent
import openai
import os
import requests
from io import BytesIO

# Streamlit layout
st.title("AI Content Wizard")
page = st.sidebar.selectbox("Choose a feature", ["Text Generation", "Image Generation"])

# Common sidebar inputs for API key
api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")

# Function to initialize the agent
def create_agent():
    openai.api_key = api_key
    os.environ["OPENAI_API_KEY"] = api_key
    return OpenAIAssistantAgent.from_new(
        name="Content Wizard",
        instructions="""[Your instructions here]""",
        openai_tools=[{"type": "retrieval"}],
        instructions_prefix="You are an Expert in content creation and SEO, specializing in tailored articles and keyword research",
        files=["Rules.txt"],
        verbose=True,
    )

# Initialize agent if not already done
if api_key and 'agent' not in st.session_state:
    st.session_state.agent = create_agent()

# Initialize conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = ""

if page == "Text Generation":
    if api_key:
        agent = create_agent()

    user_input = st.text_area("Enter your query:", height=150)
    user_example = st.text_area("Provide an example (optional):", height=100)

    # Collecting sidebar inputs
    parameters = {
        "topic": st.sidebar.text_input("Topic:"),
        "language": st.sidebar.text_input("Language:", value="English"),
        "output_format": st.sidebar.selectbox("Output Format:", ["", "Short text", "Long text", "Article", "List"]),
        "output_length": st.sidebar.selectbox("Output Length:", ["", "Short", "Medium", "Long"]),
        "template_type": st.sidebar.selectbox("Template Type:", ["", "Experience", "Personal Struggle", "Common Belief", "Everyone Knows", "Common Mistake"]),
        "post_type": st.sidebar.selectbox("Post Type:", ["", "Expert", "Promotional", "Polarizing", "Empathy", "Freestyle"]),
        "target_audience": st.sidebar.text_input("Target Audience:"),
        "hooks": st.sidebar.text_input("Hooks:"),
        "guidelines": st.sidebar.text_area("Guidelines:", height=100),
        "copywriting_formula": st.sidebar.text_input("Copywriting Formula:"),
        "tone": st.sidebar.selectbox("Select Tone", ["Friendly", "Formal", "Informative", "Casual", "Persuasive"])
    }

    # Sidebar button to execute the generation
    execute_button = st.sidebar.button("Execute")

    # Download conversation history
    save_button = st.sidebar.button("Download Conversation")

    # Execution logic for generating text
    if execute_button:
            response = st.session_state.agent.chat(user_input + " the provided example if present is" + user_example)
            st.session_state.conversation_history += f"User: {user_input}\nAI: {response}\n"
            st.text_area("Output:", response, height=200)
        
    if save_button:
            st.download_button(
                label="Download Conversation",
                data=st.session_state.conversation_history,
                file_name="conversation_history.txt",
                mime="text/plain"
            )
elif page == "Image Generation":
    # Handling Image Generation functionality
    image_prompt = st.text_input("Enter prompt for image generation:")

    # Additional parameters for image generation
    image_style = st.sidebar.selectbox("Image Style", ["Default", "Artistic", "Photorealistic", "Sketch", "Vintage"])
    color_scheme = st.sidebar.multiselect("Color Scheme", ["Default", "Warm", "Cool", "Monochrome", "Vibrant"])
    quality = st.sidebar.selectbox("Quality", ["Standard", "hd"])

    generate_image_button = st.button("Generate Image")

    if generate_image_button and api_key:
        client = openai.OpenAI(api_key=api_key)

        
        response = client.images.generate(
            model="dall-e-3",
            prompt=image_prompt +"The image style if provided is" + str(image_style) + "And the color if provided needs to be"  + str(color_scheme) ,
            size="1024x1024",
            quality=quality.lower(),
            n=1,
        )

        for i in range(len(response.data)):
            image_url = response.data[i].url
            if image_url:
                st.image(image_url, caption=f"Generated Image {i+1}")
                image_response = requests.get(image_url)
                image_bytes = BytesIO(image_response.content)
                st.download_button(
                    label=f"Download Image {i+1}",
                    data=image_bytes,
                    file_name=f"generated_image_{i+1}.png",
                    mime="image/png"
                )


# Custom CSS for styling
st.markdown("""
    <style>
    .stTextInput>div>div>input {
        color: #4B4B4B;
    }
    .stButton>button {
        background-color: #0083B8;
        color: white;
    }
    .st-bb {
        background-color: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    </style>
""", unsafe_allow_html=True)
