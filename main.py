import time
import pprint
import os
from multiprocessing import Process
from queue import Queue
from optparse import OptionParser
import csv

import requests


BASE_URL = "http://twitch.tv/"
BASE_API_URL = "https://api.twitch.tv/kraken/"
STREAMS = "streams/"
USERS = "/users/"


def online_status(streamer):
    r = requests.get(BASE_API_URL + STREAMS + streamer)
    if r.json()['stream'] == None:
        return(False)
    else:
        return(True)

def following(account):
    streamers = []
    online_streamers = []
    offline_streamers = []

    r = requests.get(BASE_API_URL + USERS + account + "/follows/channels")
    
    for streamer in r.json()["follows"]:
        streamer = streamer["channel"]["name"]
        streamers.append(streamer)

        status = online_status(streamer)
        if status == True:
            online_streamers.append(streamer)
        else:
            offline_streamers.append(streamer)

    return(streamers, online_streamers, offline_streamers)


def watch_stream(option, streamer):
    if option != "audio":
        os.system("livestreamer %s%s source" % (BASE_URL,streamer))
    else:
        os.system("livestreamer %s%s audio" % (BASE_URL,streamer))

def chat(streamer):
    os.system("firefox %s%s/chat" % (BASE_URL, streamer))

def run(account):
    parser = OptionParser()
    parser.add_option("-l", "--list", dest="status",  help="List streamers. Options 'all' or 'online'")
    parser.add_option("-q", "--quality", dest="quality",  help="Watch or listen to a stream. Options 'audio' or 'source'")
    parser.add_option("-w", "--watch", dest="watch",  help="The name of a streamer. The EXACT name.")
    parser.add_option("-c", "--chat", dest="chat", help="The name of a streamer. The EXACT name.")

    (options, args) = parser.parse_args()
    options = options.__dict__

    if options["status"]:
        if options["status"] == "all":
            print(following(account)[0])
        elif options["status"] == "online":
            print(following(account)[1])

    if options["watch"]:
        if options["quality"] == "audio":
            p_watch = Process(target=watch_stream, args=("audio", options["watch"]))
        elif options["quality"] == "source":
            p_watch = Process(watch_stream, args=("source", options["watch"]))
        else:
            p_watch = Process(watch_stream, args=("source", options["watch"]))

        p_watch.start()
        
    if options["chat"]:
        if options["chat"] == "terminal":
            print("Comming soon")
        else:
            p_chat = Process(target=chat, args=(options["chat"],))

        p_chat.start()

def setup():
    with open('config.txt', 'r') as f:
        for line in f:
            line = line.split("=")
            if line[0] == "account":
                if len(line[1]) < 1:
                    print("Add an account to the config!")
                    return None
                else:
                    return line[1]

if __name__ == "__main__":
    account = setup()
    if account!= None:
        run(account)
    
