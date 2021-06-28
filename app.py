
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
from datetime import datetime as dt
import requests, time, argparse


st.set_page_config(layout="wide")

st.title("What's Trending On Youtube Today?")

# GET YOUTUBE DATA
# Get API key
api_key = st.secrets['api_key']
# Get country code input
st.sidebar.markdown('## Country Code')
country_code = st.sidebar.text_input("Nhập Country Code", 'VN')

def api_request(page_token, country_code, category_id):
    # Builds the URL and requests the JSON from it
    request_url = f"https://www.googleapis.com/youtube/v3/videos?part=id,statistics,snippet{page_token}chart=mostPopular&regionCode={country_code}&snippet.publishedAt=2021-01-01T00%3A00%3A00Z&maxResults=50&key={api_key}&videoCategoryId={category_id}"
    request = requests.get(request_url)
    if request.status_code == 429:
        print("Temp-Banned due to excess requests, please wait and continue later")
        sys.exit()
    return request.json()

# Any characters to exclude, generally these are things that become problematic in CSV files
unsafe_characters = ['\n', '"']

def prepare_feature(feature):
    # Removes any character from the unsafe characters list and surrounds the whole item in quotes
    for ch in unsafe_characters:
        feature = str(feature).replace(ch, "")
    return f'"{feature}"'

def get_tags(tags_list):
    # Takes a list of tags, prepares each tag and joins them into a string by the pipe character
    return prepare_feature("|".join(tags_list))

def get_videos(items):

    youtube_df = None
    #Create dataframe
    dict1 = {'video_id': [], 'title': [], 'publishedAt': [], 'channelId': [], 'channelTitle': [], 'categoryId': [], 'trending_date': [], 'tags': [], 'view_count': [], 'likes': [], 'dislikes': [], 'comment_count': [], 'thumbnail_link': [], 'comments_disabled': [], 'ratings_disabled': [], 'description': []}
    for video in items:
        comments_disabled = False
        ratings_disabled = False

        # We can assume something is wrong with the video if it has no statistics, often this means it has been deleted
        # so we can just skip it
        if "statistics" not in video:
            continue

        # A full explanation of all of these features can be found on the GitHub page for this project
        video_id = prepare_feature(video['id'])

        # Snippet and statistics are sub-dicts of video, containing the most useful info
        snippet = video['snippet']
        title = prepare_feature(snippet.get('title', ""))
        publishedAt = prepare_feature(snippet.get('publishedAt', ""))
        channelId = prepare_feature(snippet.get('channelId', ""))
        channelTitle = prepare_feature(snippet.get('channelTitle', ""))
        categoryId = prepare_feature(snippet.get('categoryId', ""))
        
        statistics = video['statistics']
        view_count = statistics.get("viewCount", 0)
        # This may be unclear, essentially the way the API works is that if a video has comments or ratings disabled
        # then it has no feature for it, thus if they don't exist in the statistics dict we know they are disabled
        if 'likeCount' in statistics and 'dislikeCount' in statistics:
            likes = statistics['likeCount']
            dislikes = statistics['dislikeCount']
        else:
            ratings_disabled = True
            likes = 0
            dislikes = 0

        if 'commentCount' in statistics:
            comment_count = statistics['commentCount']
        else:
            comments_disabled = True
            comment_count = 0

        # The following are special case features which require unique processing, or are not within the snippet dict
        trending_date = time.strftime("%y.%d.%m")
        tags = get_tags(snippet.get("tags", ["[none]"]))
        thumbnail_link = snippet.get("thumbnails", dict()).get("default", dict()).get("url", "")
        description = snippet.get("description", "")

        dict1['video_id'].append(video_id)
        dict1['title'].append(title)
        dict1['publishedAt'].append(publishedAt)
        dict1['channelId'].append(channelId)
        dict1['channelTitle'].append(channelTitle)
        dict1['categoryId'].append(categoryId)
        dict1['trending_date'].append(trending_date)
        dict1['tags'].append(tags)
        dict1['view_count'].append(view_count)
        dict1['likes'].append(likes)
        dict1['dislikes'].append(dislikes)
        dict1['comment_count'].append(comment_count)
        dict1['thumbnail_link'].append(thumbnail_link)
        dict1['comments_disabled'].append(comments_disabled)
        dict1['ratings_disabled'].append(ratings_disabled)
        dict1['description'].append(description)

        youtube_df = pd.DataFrame(dict1)

    return youtube_df

if __name__ == "__main__":
    next_page_token="&"
    column_names = ['video_id', 'title', 'publishedAt', 'channelId', 'channelTitle', 'categoryId', 'trending_date', 'tags', 'view_count', 'likes', 'dislikes', 'comment_count', 'thumbnail_link', 'comments_disabled', 'ratings_disabled', 'description']
    country_df = pd.DataFrame(columns=column_names)

    # Because the API uses page tokens (which are literally just the same function of numbers everywhere) it is much
    # more inconvenient to iterate over pages, but that is what is done here.
    for category_id in range(1, 50):
        
        #print(category_id)
        next_page_token="&"
        while next_page_token is not None:
            #print(next_page_token)
            # A page of data i.e. a list of videos and all needed data
            video_data_page = api_request(next_page_token, country_code, category_id)
            
            # Get the next page token and build a string which can be injected into the request with it, unless it's None,
            # then let the whole thing be None so that the loop ends after this cycle
            next_page_token = video_data_page.get("nextPageToken", None)
            next_page_token = f"&pageToken={next_page_token}&" if next_page_token is not None else next_page_token

            # Get all of the items as a list and let get_videos return the needed features
            items = video_data_page.get('items', [])
            country_df = pd.concat([country_df, get_videos(items)])
        
    country_df = country_df.reset_index().drop(columns=['index'])
    
    st.markdown("## Today's Data")
    st.write(country_df)

    st.markdown('## Visualization')
    # Create pairplot for category
    chart1 = sns.histplot(data=country_df['categoryId'], x='categoryId')
    st.pyplot(chart1)

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