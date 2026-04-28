import streamlit as st
import requests

st.set_page_config(page_title="Conversation Reflection AI", layout="wide")

API_KEY = "API_KEY = "your_api_key_here"


# ---------- SESSION ----------
st.session_state.setdefault("history", [])
st.session_state.setdefault("current", None)
st.session_state.setdefault("feedback", None)


# ---------- CLEAN ----------
def clean_text(text):
    return text.replace("**", "").strip()


# ---------- SENTIMENT ----------
def get_sentiment(text):
    text = text.lower()

    positive_words = [
        "please","thanks","thank you","kindly","appreciate",
        "happy","great","good","awesome","congrats","well done"
    ]

    negative_words = [
        "idiot","stupid","shut up","do it now","hate","angry","bad"
    ]

    if any(w in text for w in negative_words):
        return "Sentiment: Negative 😠"
    elif any(w in text for w in positive_words):
        return "Sentiment: Positive 😊"
    else:
        return "Sentiment: Neutral 😐"


# ---------- AI ----------
def analyze_conversation(text):

    prompt = f"""
    Analyze in short (1 line each):

    Tone:
    Intent:
    Issues:
    Suggestion:
    Improved Version:

    Message:
    "{text}"
    """

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}]
        }
    )

    data = response.json()
    output = data["choices"][0]["message"]["content"]

    result = {
        "Tone":"","Intent":"","Issues":"",
        "Suggestion":"","Improved Version":""
    }

    for line in output.split("\n"):
        l = line.lower()
        if "tone" in l: result["Tone"] = clean_text(line.split(":",1)[-1])
        elif "intent" in l: result["Intent"] = clean_text(line.split(":",1)[-1])
        elif "issues" in l: result["Issues"] = clean_text(line.split(":",1)[-1])
        elif "suggestion" in l: result["Suggestion"] = clean_text(line.split(":",1)[-1])
        elif "improved" in l: result["Improved Version"] = clean_text(line.split(":",1)[-1])

    return result


# ---------- IMPROVED DYNAMIC TIP ----------
def generate_tip(result, sentiment):

    issues = result.get("Issues", "").lower()
    tone = result.get("Tone", "").lower()

    if "negative" in sentiment.lower():
        return "Your message may sound harsh — try adding polite words like 'please' or 'thanks'."

    elif "unclear" in issues:
        return "Try making your message more specific so the receiver understands it easily."

    elif "short" in issues:
        return "Add a bit more context to avoid confusion."

    elif "rude" in tone or "harsh" in tone:
        return "Soften your tone to make your message sound more professional."

    elif "positive" in sentiment.lower():
        return "Nice! Your message already sounds polite and positive."

    else:
        return "Clear and polite wording always improves communication."


# ---------- STYLE ----------
st.markdown("""
<style>
.block-container { padding-top: 1.5rem; }

.hero {
    background: linear-gradient(135deg, #fde2e4, #fbcfe8);
    padding: 16px;
    border-radius: 14px;
    margin-bottom: 18px;
    text-align:center;
}

section[data-testid="stSidebar"] {
    background: #fff1f2;
}

section[data-testid="stSidebar"] button {
    background: #fbcfe8 !important;
    color: #831843 !important;
    border-radius: 10px !important;
    margin-bottom: 8px !important;
    padding: 6px 10px !important;
}

.card {
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 10px;
    border: 1px solid #e5e7eb;
}

.tone { background:#fde2e4; }
.intent { background:#dbeafe; }
.issues { background:#fef3c7; }
.suggestion { background:#dcfce7; }
.improved { background:#f3e8ff; }

.side-box {
    background:#f9fafb;
    padding:10px;
    border-radius:10px;
    margin-bottom:10px;
}

.sentiment-box {
    background:#e0e7ff;
    padding:10px;
    border-radius:10px;
    text-align:center;
    font-size:13px;
    font-weight:600;
}

.feedback-text {
    font-size:13px;
}
</style>
""", unsafe_allow_html=True)


# ---------- SIDEBAR ----------
with st.sidebar:
    st.title("History")

    for i in range(len(st.session_state.history)):
        item = st.session_state.history[i]

        c1, c2 = st.columns([4,1])

        if c1.button(item["input"][:25], key=f"h{i}"):
            st.session_state.current = item

        if c2.button("✕", key=f"d{i}"):
            st.session_state.history.pop(i)
            st.rerun()


# ---------- HEADER ----------
st.markdown("""
<div class="hero">
<h2>Conversation <span style="color:#ec4899;">Reflection</span> AI</h2>
<p>Understand your message and refine it into something clearer, softer, and more thoughtful.</p>
</div>
""", unsafe_allow_html=True)


# ---------- LAYOUT ----------
left, right = st.columns([2,1])


# ---------- LEFT ----------
with left:

    st.subheader("Draft Your Message")

    user_input = st.text_area(
        "Type your message (e.g.,'Please send the file')",
        height=120
    )

    if st.button("Analyze"):
        if user_input:
            result = analyze_conversation(user_input)
            sentiment = get_sentiment(user_input)

            entry = {
                "input": user_input,
                "output": result,
                "sentiment": sentiment
            }

            st.session_state.current = entry
            st.session_state.history.append(entry)
            st.session_state.feedback = None
            st.rerun()

    if st.session_state.current:
        o = st.session_state.current["output"]

        st.markdown(f"<div class='card tone'><b> Tone</b><br>{o['Tone']}</div>", True)
        st.markdown(f"<div class='card intent'><b> Intent</b><br>{o['Intent']}</div>", True)
        st.markdown(f"<div class='card issues'><b> Issues</b><br>{o['Issues']}</div>", True)
        st.markdown(f"<div class='card suggestion'><b> Suggestion</b><br>{o['Suggestion']}</div>", True)
        st.markdown(f"<div class='card improved'><b> Improved Version</b><br>{o['Improved Version']}</div>", True)


# ---------- RIGHT ----------
with right:

    if st.session_state.current:
        tip = generate_tip(
            st.session_state.current["output"],
            st.session_state.current["sentiment"]
        )
    else:
        tip = "Clear wording improves communication."

    st.markdown(f"<div class='side-box'><b>💡 Tip</b><br>{tip}</div>", True)

    if st.session_state.current:

        st.markdown(f"<div class='sentiment-box'>{st.session_state.current['sentiment']}</div>", True)

        st.markdown("<div class='feedback-text'>Was this helpful?</div>", True)

        c1, c2 = st.columns(2)

        if c1.button("👍 Yes"):
            st.session_state.feedback = "yes"

        if c2.button("👎 No"):
            st.session_state.feedback = "no"

        if st.session_state.feedback == "yes":
            st.success("Thanks for your feedback!")

        if st.session_state.feedback == "no":
            fb = st.text_input("What should we improve?")

            if fb:
                st.success("Thanks! We'll try to improve this ")