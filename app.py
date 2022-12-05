import streamlit as st
from youtubeAPI_function import YouTubeAPI
import time
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from googleapiclient.discovery import build
import isodate
from dateutil import parser
import requests
from bs4 import BeautifulSoup
API_KEY = 'AIzaSyB-O6RzHQDjYHoJDZ_xccbrv9GPOZsWYtU'
YOUTUBE = build(
    "youtube", "v3", developerKey = API_KEY, cache_discovery=False)


def bar_loading():
    '''
    Create bar loading
    '''
    progress_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.001)
        progress_bar.progress(percent_complete + 1)

def show_info_channel(list_channel_id):
    '''
        Show info of channel   
        
        Params:
            channel_id: id of channel
            
            Returns:
                None
    '''
    # Show channel infor
    st.write(f'Here is your channel id {list_channel_id}')
    channel_infomation_df = YouTubeAPI.get_channels_stats(YOUTUBE,list_channel_id)
    st.write(channel_infomation_df)
    return channel_infomation_df


def plot_distribution_view(channel_information_df):
    '''
        Plot distribution view of each channel

        Prams:
        channel_information_df : List of channel stats information
    '''
    ...


def plot_channel_information_df(channel_information_df):
    '''
        Plot stats info of channel stats
    '''
    channel_numeric_feature=["subcribers","views","totalVideo"]
    channel_information_df[channel_numeric_feature] = channel_information_df[channel_numeric_feature].apply(pd.to_numeric) 

    plt.figure(figsize=(10,32))
    fig,ax = plt.subplots(1,2,figsize=(30,15))

    # Setting ax0
    p0 = sns.barplot(x = channel_information_df['channelName'],y = channel_information_df['subcribers'],ax=ax[0])
    p0.set_xlabel("Channel Name", fontsize = 20)
    p0.set_ylabel("Subcribers", fontsize = 20)
    
    # Setting ax1
    p1 = sns.barplot(x = channel_information_df['channelName'],y = channel_information_df['views'],ax=ax[1])
    p1.set_xlabel("Channel Name", fontsize = 20)
    p1.set_ylabel("Views", fontsize = 20)
    
    # Plot in streamlit
    st.pyplot(fig)


def pre_processing_video_stats(videos_stats_df):
    '''
        Processing data in video stats df 
    '''
    
    # Convert some feature to numeric
    numeric_feature = ['viewCount','likeCount','favoriteCount','commentCount']
    videos_stats_df[numeric_feature] = videos_stats_df[numeric_feature].apply(pd.to_numeric)
    
    # Create publish day (in the week) column
    videos_stats_df['publishedAt'] =  videos_stats_df['publishedAt'].apply(lambda x: parser.parse(x)) 
    videos_stats_df['pushblishDayName'] = videos_stats_df['publishedAt'].apply(lambda x: x.strftime("%A")) 

    # Create columns contain duration second converted from duration
    videos_stats_df['duration_second'] = videos_stats_df['duration'].apply(lambda x: isodate.parse_duration(x).total_seconds())

    return videos_stats_df


def plot_info_video(videos_stats_df):
    '''
        Plot information of video from video statistic data frame
    '''
    # Plot distribution of view
    st.header("Distribution of view in each channel")
    fig1 = plt.figure(figsize=(20,18))
    sns.violinplot(videos_stats_df['channelTitle'], videos_stats_df['viewCount'], palette = 'pastel')
    plt.title('Views per channel', fontsize = 14)
    st.pyplot(fig1)

    # Plot number of video published each day in week
    st.header('Number of video published each day in week')
    fig2 = plt.figure(figsize=(20,18))
    videoPerDay = videos_stats_df['pushblishDayName'].value_counts()
    sns.barplot(x = videoPerDay.index,y = videoPerDay.values) 
    st.pyplot(fig2)
    
    # Plot correlation between like and view , number comment and view
    st.header("Correlation between number of like and view , number of comment and view")
    fig3,ax = plt.subplots(1,2,figsize = (20,10))
    sns.scatterplot(x = videos_stats_df['likeCount'],y = videos_stats_df['viewCount'],ax = ax[0])
    sns.scatterplot(x = videos_stats_df['commentCount'],y = videos_stats_df['viewCount'],ax = ax[1])
    st.pyplot(fig3)


def main():
    st.title("Youtube Analytics")
    list_link_channel = st.text_input("Enter Link Of Channel Or List Of Link Channel").split(',')
    number_channel = len(list_link_channel)
    channel_info_df = pd.DataFrame()
    # Check user want to see information of list channel
    if st.button("Get Channel Info"):
        list_channel_id = []
        for channel in list_link_channel:
            list_channel_id.append(YouTubeAPI.get_channel_id(channel))
       
        if len(list_channel_id) != 0:
            st.header('Information of channel')
            bar_loading()
            channel_info_df = show_info_channel(list_channel_id)
            if len(list_channel_id) > 1:
                plot_channel_information_df(channel_info_df)
            
            # Get list of video ids
            list_playlistID = list(channel_info_df.playlistId.values)
            list_video_id =[]
            for playlist_id in list_playlistID:
                list_video_id = list_video_id + YouTubeAPI.get_video_ids(YOUTUBE,playlist_id)
            st.write(f'Total Number Video in {number_channel} channels: {len(list_video_id)}')
            # Get video df from list video
            video_stats_df = pre_processing_video_stats(YouTubeAPI.get_video_stats(YOUTUBE,list_video_id))
            st.write(video_stats_df.head())
            
            # Spinner
            with st.spinner('Wait for it...'):
                time.sleep(3)
            st.success('Done!')
            #st.header('Plot information about video')
            plot_info_video(video_stats_df)
            
if __name__ == "__main__":
    main()