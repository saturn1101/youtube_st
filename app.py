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
from datetime import date, timedelta
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

# Make clients
bqclient = bigquery.Client(credentials=credentials, project=your_project_id,)
bqstorageclient = bigquery_storage.BigQueryReadClient(credentials=credentials)

st.set_page_config(layout="wide")

# Download query results.
query_string = """
SELECT *
FROM `trending-youtube-318617.youtube.vn_youtube`
LIMIT 50000
"""

df = (
    bqclient.query(query_string)
    .result()
    .to_dataframe(bqstorage_client=bqstorageclient)
)
# Process df data
for i in range(len(df['categoryId'])):
    df['categoryId'][i] = df['categoryId'][i].strip('"')
    df['video_id'][i] = df['video_id'][i].strip('"')
    df['title'][i] = df['title'][i].strip('"')
    df['channelTitle'][i] = df['channelTitle'][i].strip('"')
    df['publishedAt'][i] = df['publishedAt'][i].strip('"')

# @st.cache
# def convert_todate(df):
#     df['publishedAt'] = pd.to_datetime(df['publishedAt']).dt.date
#     #df['trending_date'] = pd.to_datetime(df['trending_date'],format='%y.%d.%m').dt.date
#     df['timestamp'] = pd.to_datetime(df['timestamp'],format='%y.%d.%m, %H:%M').dt.hour
#     return df

# df = convert_todate(df)

# Dataset Overview
# value count
cnt_values = df.size / 17
# unique video count
cnt_unique = df['video_id'].nunique()
# Time period
start_date = '21.27.06'
end_date = dt.now().strftime("%y.%d.%m")

# Mapping categoryId to Category
id_to_category = {}

with open('videoCategories.json', 'r') as f:
    data = json.load(f)
    for category in data['items']:
        id_to_category[category['id']] = category['snippet']['title']

df.insert(6, 'category', df.categoryId.map(id_to_category))

# Get highest values by video_id
#print(df['timestamp'][5])
#today = dt.date.today()
#vid_views = df[df['trending_date'] >= today - dt.timedelta(days=1)]
vid_views = df[df['trending_date'] == '21.09.07']
vid_views = vid_views.groupby(['video_id', 'title', 'category', 'channelTitle']).agg({'view_count': 'max'}).reset_index()
vid_views['rank'] = vid_views['view_count'].rank(method='max', ascending=False)
top_video = vid_views[vid_views['rank'] <= 10].sort_values(by=['view_count'], ascending=False)

# Create a new_df with unique video_id
new_df = df.copy()
new_df.drop_duplicates(subset=['video_id'], keep='last', inplace=True)

# By category
cat_df = new_df.groupby(['category']).agg(video_count = ('video_id', 'count')).sort_values('video_count', ascending=False).reset_index().head(10)

# By channel
channel_df = new_df.groupby(['channelTitle']).agg(video_count = ('video_id', 'count')).sort_values('video_count', ascending=False).reset_index().head(10)

# Most viewed videos
view_df = new_df.sort_values(by='view_count', ascending=False).head(10)

# Most liked videos
like_df = new_df.sort_values(by='likes', ascending=False).head(10)

# View count of a video
dance_df = df[df['video_id'] == 'CuklIb9d3fI']
dance_df = dance_df[['video_id', 'title', 'timestamp', 'view_count']]
dance_df['p_view'] = dance_df['view_count'] / 1000000
dance_df = dance_df.sort_values(by='view_count')

dance = dance_df[['video_id', 'title', 'timestamp', 'p_view']]

# dance = dance_df.query("video_id == 'CuklIb9d3fI'")
# dance_df['timestamp_c'] = dance_df['timestamp']
# dance_df.sort_values(by='timestamp')
# for i in range(len(dance_df['timestamp'])):
#     dance_df['timestamp_c'][i] = dt.strptime(dance_df['timestamp'][i], '%y.%d.%m, %H:%M')
#dance_df['date'] = pd.to_datetime(df['timestamp'],format='%y.%d.%m, %H:%M').dt.date()
# dance_df = dance_df[df['trending_date'] == '21.09.07']

st.title("What's Trending On Youtube Vietnam?")

# Get date
# st.sidebar.markdown('## Date Range')
# date = st.sidebar.date_input("Chọn thời gian phân tích", [])

if __name__ == "__main__":
    
    st.markdown("### *Bắt Trend Không Cần Sức*")
    st.markdown("## Top 10 Trending Tính Theo Số Views Hôm Nay")
    st.write(top_video)
    
    st.markdown("## Liếc Nhẹ Top Trending")
    # st.write(new_df)
    col1, col2 = st.beta_columns(2)
    col1.header('Top Categories')
    # Create barplot for category
    chart1 = sns.barplot(x='video_count', y='category', data=cat_df)
    col1.pyplot(chart1.figure)

    col2.header('Top Channels')
    #Create barplot for channelTitle
    chart2 = sns.barplot(x='video_count', y='channelTitle', data=channel_df)
    col2.pyplot(chart2.figure)

    col3, col4 = st.beta_columns(2)
    col3.header('Most Viewed Trending Videos')
    # Create pairplot for category
    #st.write(view_df)
    chart3 = sns.barplot(x="view_count", y="title", data=view_df)
    st.pyplot(chart3.figure)

    col4.header('Most Liked Trending Videos')
    chart4 = sns.barplot(x='likes', y='title', data=like_df)
    st.pyplot(chart4.figure)

    st.markdown('## Giả Vờ Không Quan Tâm Tới MV Mới Của BTS: Permission to Dance')
    st.write(dance_df)
    # chart5 = sns.barplot(x="p_view", y="timestamp", data=dance)
    # st.pyplot(chart5.figure)


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

    # Number cards on Sidebar
    # Total number of values
    st.sidebar.markdown("## Tổng Quan Bộ Dữ Liệu")
    st.sidebar.markdown(f'''<div class="card text-info bg-info mb-3" style="width: 18rem">
    <div class="card-body">
    <h5 class="card-title">Tổng Số Giá Trị Thu Thập</h5>
    <p class="card-text">{cnt_values:.0f}</p>
    </div>
    </div>''', unsafe_allow_html=True)

    # Unique video counts
    st.sidebar.markdown(f'''<div class="card text-info bg-info mb-3" style="width: 18rem">
    <div class="card-body">
    <h5 class="card-title">Tổng Số Video</h5>
    <p class="card-text">{cnt_unique:02d}</p>
    </div>
    </div>''', unsafe_allow_html=True)

    # Start Time
    st.sidebar.markdown(f'''<div class="card text-info bg-info mb-3" style="width: 18rem">
    <div class="card-body">
    <h5 class="card-title">Ngày Bắt Đầu Thu Thập</h5>
    <p class="card-text">{start_date}</p>
    </div>
    </div>''', unsafe_allow_html=True)

    # End Time
    st.sidebar.markdown(f'''<div class="card text-info bg-info mb-3" style="width: 18rem">
    <div class="card-body">
    <h5 class="card-title">Ngày Bắt Đầu Thu Thập</h5>
    <p class="card-text">{end_date}</p>
    </div>
    </div>''', unsafe_allow_html=True)

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

## Run: streamlit run app.py