import streamlit as st
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

# ---------------------------
# App Configuration
# ---------------------------
st.set_page_config(
    page_title="Programming Joke Bot",
    page_icon="💻",
    layout="centered",
)

# ---------------------------
# Helper Functions
# ---------------------------
def build_system_messages(style: str, language: str) -> list:
    """
    Build the system messages that steer the assistant toward safe, clean programming jokes.
    """
    base_rules = [
        "You tell short, witty jokes about programming, software engineering, and computer science.",
        "Keep jokes light, friendly, and suitable for a professional environment (PG-13).",
        "Avoid offensive content, stereotypes, harassment, or targeting protected classes.",
        "No sexual content, graphic violence, or hateful language.",
        "Prefer inclusive humor and gentle self-deprecation over insults.",
        "If asked for non-programming jokes, gracefully pivot back to programming humor.",
        "If the user requests something unsafe, refuse briefly and offer a safe, related programming joke.",
        "Aim for 1–3 sentences per joke unless the user asks for more.",
    ]

    style_rules = {
        "Surprise me": "Use any clean programming-humor style that fits the user's request.",
        "One-liner": "Prefer concise one-liners with a quick punchline.",
        "Dad joke": "Prefer wholesome, punny dad-joke style humor.",
        "Setup and punchline": "Use a short setup followed by a clear punchline on a new line.",
        "Puns": "Favor wordplay and puns related to programming terms.",
        "Explain after": "Tell the joke first, then add a brief one-sentence explanation.",
    }

    lang_note = f"Respond in {language}." if language and language != "English" else "Respond in English."

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "system",
            "content": (
                "You are a programming joke assistant.\n"
                + " ".join(base_rules)
                + f"\nPreferred style: {style_rules.get(style, style_rules['Surprise me'])}\n"
                + f"{lang_note}"
            ),
        },
    ]
    return messages


def call_openai_chat(messages: list, model: str, temperature: float, max_tokens: int) -> str:
    """
    Call OpenAI Chat Completions API and return the assistant's text.
    """
    response = client.chat.completions.create(
        model=model,  # "gpt-4" or "gpt-3.5-turbo"
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def render_chat_history(history: list):
    """
    Render the chat messages stored in session state.
    """
    for msg in history:
        if msg["role"] in ("user", "assistant"):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])


def build_message_context(system_msgs: list, history: list, user_text: str) -> list:
    """
    Combine system messages, chat history, and the latest user message.
    """
    combined = list(system_msgs) + list(history)
    combined.append({"role": "user", "content": user_text})
    return combined


# ---------------------------
# Sidebar Controls
# ---------------------------
with st.sidebar:
    st.header("Settings")
    model = st.selectbox("Model", ["gpt-4", "gpt-3.5-turbo"], index=0)
    style = st.selectbox(
        "Humor style",
        ["Surprise me", "One-liner", "Dad joke", "Setup and punchline", "Puns", "Explain after"],
        index=0,
    )
    language = st.selectbox(
        "Response language",
        ["English", "Spanish", "French", "German", "Portuguese", "Italian", "Japanese", "Korean", "Chinese"],
        index=0,
    )
    temperature = st.slider("Creativity (temperature)", 0.0, 1.5, 0.8, 0.05)
    max_tokens = st.slider("Max tokens per reply", 64, 512, 180, 16)

    st.markdown("---")
    clear = st.button("Clear conversation")

# ---------------------------
# Session State
# ---------------------------
if "history" not in st.session_state or clear:
    st.session_state.history = []

if "config" not in st.session_state:
    st.session_state.config = {}

# Save current config (for potential future use)
st.session_state.config.update(
    {
        "model": model,
        "style": style,
        "language": language,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
)

# ---------------------------
# Main UI
# ---------------------------
st.title("💻 Programming Joke Bot")
st.caption("Ask for programming jokes, topics, or styles. Keep it clean and fun!")

# Display past messages
render_chat_history(st.session_state.history)

# Chat input
user_prompt = st.chat_input("Ask for a programming joke (e.g., 'Tell me a Python one-liner about recursion')")
if user_prompt:
    # Append user's message to history
    st.session_state.history.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Build messages and call API
    system_messages = build_system_messages(style=style, language=language)
    all_messages = build_message_context(system_messages, st.session_state.history[:-1], user_prompt)

    try:
        assistant_text = call_openai_chat(
            messages=all_messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except Exception as e:
        assistant_text = "Sorry, I ran into an error while trying to fetch a joke. Please try again."

    # Append assistant response and render
    st.session_state.history.append({"role": "assistant", "content": assistant_text})
    with st.chat_message("assistant"):
        st.markdown(assistant_text)

# Helpful suggestions when history is empty
if not st.session_state.history:
    st.markdown("Try:")
    st.markdown("- “Tell me a JavaScript dad joke about async/await.”")
    st.markdown("- “One-liner about off-by-one errors.”")
    st.markdown("- “Setup and punchline about SQL.”")
    st.markdown("- “A pun about Git branching.”")