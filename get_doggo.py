import json
import requests
import os.path
from twilio.rest import Client

accounts = ['goldenunicornrae', 'lizclimo', 'shutthekaleup', 'mattsurelee']
media = []
captions = []

for acct in accounts:
    response = requests.get('https://www.instagram.com/'+acct+'/')
    html = response.text
    firstBit = 'window._sharedData = '
    lastBit = ';</script>'
    sharedData = html[html.index(firstBit) + len(firstBit) : html.index(lastBit)]
    profilePage = json.loads(sharedData)['entry_data']['ProfilePage'][0]
    edges = profilePage["graphql"]['user']['edge_owner_to_timeline_media']['edges']
    ids=[]

    if os.path.isfile(acct+"Ids.txt"):
        f = open(acct+"Ids.txt", "r")
        for line in f:
            ids.append(line.strip())
        f.close()

    newIds = []
    for edge in edges:
        newIds.append(edge['node']['id'])
        if edge['node']['id'] not in ids:
            captions.append(edge['node']['edge_media_to_caption']['edges'][0]["node"]['text'])
            if edge['node']["is_video"] == True:
                postResponse = requests.get('https://www.instagram.com/'+acct+'/p/' + edge['node']['shortcode'] + '/')
                html = postResponse.text
                print(html)
                firstBit = 'window._sharedData = '
                lastBit = ';</script>'
                sharedData = html[html.index(firstBit) + len(firstBit) : html.index(lastBit)]
                postJson = json.loads(sharedData)['entry_data']['PostPage'][0]
                media.append('V' + postJson['graphql']['shortcode_media']['video_url'])
            else:
                media.append(edge['node']['display_url'])

    f = open(acct+"Ids.txt", "w")
    for id in newIds:
        f.write(id + "\n")
    f.close()

assert len(captions) == len(media)
print(len(captions))
account_sid = 'ACd8275d7e6a468abba1dbf8086d6e6259'
keyFile = open("api_key.txt")
auth_token = keyFile.readline()
client = Client(account_sid, auth_token)
API_ENDPOINT = "https://api-ssl.bitly.com/v4/shorten"
headers = {"Authorization": "Bearer 1c1960534c7f7cb5e9d4892237fdfa6d20be0de5", 'Content-Type': 'application/json'}

for i in range(len(media)):
    if media[i][0] == 'V':
        link = media[i][1:]
        data = {'long_url':link}
        rPost = requests.post(url=API_ENDPOINT, data=json.dumps(data), headers=headers)
        rJson = rPost.json()
        if 'link' in rJson:
            link = rJson['link']
        client.messages \
            .create(
                body=captions[i] + " VIDEO LINK: " + link,
                from_='+12016763705',
                to='+18609900863'
            )
    else:
        client.messages \
            .create(
                body=captions[i],
                from_='+12016763705',
                media_url=[media[i]],
                to='+18609900863'
            )