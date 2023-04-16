import streamlit as st
import pandas as pd
import numpy as np
import viewquery as vq

df = pd.read_csv('df.csv')
# print(df)

st.markdown("""
   # View query
   This is a tool for review article by NCBI query.
   """)

col1, col2 = st.columns([5,1])

with col1:
   query = st.text_input("_Please set your NCBI query:_", 
                        placeholder="e.g: microorganism[Title/Abstract]", 
                        key="query")
with col2:
   val_get = st.number_input('Number of paper.', min_value=0, value=50)

if query:
   st.write("**Your query: " + str(query) + "**")
   st.write("_Number of paper was got: " + str(val_get) +"_")
   df=vq.load_data(query, val_get)
   st.table(df)
