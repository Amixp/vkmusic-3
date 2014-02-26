#!/usr/bin/env python3

import os
import urllib.parse
import urllib.request
import json
import wget
import mutagenx.id3
import mutagenx.mp3

import vk_auth
from config import settings


def call_api(method, params):
    """Call VK.Api method"""
    params = urllib.parse.urlencode(params)
    url = "https://api.vk.com/method/{}?{}".format(method, params)
    response = urllib.request.urlopen(url).read().decode('utf-8')
    return json.loads(response)['response']


def get_album_name(album_id, sid):
    """album_id -> album_name"""
    params = {
        'access_token': sid
    }
    response = call_api('audio.getAlbums', params)
    for album in response[1:]:
        if album['album_id'] == album_id:
            return album['title']
    return None


def get_songs_by_album_id(sid, album_id):
    """Download list of songs from vk album"""
    params = {
        'access_token': sid,
        'album_id': album_id
    }

    album_name = get_album_name(album_id, sid)

    if album_name is None:
        print("Wrong album_id!")
        return None

    print('Downloading/updating "{}" ...'.format(album_name))

    response = call_api('audio.get', params)

    # make lists of urls and filenames
    urls = []
    names = []
    for song in response:
        names.append(song['artist'] + '-' + song['title'] + '.mp3')
        urls.append(song['url'])

    # make target directory
    directory = os.path.join(settings['directory'], album_name)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # download songs
    for name, url in zip(names, urls):
        filename = os.path.join(directory, name)
        if not os.path.exists(filename):
            bad_filename = wget.download(url)
            os.rename(bad_filename, filename)
            #edit id3 tags
            audio = mutagenx.mp3.MP3(filename)
            audio.delete()
            audio["TALB"] = mutagenx.id3.TALB(encoding=0, text=album_name)
            audio.save()


def main():
    sid, user_id = vk_auth.auth(settings['email'], settings['password'], settings['api_id'], "audio")
    get_songs_by_album_id(sid, settings['album_id'])

if __name__ == "__main__":
    main()
