import streamlit as st
import pandas as pd
import numpy as np
import viewquery as vq
import requests
from streamlit_lottie import st_lottie
from streamlit_lottie import st_lottie_spinner
import streamlit_ext as ste

st.set_page_config(page_title="View query", layout='wide')
# with open('style.css') as f:
#    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

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


st.title("**View query**")
st.markdown("""
   This tool is used for glimpsing articles on the Pubmed database of NCBI by [Entrez queries](https://www.ncbi.nlm.nih.gov/books/NBK3837/).
   """)

lottie_coding = loadLottie("https://assets7.lottiefiles.com/packages/lf20_ts4jcxke.json")

with st.form("formid"):
   col1, col2 = st.columns([5,1])

   with col1:
      query = st.text_input("_Please enter your Entrez query:_", 
                           placeholder="e.g: microorganism[Title/Abstract]", 
                           key="query")
   with col2:
      val_get = st.number_input('Number of paper.', min_value=0, value=50)

   submit = st.form_submit_button('🔍**Search**')

if submit:
   st.write("**Your query: " + str(query) + "**")
   # st_lottie(lottie_coding, height=500, key="coding")
   with st_lottie_spinner(lottie_coding, height=400, key="coding"):
      df, counts=vq.load_data(query, val_get)

   if int(val_get) <= int(counts):
      st.write("_The number of papers was got: " + str(val_get) +f"/{counts}_")
   else:
      st.write("_The number of papers was got: " + str(counts) +f"/{counts}_")

   df = df.reset_index()
   df.index = np.arange(1, len(df) + 1)

   df_show = df.copy()
   df_show["PID"] = df_show["PID"].apply(lambda xa: addLink(xa))
   
   csv = convert_df(df)

   ste.download_button(
       label="Download csv file",
       data=csv,
       file_name='data.csv',
       mime='text/csv',
   )
   # st.table(df)
   st.write('')
   st.markdown(df_show.to_html(render_links=True, escape=False),unsafe_allow_html=True)
   

   
