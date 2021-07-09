
import streamlit as st
import json
import requests
import sys
import os
import pandas as pd
pd.plotting.register_matplotlib_converters()
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re
import requests, time
import google.auth

from datetime import datetime as dt
from google.cloud import bigquery
from google.cloud import bigquery_storage

import tempfile
with tempfile.NamedTemporaryFile(mode='w', delete=False) as fp:
    fp.write(st.secrets['GOOGLE_APPLICATION_CREDENTIALS'])
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = fp.name

# Authentication
# Setting the environment variable
#export GOOGLE_APPLICATION_CREDENTIALS="/Users/andie/Documents/GitHub/youtube_st/trending-youtube-318617-2aa80e6e72c6.json"

# Explicitly create a credentials object. This allows you to use the same
# credentials for both the BigQuery and BigQuery Storage clients, avoiding
# unnecessary API calls to fetch duplicate authentication tokens.
credentials, your_project_id = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
print(credentials)
# Make clients
bqclient = bigquery.Client(credentials=credentials, project=your_project_id,)
bqstorageclient = bigquery_storage.BigQueryReadClient(credentials=credentials)

# Download query results.
query_string = """
SELECT *
FROM `trending-youtube-318617.youtube.vn_youtube`
ORDER BY view_count DESC
LIMIT 1000
"""

dataframe = (
    bqclient.query(query_string)
    .result()
    .to_dataframe(bqstorage_client=bqstorageclient)
)

st.set_page_config(layout="wide")

st.title("What's Trending On Youtube Today?")

# Get date input
st.sidebar.markdown('## Date Range')
d3 = st.sidebar.date_input("Chọn thời gian phân tích", [])
# st.write(d3)

if __name__ == "__main__":
    
    st.markdown("## Bắt Trend Không Cần Sức")
    st.write(dataframe)

    st.markdown('## Visualization')
    # Create pairplot for category
    #chart1 = sns.histplot(data=country_df, x="categoryId")
    #st.pyplot(chart1.figure)

    # st.markdown('## Lịch sử Review Assignment')
    # st.write(review_df[dis_cols2])

    # st.markdown('## Lịch sử Discussion')
    # st.write(discuss_df[dis_cols3])

    
    # st.markdown('### Phân Bổ Thời Gian Nộp Assignment')
    # # Create a distribution chart for submission
    # chart1 = sns.catplot(x="weekday", kind="count", hue="channel_name", data=total_submit[['channel_name', 'weekday']])
    # st.write(total_submit)
    # st.pyplot(chart1)
    # st.markdown('### Phân Bổ Reviews Theo Channel')
    # # Create a bar chart for reviews
    # plt.figure(figsize=(16,6))
    # chart2 = sns.barplot(x=review_channel['channel_name'], y=review_channel['percentage'])
    # st.write(total_review[dis_cols00])
    # st.pyplot(chart2.figure)
    # st.markdown('### Lịch sử Discussion theo Channel')
    # # Create a distribution chart for wordcount
    # chart3 = sns.barplot(x=discuss_user['channel_name'], y=discuss_user['wordcount'])
    # st.write(discuss_user)
    # st.pyplot(chart3.figure)

    # # Number cards on Sidebar
    # st.sidebar.markdown(f'''<div class="card text-info bg-info mb-3" style="width: 18rem">
    # <div class="card-body">
    # <h5 class="card-title">ĐÃ NỘP</h5>
    # <p class="card-text">{len(submit_df):02d}</p>
    # </div>
    # </div>''', unsafe_allow_html=True)

    # review_cnt = 100 * len(submit_df[submit_df.reply_user_count > 0])/len(submit_df) if len(submit_df) > 0  else 0
    # st.sidebar.markdown(f'''<div class="card text-info bg-info mb-3" style="width: 18rem">
    # <div class="card-body">
    # <h5 class="card-title">ĐƯỢC REVIEW</h5>
    # <p class="card-text">{review_cnt:.0f}%</p>
    # </div>
    # </div>''', unsafe_allow_html=True)

    # st.sidebar.markdown(f'''<div class="card text-info bg-info mb-3" style="width: 18rem">
    # <div class="card-body">
    # <h5 class="card-title">ĐÃ REVIEW</h5>
    # <p class="card-text">{len(review_df):02d}</p>
    # </div>
    # </div>''', unsafe_allow_html=True)

    # st.sidebar.markdown(f'''<div class="card text-info bg-info mb-3" style="width: 18rem">
    # <div class="card-body">
    # <h5 class="card-title">THẢO LUẬN</h5>
    # <p class="card-text">{sum(discuss_df['wordcount']):,d} chữ</p>
    # </div>
    # </div>''', unsafe_allow_html=True)
    
# else:
#     st.markdown('Không tìm thấy Mã Số {}'.format(user_id))

## Run: streamlit run app.py