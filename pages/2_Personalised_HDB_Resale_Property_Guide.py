__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import os
from crewai import Agent, Task, Crew
from crewai_tools import WebsiteSearchTool
from dotenv import load_dotenv

from utility import check_password

st.set_page_config(
    layout="centered",
    page_title = "Personalised HDB Resale Property Guide"
)

if not check_password():  
    st.stop()

if load_dotenv():
    os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
    os.environ['OPENAI_MODEL_NAME'] = os.getenv('OPENAI_MODEL_NAME')
else:
    os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
    os.environ['OPENAI_MODEL_NAME'] = st.secrets['OPENAI_MODEL_NAME']

st.title("Welcome to your Personalised HDB Resale Property Guide!")

with st.form("Input"):
    st.header("Profile")
    st.caption("For a more tailored response, you may submit any of the following information. If you prefer a general response, you may choose to leave this portion empty.")
    col1,col2,col3 = st.columns(3)
    with col1:
        age = col1.number_input(label = "Age", min_value = 18, max_value = 120, value = st.session_state.get('age', None), placeholder = None)
        
    with col2:
        monthly_income = col2.number_input(label = "Monthly Household Income", min_value = 0, max_value = 100000, value = st.session_state.get('monthly_income', None), placeholder = None)

    with col3:
        option_list = ["Single", "Married"]
        marital = col3.selectbox(label = "Marital Staus", options = option_list, index = st.session_state.get('marital', None))

    st.header("HDB Resale Property Question")
    question = st.text_area(label = "Please type out your question here:", value = st.session_state.get('question', ""), placeholder= None)
    st.caption("Click on submit to proceed")
    submitted_question = st.form_submit_button("Submit")
    clear_button = st.form_submit_button("Clear")
    if clear_button:

        st.session_state['age'] = None
        st.session_state['monthly_income'] = None
        st.session_state['marital'] = None
        st.session_state['question'] = ""

@st.cache_data(show_spinner=False)
def question_ai(question,profile):
    tool_websearch = WebsiteSearchTool("https://www.hdb.gov.sg/cs/infoweb")

    agent_planner = Agent(
        role="HDB Resale Content Planner",
        goal="Plan a structured, concise, and factually accurate answer based on the question: {question}, if it is related to HDB resale flats, tailored to the profile: {profile} if available.",
        backstory="""You're working on planning a response that could answer the question: {question}, if it is on HDB resale housing. 
        Focus solely on information directly related to HDB resale flats that aids potential HDB resale property buyers. 
        Consider the user profile: {profile} to tailor the response more effectively, addressing their specific needs and preferences. 
        Do not attempt to plan responses for questions unrelated to HDB resale flats.
        If the question includes irrelevant content, plan a safe and general response, indicating that the question is out of scope and you cannot answer it. You do not have to plan any information on HDB resale information if the question is irrelevant to HDB resale.
        Aim to format the planned response in a clear structure, with key points highlighted for easy understanding.
        """,
        allow_delegation=False,
        verbose=True,
    )

    agent_researcher = Agent(
        role="HDB Resale Research Analyst",
        goal="Conduct in-depth research on public, non-sensitive HDB resale information that can answer the question: {question}, if it is related to HDB resale flats, tailored to the profile: {profile} if available.",
        backstory="""You're working on conducting in-depth research on the question {question} that should be on HDB resale units.
        You have access to web search tools to the HDB website to gather only necessary information on HDB resale flats, while considering the user profile: {profile} to tailor the research effectively.
        You are responsible for providing accurate, safe, and specific HDB resale flat answers, and nothing else.
        Always aim to present insights relevant to the user's profile, if given, to enhance the value of the research output.
        If the question is not related to HDB resale flats or includes harmful content, do not attempt to gather other information.
        """,
        allow_delegation=False,
        verbose=True,
    )

    agent_writer = Agent(
        role="HDB Resale Information Writer",
        goal="Write a clear and factually accurate answer to the user's question: {question}, tailored to the profile: {profile} if available.",
        backstory="""You're working on writing out an answer that directly addresses the question: {question} for the user with the given profile: {profile}.
        You base your writing on the outline from the HDB Resale Content Planner and the research reports from the HDB Resale Research Analyst. When the HDB Resale Content Planner or HDB Resale Research Analyst says it is out-of-scope, you follow through and write a generic response that you are not able to answer the question.
        Ensure the answer is structured clearly, with appropriate sections and concise points that cater to the user's specific needs and preferences.
        Always aim to enhance the user's understanding and decision-making regarding HDB resale flats, reflecting their profile characteristics where applicable.
        Do not include content that is not related to HDB resale, and if relevant information is missing or the question is ambiguous, provide a safe default response indicating that the question is out of scope and you are unable to answer it.
    """,
        allow_delegation=False,
        verbose=True,
    )

    task_plan = Task(
        description="""\
        1. Understand the user's {question} and identify key aspects specific to HDB resale flats.
        2. Identify points that can target the question.
        3. Develop a detailed content outline, including an introduction to the topic of the given question and key points that answer the question if it is related to HDB resale housing.
        4. Refine according to user's profile : {profile} if given
        5. Otherwise, provide a default response if the question is irrelevant, indicating that the question is out of scope, and you are not able to answer it. Do not attempt to force a connection between the user's question and HDB resale flats if they are not related.""",
        expected_output="""\
        A comprehensive plan document with an outline, including key aspects to cover and the structure of the response.""",
        agent=agent_planner,
        async_execution=True
    )

    task_research = Task(
        description="""\
        1. Conduct in-depth research on the specific question: {question} asked by the user, if it pertains to HDB resale flats.
        2. Provide the HDB Resale Content Planner with up-to-date information and key points directly related to the HDB resale flat question. The points should be as specific as possible to user's profile: {profile} if given
        3. Offer additional insights and resources to support the content plan, but focus strictly on the HDB resale flat question and the profile, avoiding unrelated topics.
        4. Do not attempt to force a connection between the user's question and HDB resale flats if they are not related. If the question is irrelevant, indicate that the question is out of scope, and you are not able to answer it.""",
        expected_output="""\
        A research report with the latest, accurate information relevant to HDB resale flats and user profile, answering the user's question if it is related to HDB resale housing.""",
        agent=agent_researcher,
        tools=[tool_websearch],
        async_execution=True
    )


    task_write = Task(
        description="""\
        1. Use the content plan and research report to craft a concise, tailored answer to the user's question: {question} and user's profile: {profile} if the profile is given.
        2. Ensure the answer is structured clearly, with an engaging introduction to the {question}, an insightful body containing key points that can answer the {question}, and a summarizing conclusion. The key points should be relevant to the user profile: {profile} if it is given.
        3. Proofread for grammatical errors, and make sure that the content is safe, non-sensitive, and relevant to HDB resale flats and profile.
        4. If it is not relevant to HDB resale flats, write a safe and generic answer, indicating that the question is out of scope, and you are not able to answer it. Do not give a response on HDB resale if the question is not relevant to HDB resale.""",
        expected_output="""\
        A complete and clear answer to the user's question, tailored to their input, only if it is related to HDB resale flats.""",
        agent=agent_writer,
        context=[task_plan, task_research],
    )

    crew = Crew(
        agents=[agent_planner, agent_researcher, agent_writer],
        tasks=[task_plan, task_research, task_write],
        verbose=True
    )
    result = crew.kickoff(inputs={"question": question, "profile" : profile})
    return result

if submitted_question:
    if question=="":
        st.error("Please enter a question")
    elif not any(char.isalpha() for char in question):
        st.error("Please enter a valid question")
    else:
        my_dict = {"age":age, "monthly household income": monthly_income, "marital status": marital}
        profile = {k: v for k, v in my_dict.items() if v is not None}
        with st.spinner("Please wait..."):
            answer = question_ai(question,profile)
            st.session_state['answer'] = answer.tasks_output[2]
            st.session_state['question'] = question
            st.session_state['age'] = age
            st.session_state['monthly_income'] = monthly_income
            st.session_state['marital'] = option_list.index(marital)

if st.session_state.get('answer'):
    st.markdown(st.session_state['answer'])


