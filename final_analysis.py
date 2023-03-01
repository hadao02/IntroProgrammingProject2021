#!/usr/bin/env python
# coding: utf-8

# In[22]:


import argparse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import plotly

DEVELOPER_KEY = 'AIzaSyCZ9EKdulzZ00vxBSfcDvSeUgKJXMOk0dU'
youtube = build('youtube', 'v3', developerKey=DEVELOPER_KEY)


vid_id = []
#先跑前50筆影片資料(youtube設定每頁資料是50筆)
res = youtube.playlistItems().list(
        part= "contentDetails", 
        playlistId= "PL5l9iRZwq9UmgUx7feR8eAkWBsLtHpjFL", 
        maxResults = 50
    ).execute()
#拿影片id
for i in res['items']:
    vid_id.append(i['contentDetails']['videoId'])

#後續頁面的影片資料
while True:
    try:
        nexttoken = res['nextPageToken'] #當沒有下一頁的時候這邊會出現error，while迴圈會break
        res = youtube.playlistItems().list(
                part= "contentDetails", 
                playlistId= "PL5l9iRZwq9UmgUx7feR8eAkWBsLtHpjFL",
                pageToken = nexttoken,
                maxResults = 50
            ).execute()
        for i in res['items']:
            vid_id.append(i['contentDetails']['videoId'])
    except:
        break
# print(vid_id)
all_vid_inf = []
for id in vid_id:
    #後面接你的程式，然後id就是影片id，開始爬音樂分類
    def ytsearch():
        musiccategory = []
        request = youtube.videos().list(
            part= "topicDetails", 
            id= id 
        )
        response = request.execute()
        for i in response['items'][0]['topicDetails']['topicCategories']:
            musiccategory.append(i[30:])
        return musiccategory
    if __name__ == '__main__':
        all_vid_inf.extend(ytsearch())
print(sorted(all_vid_inf))

d = {}
[d.__setitem__(item,1+d.get(item,0)) for item in all_vid_inf]
# print(d)

keys = d.keys()
values = d.values()
plt.figure(figsize=(15, 8)) 
plt.bar(keys, values, align='center', width=0.3)


# all = np.asarray(all_vid_inf)
# print(all)

# category_dict = dict(video_categories.query('param_hl == "en"')[['id', 'snippet.title']].values)
# top10_world_vid['category'] = [None if pd.isna(x) else category_dict[x] for x in top10_world_vid['snippet.categoryId']]
# top10_world_vid[['snippet.categoryId', 'category']].head()

# df = pd.DataFrame({'freq': all})
# df.groupby('freq', as_index=False).size().plot(kind='bar')
# plt.show()

# df.groupby('Music').size().plot.hist()
# df1['Music'].value_counts().plot.bar()


# In[ ]:




