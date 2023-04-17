import streamlit as st
import pandas as pd
import numpy as np
import viewquery as vq
import requests
from streamlit_lottie import st_lottie
from streamlit_lottie import st_lottie_spinner

def addLink(pid):
   url = 'https://pubmed.ncbi.nlm.nih.gov/'+ str(pid)
   return f'<a target="_blank" href="{url}/">{pid}</a>'

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

@st.cache_data
def loadLottie(url):
   r = requests.get(url)
   if r.status_code != 200:
      return None
   else:
      return r.json()

st.set_page_config(page_title="View query", layout='wide')

st.markdown("""
   # View query
   This tool is for glimpsing articles on the Pubmed database of NCBI by [Entrez queries](https://www.ncbi.nlm.nih.gov/books/NBK3837/).
   """)

lottie_coding = loadLottie("https://assets7.lottiefiles.com/packages/lf20_ts4jcxke.json")

col1, col2 = st.columns([5,1])

with col1:
   query = st.text_input("_Please enter your NCBI query:_", 
                        placeholder="e.g: microorganism[Title/Abstract]", 
                        key="query")
with col2:
   val_get = st.number_input('Number of paper.', min_value=0, value=50)

submit = st.button('🔍**Search**')

if submit:
   st.write("**Your query: " + str(query) + "**")
   # st_lottie(lottie_coding, height=500, key="coding")
   with st_lottie_spinner(lottie_coding, height=400, key="coding"):
      df, counts=vq.load_data(query, val_get)
   st.write("_The number of papers was got: " + str(val_get) +f"/{counts}_")

   df = df.reset_index()
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
