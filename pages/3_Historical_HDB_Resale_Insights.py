__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import pandas as pd
import streamlit as st
import os
from langchain.agents import Tool
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew
from dotenv import load_dotenv
from utility import check_password

st.set_page_config(
    layout="centered",
    page_title = "Historical HDB Resale Insights"
)

if not check_password():  
    st.stop()

if load_dotenv():
    os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
    os.environ['OPENAI_MODEL_NAME'] = os.getenv('OPENAI_MODEL_NAME')
else:
    os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
    os.environ['OPENAI_MODEL_NAME'] = st.secrets['OPENAI_MODEL_NAME']

st.title("Welcome to the Historical HDB Resale Insights Page")

with st.form("Input"):
    st.header("HDB Resale Property Question on Past Transactions")
    topic = st.text_area(label = "What would you like to find out?", value=st.session_state.get('topic', ""), placeholder= None)
    st.caption("Click on submit to proceed")
    submitted_topic = st.form_submit_button("Submit")

df = pd.read_csv("ResaleflatpricesbasedonregistrationdatefromJan2017onwards.csv")

@st.cache_data(show_spinner=False)
def data_ai(topic):
    pandas_tool_agent = create_pandas_dataframe_agent(
        llm=ChatOpenAI(temperature=0, model='gpt-4o-mini'),
        df=df, 
        agent_type=AgentType.OPENAI_FUNCTIONS,
        allow_dangerous_code=True
    )

    pandas_tool = Tool(
        name="Analyse tabular data with Code",
        func=pandas_tool_agent.invoke,
        description="Useful for search-based queries to perform analysis, filtering, and calculations on HDB resale data.",
    )

    agent_planner = Agent(
        role = "Content Planner",
        goal = "Extract key features of the topic: {topic}",
        backstory = """ You're working on extracting key aspects of the topic: {topic}, if the topic is on HDB resale housing statistics. 
        You collect information that is helpful for analysis and generating concise written content. 
        Your work is the basis for the Content Analyst to filter the dataset for analysis purpose, for the Content Writer to write a concise answer, and for the Programmer to code out a visulisation on the topic.
        If the topic is irrelevant to the HDB resale housing statistics, ambiguous, or contains harmful content, plan a safe and general response, indicating that the question is out of scope and you cannot answer it. 
        Do not attempt to create an outline for topics that are not related to HDB resale property.
        """,
        allow_delegation=False,
        verbose=True,
    )

    agent_data_analyst = Agent(
        role="Content Analyst",
        goal="Analyze the data based on the topic: {topic}",
        backstory="""You're the best data analyst. You will work on gathering insights that can answer the topic: {topic}, only if the topic is related to HDB resale housing.
        You base your analysis on the key aspects from the Content Planner.
        Your work is the basis for the Programmer to create suitable visualisations on the topic, and for the Content Writer to write out a data-driven response that could answer the topic.
        Aim to present the statistics in a mannner the Programmer can retrieve to generate python graph visualisations. 
        You have access to pandas_tool to gather the necessary information. Focus solely on information that can be obtained from the data. Remember that this data contain HDB resale statistics and nothing else.
        Do not attempt to modify the data or search for insights that are irrelevant to the data context or HDB resale property. Always respect user privacy.

        """,
        allow_delegation=False,
        verbose=True,
        tools=[pandas_tool],
    )

    agent_writer = Agent(
        role = "Content Writer",
        goal = "Write a clear and factually accurate answer to the user's topic: {topic} based on data, if the topic is on HDB resale housing",
        backstory = """You're working on writing a summary report that contains statistics and insights about the topic: {topic}, if the topic is on HDB resale housing.
        You base your writing on the statistics and insights of the Content Analyst, who provides the values calculated for the topic.
        You follow the main objectives and direction of the outline as provided by the Content Planner.
        You always strive to communicate in a clear, concise manner, adhering to best practices in data analysis reporting.
        Avoid including any content that is not related to HDB resale property, and if relevant information is missing or the question is ambiguous, provide a safe default response indicating that the question is out of scope and you are unable to answer it.
    """,
        allow_delegation= False,
        verbose=True
    )

    agent_programmer = Agent(
        role="Programmer",
        goal="Write matplotlib code to visualise the topic: {topic}",
        backstory="""You're the top-notch programmer who follows the best practices in Python coding.
        Based on the key aspects extracted by the Content Planner and information gathered by the Content Analyst, you write a code that could show an appropriate visualisation to enhance the answer given to the user's question: {topic}.
        Focus solely on the instructions given by Content Planner and information gathered by the Content Analyst. 
        You ignore any content not related to HDB resale property.
        """,
        allow_delegation=False,
        verbose=True, 
    )

    task_plan = Task(
        description ="""\
        1. Understand the topic: {topic}.
        2. Verify the topic is relevant to HDB resale housing statistics.
        3. If it relevant, identify key aspects of the topic that needs to be answered, that can be used to guide the direction of an analysis, report writing and python codes for visualisations.
        4. If the topic is irrelevant to the HDB resale housing statistics, ambiguous, or contains harmful content, plan a safe and general response, indicating that the question is out of scope and you cannot answer it. 
        5. Do not force a connection between the topic and HDB resale housing.
        """,
        expected_output="""\
        A list of key aspects on the topic if topic is relevant to HDB resale housing statistics, otherwise a plan on a safe and general response.""",

        agent=agent_planner,
    )


    task_analyze = Task(
        description="""\
        1. If the Content Planner gave a outline of a safe and generic response, do not attempt to query or analyse the data. 
        2. Otherwise, verify if the key aspects aligns with the dataset's contents. The dataset is only on HDB resale statistics.
        3. If it is relevant, use the tool to analyze the data based on the user query. If no data can be obtained, you may attempt to generalize the key aspects by identifying broader trends or related aspects, and then try to obtain the data again. If there is still no data, provide a generic response indicating that there is insufficient data to answer the topic. Always ensure that your responses are grounded in actual data; do not attempt to generate data that is non-existent.
        4. Develop key points covering the insights and statistics, prioritising readability for the Programmer.
        5. If the topic is irrelevant to the data, ambiguous, or contains harmful content, do not proceed with the analysis. 
        6. Do not force a connection between the topic and the dataset. The dataset only contains HDB resale property statistics.
        """,
        expected_output="""\
        Key statistics that can answer the topic if it is relevant and appropriate""",

        agent=agent_data_analyst,
        context= [task_plan],
    )

    task_write = Task(
        description = """\
        1. If the Content Planner gave a outline of a safe and generic response or the Content Analyst gave no analysis, provide a safe and generic response
        2. Otherwise, develop a comprehensive report based on the analysis and insights gained, that directly addresses the topic: {topic},  only if it is related to HDB resale flats
        3. Sections/Subtitles are properly named in an engaging manner.
        4. Ensure the post is structured with an engaging introduction, insightful body, and a summarizing conclusion.
        5. Proofread for grammatical error.
    """,
        expected_output="""\
        A well-written report that presents the insights the user is interested in.
        """,
        agent = agent_writer,
        context = [task_plan, task_analyze],
    )

    task_code = Task(
        description="""\
        1. If the Content Planner provided a generic response or there is no analysis from the Content Analyst, do not attempt to code. Simply state that a graph is not available.
        2. Otherwise, understand the user request on the topic: {topic} given by the Content Planner.
        3. Use the statistics by the Content Analyst to create a dataframe. This dataframe should have actual HDB resale statistics from the Content Analyst. If it is empty or not related to HDB resale property, state that the graph is not available.
        4. Write the matplotlib code to create a graph that answers the topic, using the dataframe created. Do not create your own sample data and add into the output. Proceed to next step only if the code is correct.
        5. End the code with st.pyplot(plt) instead of plt.show().
        """,

        expected_output="""\
        1. The code used to generate the visualisation. Only include code, do not include any text.
        """,

        agent=agent_programmer,
        context = [task_plan, task_analyze],
    )

    crew = Crew(
        agents=[agent_planner, agent_data_analyst, agent_writer, agent_programmer],
        tasks=[task_plan, task_analyze, task_write, task_code],
        verbose=True
    )

    result = crew.kickoff(inputs={"topic": topic})
    return result

if submitted_topic:
    if topic=="":
        st.error("Please enter a topic/question")
    elif not any(char.isalpha() for char in topic):
        st.error("Please enter a valid topic/question")
    else:
        with st.spinner("Please wait..."):
            analysis_report = data_ai(topic)
            st.session_state['topic'] = topic
            st.session_state['analysis_report'] = analysis_report.tasks_output[2]
            st.session_state['graph_code'] = str(analysis_report.tasks_output[3])

if st.session_state.get('analysis_report'):
    st.markdown(st.session_state['analysis_report'])
if st.session_state.get('graph_code'):
    try:
        graph_code = str(analysis_report.tasks_output[3])
        exec(graph_code.replace("`", "").replace("python", ""))
    except:
        st.error("Sorry, there are no available graphs")