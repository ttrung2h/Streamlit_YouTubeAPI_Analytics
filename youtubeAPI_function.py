import pandas as pd
import requests
from bs4 import BeautifulSoup
class YouTubeAPI:
    '''
        Class include function for crawling data from youtube such as: channel,video,comment
    '''
    @classmethod
    def get_channel_id(cls,url):
        '''
            Get channel id from url

            Param:
                url: url of channel

            Return:
                channel_id: id of channel
        '''
        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.content, 'html.parser')
            channel_id = soup.find('meta', {'itemprop': 'channelId'})['content']
        except:
            channel_id = None
        return channel_id
    @classmethod
    def get_channels_stats(cls,youtube,channel_ids):
        """
            Get channels stats from list of channel id

        Params:

            youtube: the build object from googleapiclient.discovery
            channel_ids: list of channel id
        
        Returns:
            Dataframe of given channel list id include: channelName,subcribers,views,totalvideo,playlistid 
        """
        all_data = []
        request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=','.join(channel_ids)
        )
        response = request.execute()
        for item in response['items']:
            data = {'channelName':item['snippet']['title'],
                'subcribers':item['statistics']['subscriberCount'],
                'views':int(item['statistics']['viewCount']),
                'totalVideo':int(item['statistics']['videoCount']),
                'playlistId':item['contentDetails']['relatedPlaylists']['uploads']}
            all_data.append(data)
        return pd.DataFrame(data=all_data)
    @classmethod
    def get_video_ids(cls,youtube,playlist_id):
        '''
        
        Get video id from playlist id

        Params:

            youtube: the build object from googleapiclient.discovery
            playlist_id: id of paticular playlist

        Returns:
            List of video ids got from playlist_ID
        '''
        video_ids = []
        request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults = 50
        )
        response = request.execute()
        for item in response['items']:
            video_ids.append(item['contentDetails']['videoId'])
        
        # using next page token to get all of data
        next_page_token = response.get('nextPageToken')
        # Loop until next page token is none
        while next_page_token is not None:
            
            request = youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=playlist_id,
                maxResults = 50,
                pageToken = next_page_token
            )
            response = request.execute()
            for item in response['items']:
                video_ids.append(item['contentDetails']['videoId'])
            next_page_token = response.get('nextPageToken')

        return video_ids
    @classmethod
    def get_video_stats(cls,youtube,video_ids):
        """
        
        Get stats information in list of video with given by list of video id
        Params:

            youtube: the build object from googleapiclient.discovery
            video_ids: list of video id

        Returns:
            Dataframe with video stats information.
        """
        all_video_info = []
        for i in range(0,len(video_ids),50):
            request = youtube.videos().list(
                    part="snippet,contentDetails,statistics",
                    id=video_ids[i:i+50]
                )
            response = request.execute()
            infor_to_keep = {'snippet':['channelTitle','publishedAt', 'title', 'description', 'tags'],
                                'statistics':['viewCount', 'likeCount', 'favoriteCount', 'commentCount'],
                                'contentDetails':['duration','definition', 'caption']}
            for video_item in response['items']:
                video_info = {}
                video_info['video_id'] = video_item['id']
                
                for k in infor_to_keep.keys():
                    for v in infor_to_keep[k]:
                        # Some infor will be None so we using try and execpt here
                        try:
                            video_info[v] = video_item[k][v]
                        except:
                            video_info[v] = None    
                all_video_info.append(video_info) 
        return pd.DataFrame(all_video_info)
    @classmethod
    def get_comments_in_videos(cls,youtube, video_ids):
        """
        Get top level comments as text from all videos with given IDs (only the first 10 comments due to quote limit of Youtube API)
        Params:
        
        youtube: the build object from googleapiclient.discovery
        video_ids: list of video IDs
        
        Returns:
        Dataframe with video IDs and associated top level comment in text.
        
        """
        all_comments = []
        
        for video_id in video_ids:
            try:   
                request = youtube.commentThreads().list(
                    part="snippet,replies",
                    videoId=video_id
                )
                response = request.execute()
            
                comments_in_video = [comment['snippet']['topLevelComment']['snippet']['textOriginal'] for comment in response['items'][0:10]]
                comments_in_video_info = {'video_id': video_id, 'comments': comments_in_video}

                all_comments.append(comments_in_video_info)
                
            except: 
                # When error occurs - most likely because comments are disabled on a video
                print('Could not get comments for video ' + video_id)
            
        return pd.DataFrame(all_comments)     