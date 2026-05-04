# chat_page.py
import streamlit as st
from ai_chat_client import ai_chat_client

# 页面配置
st.set_page_config(
    page_title="AI职业顾问 - 智能对话",
    page_icon="💬",
    layout="wide"
)

# 自定义样式
st.markdown("""
<style>
    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        text-align: center;
    }
    .chat-header h1 {
        margin: 0;
        font-size: 28px;
    }
    .chat-header p {
        margin: 10px 0 0;
        opacity: 0.9;
    }
    .message-user {
        text-align: right;
        margin: 15px 0;
    }
    .message-user span {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 10px 16px;
        border-radius: 20px;
        display: inline-block;
        max-width: 70%;
        word-wrap: break-word;
        font-size: 14px;
    }
    .message-assistant {
        text-align: left;
        margin: 15px 0;
    }
    .message-assistant span {
        background: #f0f2f6;
        color: #333;
        padding: 10px 16px;
        border-radius: 20px;
        display: inline-block;
        max-width: 70%;
        word-wrap: break-word;
        font-size: 14px;
    }
    .quick-buttons {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
        flex-wrap: wrap;
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

# 标题（不需要返回按钮了）
st.markdown("""
<div class="chat-header">
    <h1>🤖 AI职业顾问</h1>
    <p>你的专属职业规划助手，随时为你解答问题</p>
</div>
""", unsafe_allow_html=True)

# 初始化聊天历史
if 'chat_page_messages' not in st.session_state:
    st.session_state['chat_page_messages'] = [
        {"role": "assistant", "content": "你好！我是你的AI职业顾问 👋\n\n我可以帮你解答：\n• 职业规划问题\n• 面试准备技巧\n• 技能提升建议\n• 岗位选择咨询\n\n有什么我可以帮你的吗？"}
    ]

# 显示消息区域
messages_container = st.container()
with messages_container:
    for msg in st.session_state['chat_page_messages']:
        if msg['role'] == 'user':
            st.markdown(f"""
            <div class="message-user">
                <span>{msg['content']}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message-assistant">
                <span>{msg['content']}</span>
            </div>
            """, unsafe_allow_html=True)

# 快捷问题
st.markdown("---")
st.markdown('<div class="quick-buttons">', unsafe_allow_html=True)
cols = st.columns(4)
quick_questions = [
    ("🎯 面试准备", "如何准备面试？"),
    ("📚 技能提升", "怎样提升专业技能？"),
    ("📈 岗位前景", "这个岗位前景怎么样？"),
    ("🗺️ 职业规划", "帮我做职业规划")
]

for col, (label, question) in zip(cols, quick_questions):
    with col:
        if st.button(label, key=f"chat_q_{label}", use_container_width=True):
            st.session_state['chat_page_messages'].append({"role": "user", "content": question})
            with st.spinner("AI思考中..."):
                profile = st.session_state.get('student_profile', None)
                response = ai_chat_client.get_answer(question, profile)
                st.session_state['chat_page_messages'].append({"role": "assistant", "content": response})
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# 输入区域
st.markdown("---")
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input("", placeholder="输入你的问题...", key="chat_page_input", label_visibility="collapsed")
with col2:
    send_clicked = st.button("发送", key="chat_page_send", use_container_width=True, type="primary")

if send_clicked and user_input:
    st.session_state['chat_page_messages'].append({"role": "user", "content": user_input})
    with st.spinner("AI思考中..."):
        profile = st.session_state.get('student_profile', None)
        response = ai_chat_client.get_answer(user_input, profile)
        st.session_state['chat_page_messages'].append({"role": "assistant", "content": response})
    st.rerun()

# 清空按钮
if st.button("🗑️ 清空对话", use_container_width=True):
    st.session_state['chat_page_messages'] = [
        {"role": "assistant", "content": "对话已清空！有什么我可以帮你的吗？"}
    ]
    st.rerun()