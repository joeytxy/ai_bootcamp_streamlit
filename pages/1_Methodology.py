import streamlit as st 

from utility import check_password

st.set_page_config(
    layout="centered",
    page_title = "Methodology"
)

if not check_password():  
    st.stop()

st.title("Methodology")
st.header("Use Case 1: Personalised HDB Resale Property Guide")
with st.expander("Data Flows and Implementation Details"):
    st.markdown("""
        **1. Collecting User Input**
        
        The application starts off with collecting input from the user in a form format. Users can key in some details about themselves, such as their age and monthly household income, and a specific question related to HDB resale properties.
        The type of input users can give for their profile details is controlled to avoid nonsensical input. 
        For instance, the input that users can give for ```age``` and ```monthly houshold income``` are limited to a number within an appropriate range. For ```marital status```, there are fixed options for users to select from.
        User input for profile is not compulsory, and users can simply submit a form with a question typed in a text box. 
                
        **2. Checking Validity of Question**
                
        Once the user submits their question, the application checks for the following:
                
        - The submitted question is not empty 
        - The submitted question contains alphabetic characters
        
        If the submitted question passes these two checks, the submitted question is assigned to the ```prompt``` parameter of a function that consists of an AI agent workflow. 
        If any profile details is given, it will be assigned to the ```profile``` parameter of the function. Otherwise, the ```profile``` parameter is set to None. 
                
        **3. AI Agents**
                
        A function containing of :blue-background[3 agents] and :gray-background[3 tasks] will be invoked upon submission of a valid question. The agents and tasks are listed below:
                
        - :blue-background[**Agent Planner:**] Plans a clear outline of the answer to the submitted question. Takes into consideration the profile given, if any.
                       
        - :blue-background[**Agent Researcher:**] Conducts research to gather accurate and relevant information regarding HDB resale properties. It has access to web search tools to the HDB official website to gather only necessary information that is relevant to the question and profile.
                
        - :blue-background[**Agent Writer:**] Compiles findings by the Agent Researcher and follows the outline given by the Agent Planner. Writes a coherent response that is structured clearly, with appropriate sections and concise points that answers to the user's question and profile.
                
        - :gray-background[**Task Plan:**] Identify key aspects of the question that relates to HDB resale flats and create an outline of key points that can target the question and user's profile.
        If irrelevant, plan a safe and default answer, indicating that the question is out of scope and you cannot answer it. ```async_execution=True``` is applied here along with Task Research to improve performance and overall execution time.
                
        - :gray-background[**Task Research:**] Gather HDB resale property information from the [HDB Official Website](https://www.hdb.gov.sg/cs/infoweb) using the ```WebsiteSearchTool``` that is relevant to the user's question and profile. 
        If question is not related to HDB resale property, do not force a link between the topic of the question and HDB resale flats. 
        ```async_execution=True``` is applied here along with Task Plan to improve performance, as we anticipate that the web search will take some time. 
        The outline from the Agent Planner is not crucial for the Agent Researcher to do its task as the Agent Writer will compile the results from both agents.
    
        - :gray-background[**Task Write:**] Write a response that is structured clearly, with an engaging introduction, insightful points and a conclusion. 
        The response should answer the question if it is related to HDB resale flats.
                
        A ```Crew``` object is instantiated to manage the agents and tasks. ```crew.kickoff()``` is called with the given ```prompt``` and ```profile```.
                
        **4. Result Processing**
        
        Results obtained from the function is processed and displayed on the Streamlit App.
                
        """)
st.image("case1.png")

st.divider()

st.header("Use Case 2: Historical HDB Resale Insights")
with st.expander("Data Flows and Implementation Details"):
    st.markdown("""
        **1. Collecting User Input**
        
        The application starts off with collecting input from the user in a form format. 
        The expected input is a question on the insights that the user would like to find out about past HDB resale transactions.
                
        **2. Checking Validity of Question**
                
        Once the user submits their question, the application checks for the following:
                
        - The submitted question is not empty 
        - The submitted question contains alphabetic characters
        
        If the submitted question passes these two checks, the submitted question is assigned to the ```topic``` parameter of a function that consists of an AI agent workflow. 

        **3. Data**
                
        A CSV file with past HDB resale transactions is downloaded from [data.gov.sg](https://data.gov.sg/datasets/d_8b84c4ee58e3cfc0ece0d773c8ca6abc/view) and loaded into a pandas DataFrame. 

        **4. AI Agents**
                
        A function containing of :blue-background[4 agents] and :gray-background[4 tasks] will be invoked upon submission of a valid question. The agents and tasks are listed below:
                
        - :blue-background[**Content Planner:**] Identifies key aspects of the submitted question. 
        Key aspects identified by the agent serves as a guide for the Content Analyst and Content Writer to perform their tasks. 
   
        - :blue-background[**Content Analyst:**] Analyses the data based on key aspects identified by the Content Planner and retrieves relevant statistics for the Content Writer and the Programmer to perform their tasks. 
        It has access to ```create_pandas_dataframe_agent``` from LangChain to analyse the dataset, and is aware that the dataset only covers HDB resale statistics.
                                
        - :blue-background[**Content Writer:**] Writes a comprehensive report based on the outline given by the Content Planner and insights consolidated by the Content Analyst.
                
        - :blue-background[**Programmer:**] Generates Python code for visualisations based on the insights provided by the Content Analyst and key aspects provided by the Content Planner.      
                
        - :gray-background[**Task Plan:**] Understand the submitted question and verify if question is related to HDB resale statistics. If relevant, identify key aspects of the question.
        If irrelevant, plan a safe and default answer, indicating that the question is out of scope and you cannot answer it. Do not assume that the data can be used to answer the question.
                                
        - :gray-background[**Task Analyze:**] Verify if insights can be extracted from the dataset to answer the key aspects identified by the Content Planner. 
        Do not modify the data. Do not proceed with the analysis if the question is not relevant or contains harmful content.
                    
        - :gray-background[**Task Write:**] Write a response that is structured clearly, with an engaging introduction, insightful points and a conclusion. 
        The response should answer the question if it is related to HDB resale statistics.
                
        - :gray-background[**Task Code:**] Generate a matplotlib code that could show a visualisation covering the key aspects given by the Content Planner and insights consolidated by the Content Analyst. Do not produce any graph if the question is not related to past HDB resale transactions.

        A ```Crew``` object is instantiated to manage the agents and tasks. ```crew.kickoff()``` is called with the given ```topic```.
                
        **4. Result Processing**
        
        Results obtained from the function is processed and displayed on the Streamlit App. If applicable, the generated code for visualisation is executed to produce the graph.
                
        """)
st.image("case2.png")