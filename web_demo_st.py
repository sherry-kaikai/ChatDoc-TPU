# coding=utf-8
from chat import DocChatbot
import os
import streamlit as st
import time
import sys
import logging
sys.path.append(".")
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

'''
@st.cache_resource 是 Streamlit 提供的一个装饰器，
用于缓存返回全局资源（如数据库连接、机器学习模型等）的函数。
这些缓存的对象可以在所有用户、会话和重新运行中全局可用。
这个装饰器特别适合于那些本质上不可序列化的类型，例如数据库连接、文件句柄或线程等，但也可以用于可序列化的对象。
缓存的对象必须是线程安全的，因为它们可能会被多个线程同时访问。如果线程安全成为问题，可以考虑使用 st.session_state 来存储每个会话的资源。

@st.cache缓存函数输出，提高程序性能。当相同的输入再次调用该函数时，Streamlit 会返回缓存的输出而不是重新计算，这可以节省宝贵的时间。
'''
@st.cache_resource
def load_model():
    # 创建唯一实例（单实例模式）
    return DocChatbot.get_instance()

# 单实例 
chatbot_st = load_model()

# TODO: use glm2 format and hard code now, new to opt
def cut_history(u_input):
    if 'messages' not in st.session_state:
        return []

    history = []
    for idx in range(0, len(st.session_state['messages']), 2):
        history.append((st.session_state['messages'][idx]['content'], st.session_state['messages'][idx + 1]['content']))

    spilt = -1
    if len(history) > 0:
        while spilt >= -len(history):
            prompt_str = ["[Round {}]\n\n问：{}\n\n答：{}\n\n".format(idx + 1, x[0], x[1]) for idx, x in
                          enumerate(history[spilt:])]
            if len("".join(prompt_str) + u_input) < 450:
                spilt -= 1
            else:
                spilt += 1
                break
    else:
        spilt = 0

    if spilt != 0:
        history = history[spilt:]

    return history


# 侧边栏
with st.sidebar:
    st.title("💬 ChatDoc-TPU")
    st.write("上传一个文档，然后与我对话.")
    with st.form("Upload and Process", True):
        uploaded_file = st.file_uploader("上传文档", type=["pdf", "txt", "docx"], accept_multiple_files=True,
                                         )

        option = st.selectbox(
            "选择已保存的知识库",
            chatbot_st.get_vector_db(),
            format_func=lambda x: chatbot_st.time2file_name(x)
        )

        col1, col2 = st.columns(2)
        with col1:
            import_repository = st.form_submit_button("导入知识库")
        with col2:
            add_repository = st.form_submit_button("添加知识库")
        col3, col4 = st.columns(2)
        with col3:
            save_repository = st.form_submit_button("保存知识库")
        with col4:
            del_repository = st.form_submit_button("删除知识库")

        col5, col6 = st.columns(2)
        with col5:
            clear = st.form_submit_button("清除聊天记录")
        with col6:
            clear_file = st.form_submit_button("移除选中文档")

        if st.form_submit_button("重命名知识库") or 'renaming' in st.session_state:
            if len([x for x in chatbot_st.get_vector_db()]) == 0:
                st.error("无可选的本地知识库。")
                st.stop()

            st.session_state['renaming'] = True
            title = st.text_input('新知识库名称')
            if st.form_submit_button("确认重命名"):
                if title == "":
                    st.error("请输出新的知识库名称。")
                else:
                    chatbot_st.rename(option, title)
                    st.success("重命名成功。")
                    del st.session_state["renaming"]
                    time.sleep(0.1)
                    st.experimental_rerun()

        if save_repository and 'files' not in st.session_state:
            st.error("先上传文件构建知识库，才能保存知识库。")

        if not uploaded_file and add_repository:
            st.error("请先上传文件，再点击构建知识库。")

        if import_repository and len([x for x in chatbot_st.get_vector_db()]) == 0:
            st.error("无可选的本地知识库。")

        if clear:
            if 'files' not in st.session_state:
                if "messages" in st.session_state:
                    del st.session_state["messages"]
            else:
                st.session_state["messages"] = [{"role": "assistant", "content": "嗨！"}]

        if clear_file:
            if 'files' in st.session_state:
                del st.session_state["files"]
            if 'messages' in st.session_state:
                del st.session_state["messages"]

        if uploaded_file and add_repository:
            with st.spinner("Initializing vector db..."):
                files_name = []
                for i, item in enumerate(uploaded_file):
                    ext_name = os.path.splitext(item.name)[-1]
                    file_name = f"""./data/uploaded/{item.name}"""
                    with open(file_name, "wb") as f:
                        f.write(item.getbuffer())
                        f.close()
                    files_name.append(file_name)
                if chatbot_st.init_vector_db_from_documents(files_name):
                    if 'files' in st.session_state:
                        st.session_state['files'] = st.session_state['files'] + files_name
                    else:
                        st.session_state['files'] = files_name

                    st.session_state["messages"] = [{"role": "assistant", "content": "嗨！"}]
                    st.success('知识库添加完成！', icon='🎉')
                    st.balloons()
                else:
                    st.error("文件解析失败！")

        if save_repository and 'files' in st.session_state:
            chatbot_st.save_vector_db_to_local()
            st.success('知识库保存成功！', icon='🎉')
            st.experimental_rerun()

        if import_repository and option:
            chatbot_st.load_vector_db_from_local(option)
            st.session_state["messages"] = [{"role": "assistant", "content": "嗨！"}]
            st.success('知识库导入完成！', icon='🎉')
            st.session_state['files'] = chatbot_st.time2file_name(option).split(", ")
            st.balloons()

        if del_repository and option:
            chatbot_st.del_vector_db(option)
            st.success('知识库删除完成！', icon='🎉')
            st.experimental_rerun()

    if 'files' in st.session_state:
        st.markdown("\n".join([str(i + 1) + ". " + x.split("/")[-1] for i, x in enumerate(st.session_state.files)]))
    else:
        st.info(
            '点击Browse files选择要上传的文档，然后点击添加知识库按钮构建知识库。或者选择选择已持久化的知识库然后点击导入知识库按钮导入知识库。',
            icon="ℹ️")

if 'messages' in st.session_state:
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
# 获取用户输入
if user_input := st.chat_input():
    # import pdb;pdb.set_trace()
    # 检查是否已经有文件被上传
    if 'files' not in st.session_state:
        # 获取历史对话
        his = cut_history(user_input)
        # 检查是否已经有消息记录
        if 'messages' not in st.session_state:
            # 初始化消息记录
            st.session_state["messages"] = [{"role": "user", "content": user_input}]
        else:
            # 添加新的用户消息到消息记录
            st.session_state["messages"].append({"role": "user", "content": user_input})
        # 显示用户消息
        st.chat_message("user").write(user_input)
        # 创建助手消息容器
        with st.chat_message("assistant"):
            # 创建一个空的容器用于显示答案
            answer_container = st.empty()
            # 生成答案并显示
            for result_answer, _ in chatbot_st.llm.stream_predict(user_input, his):
                answer_container.markdown(result_answer)
        # 添加助手的回答到消息记录
        st.session_state["messages"].append({"role": "assistant", "content": result_answer})
    else:
        # 添加用户输入到消息记录
        st.session_state["messages"].append({"role": "user", "content": user_input})
        # 显示用户消息
        st.chat_message("user").write(user_input)
        # 创建助手消息容器
        with st.chat_message("assistant"):
            # 创建一个空的容器用于显示答案
            answer_container = st.empty()
            # 记录查询开始时间
            start_time = time.time()
            # 查询文档
            docs = chatbot_st.query_from_doc(user_input, 3)
            # 记录查询所用时间
            logging.info("Total quire time {}".format(time.time()- start_time))
            # 准备参考文档内容
            refer = "\n".join([x.page_content.replace("\n", '\t') for x in docs])
            # 准备提示信息
            PROMPT = """{}。\n请根据下面的参考文档回答上述问题。\n{}\n"""
            prompt = PROMPT.format(user_input, refer)
            # 生成答案并显示
            for result_answer, _ in chatbot_st.llm.stream_predict(prompt, []):
                answer_container.markdown(result_answer)
            # 展示参考文档
            with st.expander("References"):
                for i, doc in enumerate(docs):
                    # 获取文档来源和页码
                    source_str = os.path.basename(doc.metadata["source"]) if "source" in doc.metadata else ""
                    page_str = doc.metadata['page'] + 1 if "page" in doc.metadata else ""
                    # 显示参考文档
                    st.write(f"""### Reference [{i + 1}] {source_str} P{page_str}""")
                    st.write(doc.page_content)
                    i += 1
        # 添加助手的回答到消息记录
        st.session_state["messages"].append({"role": "assistant", "content": result_answer})
