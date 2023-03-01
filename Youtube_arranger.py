# term_project_direct_version.py
# 第一次使用前請先確認是否已安裝妥google-api-python-client、google-auth-oauthlib, 未安裝請執行: pip3 install google-api-python-client google-auth-oauthlib
# 每天每個API金鑰最多只能整理198個影片
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.discovery import build


while True:
    try:
        scopes = ["https://www.googleapis.com/auth/youtube"]
        client_secrets_file = input('請輸入您的OAuth2.0用戶端資訊json檔案，並將該檔案放於同層之資料夾: ') # client_secret_<example>.apps.googleusercontent.com.json
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
        credentials = flow.run_console()
        service = googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)
        break
    except:
        print('\n!!!錯誤訊息!!!\n未找到該檔案')
        print('若尚未取得OAth2.0用戶端資訊json檔案，請閱讀以下第15天至第18天之教學，取得該檔案，並將其至於同層資料夾: \nhttps://ithelp.ithome.com.tw/users/20140740/ironman/4250?page=2')


while True:
        try:
            DEVELOPER_KEY = input('請輸入您的API金鑰: ')
            youtube = build('youtube', 'v3', developerKey=DEVELOPER_KEY)
            break
        except:
            print('\n!!!錯誤訊息!!!\n請輸入有效API金鑰；若尚未申請，可參考以下申請教學: https://blog.jiatool.com/posts/youtube_spider_api/\n')


def duration(lst):
    vid_len = str(lst['contentDetails']['duration'])
    vid_len = vid_len.replace('P', ''); vid_len = vid_len.replace('T', ''); vid_len = vid_len.replace('H', ':'); vid_len = vid_len.replace('M', ':'); vid_len = vid_len.replace('S', '')
    len_lst = vid_len.split(':')
    if len(len_lst) == 1:
        duration = int(len_lst[0])
    elif len(len_lst) == 2:
        if len_lst[1] == '':
            duration = int(len_lst[0])*60
        else:
            duration = int(len_lst[0])*60 + int(len_lst[1])
    else:
        if len_lst[1] == '':
            len_lst[1] = '0'
        if len_lst[2] == '':
            len_lst[2] = '0'
        duration = int(len_lst[0])*3600 + int(len_lst[1])*60 + int(len_lst[2])
    return duration

def youtube_playlistItems(lst_id):
    vid_id = []
    playlist_dic = {'index':[], 'title':[], 'duration':[], 'creator':[], 'viewcount':[], 'likecount':[], 'vid_id' : []}
    index = 1
    request = youtube.playlistItems().list(
        part= "contentDetails,snippet,status", 
        playlistId= lst_id , #公開播放清單的id
        maxResults = 50
    )
    response = request.execute()
    for i in response['items']:
        if i["status"]["privacyStatus"] == 'public' or i["status"]["privacyStatus"] == 'unlisted':
            playlist_dic['index'].append(index)
            playlist_dic['title'].append(i['snippet']['title'])
            vid_id.append(i['contentDetails']['videoId'])
            playlist_dic['creator'].append(i['snippet']['videoOwnerChannelTitle'])
            index +=1
    playlist_dic['vid_id'].extend(vid_id)
    req = youtube.videos().list(
        part= "contentDetails,statistics", 
        id = ','.join(vid_id)
    )
    res = req.execute()
    for i in res['items']:
        playlist_dic['duration'].append(duration(i))
        playlist_dic['viewcount'].append(int(i['statistics']['viewCount']))
        try:
            playlist_dic['likecount'].append(int(i['statistics']['likeCount']))
        except:
            playlist_dic['likecount'].append(0)
    
    try:
        nexttoken = response['nextPageToken']
        while True:
            vid_id = []
            request = youtube.playlistItems().list(
                part= "contentDetails,snippet,status", 
                playlistId= lst_id , #公開播放清單的id
                pageToken = nexttoken, 
                maxResults = 50
            )
            response = request.execute()
            for i in response['items']:
                if i["status"]["privacyStatus"] == 'public' or i["status"]["privacyStatus"] == 'unlisted':
                    playlist_dic['index'].append(index)
                    playlist_dic['title'].append(i['snippet']['title'])
                    vid_id.append(i['contentDetails']['videoId'])
                    playlist_dic['creator'].append(i['snippet']['videoOwnerChannelTitle'])
                    index +=1
            playlist_dic['vid_id'].extend(vid_id)
            req = youtube.videos().list(
                part= "contentDetails,statistics", 
                id = ','.join(vid_id)
            )
            res = req.execute()
            for i in res['items']:
                playlist_dic['duration'].append(duration(i))
                playlist_dic['viewcount'].append(int(i['statistics']['viewCount']))
                try:
                    playlist_dic['likecount'].append(int(i['statistics']['likeCount']))
                except:
                    playlist_dic['likecount'].append(0)
            nexttoken = response['nextPageToken']
    except:
        return playlist_dic

def create_and_getId(playlst_name):
    response = service.playlists().insert(
        part = 'snippet,status', 
        body = {'snippet':{'title':playlst_name}, "status": {"privacyStatus": "public"}}
    ).execute()
    return response['id']

def sort_playList_dic(method, dic):
    """將播放清單以特定順序排列"""
    method_dic = {'t':'duration', 'n':'creator', 'v':'viewcount', 'l':'likecount'}
    if method[1] == 'a':
        dic['vid_id'] = sorted(dic['vid_id'], key = lambda x: dic[method_dic[method[0]]][dic['vid_id'].index(x)])
    else:
        dic['vid_id'] = sorted(dic['vid_id'], key = lambda x: dic[method_dic[method[0]]][dic['vid_id'].index(x)], reverse = True)
    return dic

def costume_sort(tar, des, dic):
    """將影片自原編號拖曳至指定編號"""
    if tar > des:
        for i in range(len(dic['index'])):
            if i >= des-1 and i < tar-1:
                dic['index'][i] += 1
            elif i == tar-1:
                dic['index'][i] = des
    else:
        for i in range(len(dic['index'])):
            if i <= des-1 and i > tar-1:
                dic['index'][i] -= 1
            elif i == tar-1:
                dic['index'][i] = des
    dic['vid_id'] = sorted(dic['vid_id'], key = lambda x: dic['index'][dic['vid_id'].index(x)])
    dic['index'] = sorted(dic['index'])
    return dic

def insert_to_playlist(dic, playlst_id):
    for id in dic['vid_id']:
        request_body = {
            'snippet': {
                'playlistId': playlst_id,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': id
                }
            }
        }
        service.playlistItems().insert(
            part='snippet',
            body=request_body
        ).execute()
    print("\n!!!清單重整成功!!!")
    print(f'請至以下連結確認新建立之撥放清單: https://www.youtube.com/playlist?list={playlst_id}')

if __name__ == '__main__': 
    print('歡迎使用yt播放清單排序小工具，以下為排序方法代碼:\n1. 播放時間正序/倒序排列: ta/td\n2. 頻道名稱正序/倒序排列: na/nd\n3. 觀看數正序/倒序排列: va/vd\n4. 按讚數正序/倒序排列: la/ld\n5. 自訂順序調換: co\n')

    while True:
        method = input('請輸入欲使用之排序方法的代碼: ')
        if method in ['ta', 'td', 'na', 'nd', 'va', 'vd', 'la', 'ld', 'co']:
            break
        print('\n!!!錯誤訊息!!!\n請輸入以下代碼:\n1. 播放時間正序/倒序排列: ta/td\n2. 頻道名稱正序/倒序排列: na/nd\n3. 觀看數正序/倒序排列: va/vd\n4. 按讚數正序/倒序排列: la/ld\n5. 自訂順序調換: co\n')

    while True:
        playlistId = input('請輸入您欲整理的播放清單id，並請務必確認已設為「公開」模式: ')
        try:
            playList = youtube_playlistItems(playlistId)
            break
        except:
            print('\n!!!錯誤訊息!!!\n請確認id是否輸入錯誤或該清單是否已設為「公開」模式\n')

    if method == 'co':
        print('\n自訂順序調換輸入格式說明:\n1. 欲調換影片排序，請輸入: 當前影片編號>更改後之編號(例:欲將編號11的影片移至編號22，請輸入11>22)\n2. 如欲結束操作，請輸入: 結束')
        while True:
            command = input('請輸入當前影片編號及更改後之編號: ')
            try:
                if command == '結束':
                    break
                target, destination = [int(m) for m in command.split('>')]
                if target == destination:
                    print('\n!!!錯誤訊息!!!\n請「移動」您的影片，輸入格式: 當前影片編號>更改後之編號；如欲結束操作，請輸入: 結束\n')
                    continue
                if target > len(playList['index']):
                    print('\n!!!錯誤訊息!!!\n請輸入正確的當前影片編號，輸入格式: 當前影片編號>更改後之編號；如欲結束操作，請輸入: 結束\n')
                    continue
                if destination > len(playList['index']):
                    destination = len(playList['index'])
                playList = costume_sort(target, destination, playList)
            except:
                print('\n!!!錯誤訊息!!!\n請輸入正確格式: 當前影片編號>更改後之編號；如欲結束操作，請輸入: 結束\n')
    else:
        playList = sort_playList_dic(method, playList)
    
    while True:
        try:
            tar_playlst = create_and_getId(input("請輸入新播放清單名稱: "))
            insert_to_playlist(playList, tar_playlst)
            break
        except:
            print('\n!!!錯誤訊息!!!\n請輸入有效播放清單名稱\n')
    



