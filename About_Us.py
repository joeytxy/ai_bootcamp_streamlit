__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
from utility import check_password

st.set_page_config(
    layout="centered",
    page_title = "My Streamlit Application for HDB Resale Flat Buyers"
)

if not check_password():  
    st.stop()

st.title("Welcome to My Application! ")

with st.expander ("Disclaimer"):
    st.write('''
IMPORTANT NOTICE: This web application is a prototype developed for educational purposes only. The information provided here is NOT intended for real-world usage and should not be relied upon for making any decisions, especially those related to financial, legal, or healthcare matters.

Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You assume full responsibility for how you use any generated output.

Always consult with qualified professionals for accurate and personalized advice.
''')

st.header("About Us")

st.subheader("Project Scope")
st.markdown('''
Develop a Streamlit application with two use cases:

- **Answer User Queries**: Provide tailored responses to user questions related to HDB resale properties, personalized to their profiles.

- **Insights and Visualizations**: Offer easily understandable insights and visualizations (when applicable) using historical data on HDB resale property transactions, based on user queries.
''')

st.subheader("Objective")
st.write('''
The main goal of this application is to enhance the flat selection experience for buyers.

Currently, resale property buyers often need to conduct extensive research across multiple websites to understand the steps and details involved in purchasing a resale unit. They frequently encounter jargon and terminology specific to the HDB resale context, which may require further research to comprehend. 
Additionally, the information available online is often generic and difficult to relate to individual profiles.

Once buyers decide on a unit, negotiating prices becomes crucial. However, information about past HDB resale transactions is often limited on listings, and available datasets on past transactions can be hard to analyse and understand.

Hence, this application aims to bridge these gaps by addressing both use cases outlined in the project scope within a single website.
''')

st.subheader("Features")
with st.container():
    st.page_link("pages/2_Personalised_HDB_Resale_Property_Guide.py", label = "Provides answers to any questions on HDB resale flats, tailored to given profile", icon = "1️⃣" )
    st.caption("""Interested in buying a HDB resale flat but not sure where to start? Head over to the 'Personalised HDB Resale Property Guide' to get answers to any questions regarding resale flats tailored to your profile!
            Do note that this site is meant to answer HDB resale property questions. For other information beyond the HDB resale property scope, do head over to other relevant sites instead.
            """)
    with st.expander("A sample response"):
        st.image("PersonalisedAnswer1.png")
        st.image("PersonalisedAnswer2.png")
st.divider()
with st.container():
    st.page_link("pages/3_Historical_HDB_Resale_Insights.py", label = "Provides insights and visualisations (if applicable) to any questions on past HDB resale transactions", icon = "2️⃣" )
    st.caption("""Found your favourite listing but not sure how to start negotiating? Head over to the 'Historical HDB Resale Insights' page to find out more about HDB resale property transactions from 
                   January 2017 to October 2024.
                   Do note that the data only consists of HDB resale transactions from 2017 to 2024. For other information, you may wish to head over to the relevant sites instead.""")
    with st.expander("A sample response"):
        st.image("insight1.png")
        st.image("insight2.png")
        st.image("insight3.png")
        st.image("insight4.png")

st.subheader("Data Sources")
st.page_link("https://www.hdb.gov.sg/cs/infoweb", label= "HDB Offical Website", icon ="🔗")
st.page_link("https://data.gov.sg/datasets/d_8b84c4ee58e3cfc0ece0d773c8ca6abc/view", label = "Government Data on resale flat prices from Jan 2017 to Oct 2024", icon ="🔗")