import streamlit as st
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# 设置页面配置
st.set_page_config(
    page_title="问数机器人",
    page_icon="🤖",
    layout="centered"
)

# 标题
st.title("🤖 问数机器人")
st.markdown("基于 LangGraph 的智能问答系统")

# 侧边栏状态
st.sidebar.header("系统状态")

# 检查依赖
dependencies_ok = True
try:
    from src.config import cfg
    st.sidebar.success("✅ 配置加载成功")
except Exception as e:
    st.sidebar.error(f"❌ 配置加载失败: {e}")
    dependencies_ok = False

try:
    from src.database import db_manager
    if db_manager.test_connection():
        st.sidebar.success("✅ 数据库连接正常")
        db_ok = True
    else:
        st.sidebar.error("❌ 数据库连接失败")
        db_ok = False
except Exception as e:
    st.sidebar.error(f"❌ 数据库模块错误: {e}")
    db_ok = False

# 初始化应用
app_ok = False
if dependencies_ok and db_ok:
    try:
        from src.main import langgraph_app
        app = langgraph_app()
        st.sidebar.success("✅ AI 模型加载成功")
        app_ok = True
    except Exception as e:
        st.sidebar.error(f"❌ AI 模型加载失败: {e}")

# 简单的问答界面
st.markdown("---")

# 示例问题
st.markdown("### 💡 示例问题")
col1, col2 = st.columns(2)

with col1:
    if st.button("什么是LangGraph？", key="q1"):
        st.session_state.example_question = "什么是LangGraph？"
    if st.button("你今天心情怎么样？", key="q2"):
        st.session_state.example_question = "你今天心情怎么样？"

with col2:
    if st.button("2024年即饮茶总销售额", key="q3"):
        st.session_state.example_question = "2024年即饮茶的总销售额是多少？"
    if st.button("查询商品销量TOP10", key="q4"):
        st.session_state.example_question = "查询销量最高的10个商品"

# 用户输入
user_question = st.text_input(
    "请输入您的问题:",
    value=st.session_state.get("example_question", ""),
    placeholder="例如：2024年即饮茶的总销售额是多少？"
)

# 处理问题
if user_question and st.button("🚀 提交问题"):
    st.markdown("---")

    # 显示用户问题
    st.markdown("### 📝 您的问题")
    st.write(user_question)

    if not app_ok:
        st.error("❌ 系统未完全就绪，无法处理问题。请检查侧边栏状态。")
    else:
        # 处理问题
        with st.spinner("🤔 正在思考中..."):
            try:
                result = app.invoke({"question": user_question})

                # 显示结果
                st.markdown("### 🤖 回答")

                final_answer = result.get("final_answer", [])
                if final_answer:
                    answer_text = final_answer[-1] if isinstance(final_answer, list) else str(final_answer)
                    st.success(answer_text)
                else:
                    st.warning("没有生成回答")

                # 显示SQL（如果有）
                sql = result.get("sql", "")
                if sql:
                    with st.expander("🔍 生成的SQL"):
                        st.code(sql, language="sql")

                # 显示查询结果（如果有）
                search_result = result.get("search_result", "")
                if search_result:
                    with st.expander("📊 查询结果"):
                        if isinstance(search_result, list) and len(search_result) > 0:
                            try:
                                import pandas as pd
                                df = pd.DataFrame(search_result)
                                st.dataframe(df)
                            except:
                                st.write(search_result)
                        else:
                            st.write(search_result)

            except Exception as e:
                st.error(f"处理问题时出现错误: {str(e)}")

# 使用说明
with st.expander("📖 使用说明"):
    st.markdown("""
    ### 功能介绍
    - **闲聊对话**: 可以进行普通的聊天对话
    - **数据库查询**: 根据自然语言生成SQL并查询数据库
    - **智能路由**: 自动识别问题类型并选择合适的处理方式

    ### 示例问题类型
    - 闲聊：`"什么是LangGraph？"`, `"你今天心情怎么样？"`
    - 数据库查询：`"2024年即饮茶总销售额"`, `"查询商品销量TOP10"`

    ### 注意事项
    - 确保数据库连接正常（见侧边栏状态）
    - AI 模型需要一定时间响应
    - 复杂查询可能需要更多时间处理
    """)

# 页脚
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 14px;'>"
    "🤖 问数机器人 - 基于 LangGraph + Streamlit 构建"
    "</div>",
    unsafe_allow_html=True
)