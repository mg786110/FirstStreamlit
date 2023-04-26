import streamlit as st
import gspread as gs
import pandas as pd
import numpy as np
import plotly.express as px
from google.oauth2 import service_account
import google.auth
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import httplib2
import os

from apiclient import discovery


def load_data():
    # API_KEY = 'AIzaSyB54rSWJhWjR-ErVPq2q7rzoyY9iJFKZiA'
    # SHEET_ID = '14LYf7RoDNXS2TmWvrSJ6cn99WIoYaXohiDBUU9x8R4g'
    # rangeName = 'Sheet1!A1:L11190'
    # discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
    #                 'version=v4')
    # service = discovery.build(
    #     'sheets',
    #     'v4',
    #     http=httplib2.Http(),
    #     discoveryServiceUrl=discoveryUrl,
    #     developerKey=API_KEY)
    # result = service.spreadsheets().values().get(
    #     spreadsheetId=SHEET_ID,range=rangeName).execute()
    # values = result.get('values', [])
  
    sheetsurl = st.secrets["privatesheeturl"]
    scopes = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
    credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes = scopes 
    )  
    


    
    

    gc = gs.authorize(credentials)
    sh = gc.open_by_url(sheetsurl)
    ws  = sh.worksheet("Sheet1")
    df = pd.DataFrame(ws.get_all_records())
   
 
    return df



st.header("Consumer Financial Complains Dashboard")
df = load_data()
# st.write(len(df))
states_list = df['state'].unique().tolist()
states_list.insert(0, 'ALL')
selected_state = st.selectbox('Select a state', states_list)

if selected_state == "ALL":
    df = df
else:
    df = df[df['state'] == selected_state]

st.subheader("Displaying data for " + selected_state )
# st.write('You selected:', state)

c = st.container()
col1,col2 ,col3,col4= c.columns((2,2,2,2))
total_complaints = df['count_distinct'].sum()

closed_data = df[df['company_response'].str.contains('close', case=False)]
closed_complaints = closed_data['count_distinct'].sum()

timely_data = df[df['timely'] == 'Yes']
timely_complaints = timely_data['count_distinct'].sum()

timelypercent  =  str(round((timely_complaints / total_complaints) * 100,2)) + '%'

inprogress_data = df[df['company_response'] == 'In progress']
inprogress_complaints = inprogress_data['count_distinct'].sum()



col1.metric("Total Complains", total_complaints)
col2.metric("Complains (Closed)",closed_complaints)
col3.metric("Timely Reponded(%)",timelypercent)
col4.metric("Complains (In Progress)",inprogress_complaints)
# st.write(df.head(10))

c1= st.container()
col5,col6 = c1.columns((2,2))
product_complaints = df.groupby('product')['count_distinct'].sum().reset_index()
barfig = px.bar(product_complaints, x='product', y='count_distinct', orientation='v')
             
barfig.update_layout(title = "Number of Complaints by Product",
                      xaxis_title = "Product",
                      yaxis_title = "# of Complaints")
                     


col5.plotly_chart(barfig, use_container_width=True)


df['month_end'] = pd.to_datetime(df['month_end'])
df['MonthYear'] = df['month_end'].dt.strftime('%Y-%m')
monthyear_complaints = df.groupby('MonthYear')['count_distinct'].sum().reset_index()
monthyear_complaints = monthyear_complaints.sort_values('MonthYear')

fig = px.line(monthyear_complaints, x='MonthYear', y='count_distinct')

fig.update_layout(title='Total Number of Complaints by Month and Year',
                   xaxis_title='Month and Year',
                   yaxis_title='Number of Complaints')

col6.plotly_chart(fig, use_container_width=True)

c2= st.container()
col7,col8 = c2.columns((2,2))

df['count_distinct'] = pd.to_numeric(df['count_distinct'])
channel_complaints = df.groupby('submitted_via')['count_distinct'].sum().reset_index()
fig_pie = px.pie(channel_complaints, values='count_distinct', names='submitted_via')


fig_pie.update_traces( textinfo='value')
fig_pie.update_layout(title='Total Number of Complaints by Channel')
col7.plotly_chart(fig_pie, use_container_width=True)


df_grouped = df.groupby(["issue", "sub_issue"])["count_distinct"].sum().reset_index()
fig_tree = px.treemap(df_grouped, path=['issue', 'sub_issue'], values='count_distinct')
fig_tree.update_layout(title='Number of Complaints by Issue and Sub-Issue', 
                  xaxis_title='Issue', 
                  yaxis_title='Sub-Issue' 
                  )
col8.plotly_chart(fig_tree, use_container_width=True)