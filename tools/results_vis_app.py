import streamlit as st
import matplotlib.pyplot as plt
import json
from result_analysis import analyze_result_messages

st.set_page_config(page_title="Agent Message Visualizer", layout="wide")
st.title("🧠 Agent Team Message History Analyzer")

uploaded_file = st.file_uploader("Upload a JSON list of messages", type="json")
if uploaded_file:
    messages = json.load(uploaded_file)

if messages and isinstance(messages, list):
    analysis = analyze_result_messages(messages)

    st.subheader("📊 Key Stats")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Messages", analysis['total_messages'])
    col2.metric("Prompt Tokens", analysis['total_prompt_tokens'])
    col3.metric("Completion Tokens", analysis['total_completion_tokens'])
    col4.metric("Total Tokens", analysis['total_tokens'])

    st.subheader("📈 Visualizations")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**🔋 Token Usage per Agent**")
        fig1, ax1 = plt.subplots(figsize=(5, 4))
        agents = list(analysis['tokens_per_agent'].keys())
        prompt_tokens = [analysis['tokens_per_agent'][a]['prompt_tokens'] for a in agents]
        completion_tokens = [analysis['tokens_per_agent'][a]['completion_tokens'] for a in agents]

        ax1.bar(agents, prompt_tokens, label="Prompt Tokens")
        ax1.bar(agents, completion_tokens, bottom=prompt_tokens, label="Completion Tokens")
        ax1.set_ylabel("Tokens")
        ax1.set_title("Token Usage by Agent")
        ax1.legend()
        st.pyplot(fig1)

    with col2:
        st.markdown("**📨 Messages per Agent**")
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        ax2.bar(analysis['messages_per_agent'].keys(), analysis['messages_per_agent'].values(), color='orange')
        ax2.set_ylabel("Messages")
        ax2.set_title("Messages per Agent")
        plt.xticks(rotation=45)
        st.pyplot(fig2)

    with col3:
        st.markdown("**📂 Message Types Count**")
        fig3, ax3 = plt.subplots(figsize=(5, 4))
        ax3.bar(analysis['messages_per_type'].keys(), analysis['messages_per_type'].values(), color='skyblue')
        ax3.set_ylabel("Count")
        ax3.set_title("Messages by Type")
        plt.xticks(rotation=45)
        st.pyplot(fig3)

    st.subheader("📜 Raw Message Log")
    for i, msg in enumerate(messages):
        msg_type = msg.get('type', 'unknown') if isinstance(msg, dict) else getattr(msg, 'type', 'unknown')
        source = msg.get('source', 'unknown') if isinstance(msg, dict) else getattr(msg, 'source', 'unknown')
        target = msg.get('target', None) if isinstance(msg, dict) else getattr(msg, 'target', None)
        content = msg.get('content', '') if isinstance(msg, dict) else getattr(msg, 'content', '')

        header = f"**Message {i+1}: {msg_type} from {source}**"
        if target:
            header += f" to {target}"
        st.markdown("---")
        st.markdown(header)
        st.write(content)
        with st.expander(f"Full Message"):
            st.json(msg)

elif messages is not None:
    st.error("Provided data is not a valid list of messages.")