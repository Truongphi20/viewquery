import streamlit as st
import pandas as pd
import numpy as np
import viewquery as vq

def addLink(pid):
   url = 'https://pubmed.ncbi.nlm.nih.gov/'+ str(pid)
   return f'<a target="_blank" href="{url}/">{pid}</a>'

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

st.markdown("""
   # View query
   This is a tool for review article by NCBI query.
   """)

col1, col2 = st.columns([5,1])

with col1:
   query = st.text_input("_Please enter your NCBI query:_", 
                        placeholder="e.g: microorganism[Title/Abstract]", 
                        key="query")
with col2:
   val_get = st.number_input('Number of paper.', min_value=0, value=50)

submit = st.button('**Search**')

if submit:
   st.write("**Your query: " + str(query) + "**")
   st.write("_Number of paper was got: " + str(val_get) +"_")
   df=vq.load_data(query, val_get).reset_index()
   df["PID"] = df["PID"].apply(lambda xa: addLink(xa))
   df.index = np.arange(1, len(df) + 1)
   st.markdown(df.to_html(render_links=True, escape=False),unsafe_allow_html=True)
   st.write('')

   csv = convert_df(df)

   st.download_button(
       label="Download",
       data=csv,
       file_name='data.csv',
       mime='text/csv',
   )
   # st.table(df)
