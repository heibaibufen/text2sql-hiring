from operator import add
from re import search
from typing import Annotated, List, TypedDict
from langgraph.graph import END, StateGraph
from langgraph.graph import START
from langchain.chat_models import init_chat_model
from pydantic import BaseModel
from langchain_core.prompts import PromptTemplate
from sqlalchemy import sql
from src.config import cfg
from src.database import db_manager
from src.utils import clean_generation_result

tables = db_manager.get_tables_schemas()

chat_model = init_chat_model(
    model_provider="deepseek",
    model="deepseek-chat",
    base_url="https://api.deepseek.com/v1",
    api_key="sk-143f9eececeb4b2f958cb525a6d4a8be",
)
Question_Router_prompt = """
    请根据用户输入的问题，进行问题分类，并返回问题类型。
    问题类型有：闲聊类型，数据库类型
    请根据用户输入的问题，进行问题分类，并返回问题类型。
    实例：
    问题：什么是LangGraph？
    输出：闲聊类型

    问题：2024年康师傅品牌在各业态的即饮茶市场份额的排名
    输出：数据库问题

    问题：你会干什么？
    输出：闲聊问题
    只输出问题类型的string，不要返回其他内容。
    问题：{question}
    """
sql_prompt = """
    请根据用户输入的问题，生成SQL查询语句。
    这是数据库的schemas：
    {tables}
    实例：
    questions: 2024年即饮茶的总销售额
    sql: |
      ```
      SELECT
        "category",
        SUM("amount") AS "amount"
      FROM
        "product_sales_monthly"
      WHERE
        "region_name" IS NULL
        AND "province_name" IS NULL
        AND "channel" IS NULL
        AND "category" = '即饮茶'
        AND DATE_TRUNC ('MONTH', "biz_date") BETWEEN '2024-01-01' AND '2024-12-31'
      GROUP BY "category";
      ```
    问题：{question}
    请根据用户输入的问题，生成SQL查询语句，只输出sql查询语句不要有任何其他无关的内容。
    """
summary_prompt = """
    根据sql语句或查询结果完整的回答用户的问题。
    规则：如果用户的问题数据库中没有关联或者结果中不包含用户所需要的问题，请返回"数据库中没有对应的数据，请加入数据后在进行查询。"。
    问题：
    {question}
    sql语句:
    {sql}
    查询结果：
    {search_result}
    根据sql语句或查询结果完整的回答用户的问题，不要输出任何无关的内容。
    """
chat_prompt = """
    用户的问题为闲聊问题，你作为一个智能助理，对用户的问题进行回答。
    问题：
    {question}
"""
# 输入字段：用户的问题
class InputState(TypedDict):
    question: str
 
 
# 中间状态：包括中间结果
class InternalState(TypedDict):
    question: str
    search_result: str
    final_answer: Annotated[List[str], add]
    sql: str
    question_type: str
 
 
# 输出字段：只想返回最终答案
class OutputState(TypedDict):
    final_answer: Annotated[List[str], add]
 
 
def pre_process(state: InputState) -> InternalState:
    state["question"] = state["question"]
    return state
# 2. 定义节点函数（中间节点用中间字段）
def Question_Router(state: InternalState):
    prompt = PromptTemplate(
        template=Question_Router_prompt,
        input_variables=["question"],
    )
    llm = prompt| chat_model 
    res = llm.invoke({"question": state["question"]})
    print(res.content)
    if res.content in ["数据库类型", "闲聊类型"]:
        if res.content == "数据库类型":
            return "sql_node"
        elif res.content == "闲聊类型":
            return "chat_node"
    else:
        return "pre_process"

def chat(state: InternalState) -> dict:
    print("chat节点执行中")
    prompt = PromptTemplate(
        template=chat_prompt,
        input_variables=["question"],
    )
    llm = prompt| chat_model 
    res = llm.invoke({"question": state["question"]})
    return {"final_answer": [f"闲聊:{res.content}"]}
def SQL_Generator(state: InternalState) -> dict:
    print("1、SQL_Generator节点执行中")
    prompt = PromptTemplate(
        template=sql_prompt,
        input_variables=["question"],
        partial_variables={"tables": tables}
    )
    llm = prompt| chat_model 
    res = llm.invoke({"question": state["question"]})
    return {"sql": res.content,"final_answer": [f"sql生成节点"]}

def SQL_Correction(state: InternalState) -> dict:
    print("2、SQL_Correction节点执行中")
    sql = state["sql"]
    sql = clean_generation_result(sql)
    print(sql)
    return {"sql":sql , "final_answer": [f"sql校正节点"]}

def SQL_Executor(state: InternalState) -> dict:
    print("3、SQL_Executor节点执行中")
    sql = state["sql"]
    search_result = db_manager.execute_sql(sql)
    return {"search_result":search_result,"final_answer": [f"sql执行节点"]}

def Answer_Summary(state: InternalState) -> dict:
    
    print("4、Answer_Summary节点执行中")
    prompt = PromptTemplate(
        template=summary_prompt,
        input_variables=["question","sql","search_result"],
    )
    llm = prompt| chat_model 
    res = llm.invoke({"question": state["question"],"sql":state["sql"],"search_result":state["search_result"]})
    return {"final_answer": [f"回答: {res.content}"]}
def langgraph_app():
    builder = StateGraph(state_schema=InternalState,
                        input_schema=InputState,
                        output_schema=OutputState)
    builder.add_node("pre_process", pre_process)
    builder.add_node("SQL_Generator", SQL_Generator)
    builder.add_node("SQL_Correction", SQL_Correction)
    builder.add_node("SQL_Executor", SQL_Executor)
    builder.add_node("Answer_Summary", Answer_Summary)
    builder.add_node("chat", chat)
    
    builder.add_edge(START, "pre_process")
    builder.add_conditional_edges("pre_process",Question_Router,{
        "chat_node": "chat",
        "sql_node": "SQL_Generator",
        "pre_process": "pre_process"
    })
    builder.add_edge("SQL_Generator", "SQL_Correction")
    builder.add_edge("SQL_Correction", "SQL_Executor")   
    builder.add_edge("SQL_Executor", "Answer_Summary") 
    builder.add_edge("Answer_Summary", END)
    builder.add_edge("chat", END)
    app = builder.compile()
    return app
def main():
    # 测试数据库连接
    print("=== 数据库连接测试 ===")
    if db_manager.test_connection():
        print("✅ 数据库连接成功!")
    else:
        print("❌ 数据库连接失败!")
        return
    app = langgraph_app()
    result = app.invoke({"question": "即饮茶今年第一季度上市新品在今年间的销售额TOP10商品"})
    print(result)
    # print(sql)
    print("请实现你的项目代码")


if __name__ == "__main__":
    main()
