#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import json
from urllib.request import urlopen
from urllib.parse import urlencode
import os
from shutil import rmtree
from time import sleep, time


def auth(login, pwd):
    params = {}
    params['grant_type'] = 'password'
    params['client_id'] = '2274003'
    params['client_secret'] = 'hHbZxrka2uZ6jB1inYsH'
    params['username'] = login
    params['password'] = pwd
    request_str = 'https://oauth.vk.com/token?%s' % urlencode(params)
    r = urlopen(request_str).read()
    response = bytes.decode(r)
    json_data = json.loads(response)
    if 'error' in json_data:
        return {'error': 'Wrong auth data'}
    if 'access_token' in json_data:
        return json_data
    if not 'error' in json_data and not 'access_token' in json_data:
        return {'error': 'Unknown error'}


def deauth():
    try:
        os.remove('token')
        sys.exit('User deauthorized.')
    except Exception:
        sys.exit('Error. No authorized user found.')


def touch(path):
    with open(path, 'a'):
        os.utime(path, None)


def create_file(file_path):
    if not os.path.exists(file_path):
        touch(file_path)


def create_directory(private_dir_name):
    if os.path.isdir(private_dir_name):
        rmtree(private_dir_name)
        os.mkdir(private_dir_name)
    else:
        os.mkdir(private_dir_name)


def emoji_wipe(plain):
    array = bytearray(plain)
    while b'\xf0' in array:
        pos = array.find(b'\xf0')
        array = array.replace(array[pos:], array[pos+4:])
    while b'\xe2' in array:
        pos = array.find(b'\xe2')
        array = array.replace(array[pos:], array[pos+3:])
    return bytearray.decode(array, 'utf-8', errors='ignore')


def request(method, params, is_one):
    try:
        sleep(request_interval)
        request_str = 'https://api.vk.com/method/%s?%s' % (method, urlencode(params))
        r = urlopen(request_str).read()
        json_data = json.loads(emoji_wipe(r))
        if 'error' in json_data:
            return {'error': json_data['error']}
        if 'response' in json_data:
            json_data = json_data['response']
            json_data = list(json_data)
            if is_one == True:
                return json_data.pop()
            else:
                return json_data
        if not 'error' in json_data and not 'response' in json_data:
            return {'error': 'unknown error'}
    except Exception:
        pass


def get_photos_method(uid, token, file_name, f, photo_method):
    params = {}
    params['access_token'] = token
    params['owner_id'] = uid
    params['count'] = 0
    photos_count = request('photos.%s' % photo_method, params, is_one=True)
    path = file_name
    if photos_count:
        try:
            f = open(path, 'a')
            fave_iterations = int(photos_count/100)+1
            params['count'] = 100
            for i in range(0,fave_iterations,1):
                params['offset'] = 100*i
                photos_response = request('photos.%s' % photo_method, params, is_one=False)
                photos_response = photos_response[1:]
                for each in photos_response:
                    if 'src_xxbig' in each:
                        link = each['src_xxbig']
                    elif 'src_xbig' in each:
                        link = each['src_xbig']
                    elif 'src_xbig' in each:
                        link = each['src_xbig']
                    elif 'src_big' in each:
                        link = each['src_big']
                    elif 'src_small' in each:
                        link = each['src_small']
                    elif 'src' in each:
                        link = each['src']
                    else:
                        link = '???'
                    f.write('%s\n' % link)
                    print('collecting %s' % link)
            f.close()
        except Exception:
            pass
    else:
        pass


def get_photos_album(uid, token, file_name, f, album_id):
    params = {}
    params['access_token'] = token
    params['owner_id'] = uid
    params['count'] = 1000
    params['album_id'] = str(album_id)
    path = file_name
    try:
        f = open(path, 'a')
        photos_response = request('photos.get', params, is_one=False)
        for each in photos_response:
            try:
                if 'src_xxbig' in each:
                    link = each['src_xxbig']
                elif 'src_xbig' in each:
                    link = each['src_xbig']
                elif 'src_xbig' in each:
                    link = each['src_xbig']
                elif 'src_big' in each:
                    link = each['src_big']
                elif 'src_small' in each:
                    link = each['src_small']
                elif 'src' in each:
                    link = each['src']
                else:
                    link = '???'
                f.write('%s\n' % link)
                print('collecting %s' % link)
            except Exception:
                pass
        f.close()
    except Exception:
        pass


def get_photos(uid, token, directory_name, f):
    download_methods = ['getAll']#, 'getUserPhotos' 'getNewTags'
    album_ids = [-6, -7, -15]
    for index, d_method in enumerate(download_methods):
        get_photos_method(uid, token, directory_name, f, d_method)
    for index, album_num in enumerate(album_ids):
        get_photos_album(uid, token, directory_name, f, album_num)


def check_token(token):
    params = {'access_token': token}
    try:
        check = request('users.get', params, is_one=True)
    except Exception:
        return False
    if ('uid' in check) and ('first_name' in check) and ('last_name' in check):
        return True
    else:
        return False


def download_photo(dir_name, url):
    file_name = url[url.rfind('/')+1:]
    resource = urlopen(url)
    out = open('%s/%s' % (dir_name, file_name), 'wb')
    out.write(resource.read())
    out.close()


def drop():
    sys.exit('Invalid commandline arguments')


def check_argv(num):
    try:
        if sys.argv[num]:
            drop()
    except Exception:
        pass


def help():
    print('\n\n *** -------------------------------------------------------- *** \n')
    print('This script allows you to dump all photos from albums of any vk user or group\n')
    print('\n List of commands examples:\n')
    print('" python photos.py help " --- Info about program and commandline arguments\n\n')
    print('" python photos.py auth login password " --- Authorizes user. Tel number must be w/o "+"')
    print('example: "python photos.py auth 79211234567 qwerty123456"\n\n')
    print('" python photos.py deauth " --- Deauthorizes current user\n\n')
    print('" python photos.py collect type id " --- Takes list of all photos. Type can only be "user" or "group". Id is user identifier in vk. You cannot use users domain, id must be a number. Creates a txt file with list of photos.')
    print('example: "python photos.py collect user 1234567" or "python photos.py collect group 7654321"\n\n')
    print('" python photos.py download list " --- Downloads collected list of photos. List is name of file, watch your script directory.')
    print('example: "python photos.py download user_1234567.txt" or "python photos.py download group_7654321.txt"\n\n')
    sys.exit('\n *** -------------------------------------------------------- *** \n\n')


request_interval = 0
file_with_token = 'token'

try:
    first_param = sys.argv[1]
except Exception:
    drop()

if (first_param != 'help') and (first_param != 'deauth') and (first_param != 'auth') and (first_param != 'collect') and (first_param != 'download'):
    drop()

if first_param == 'help':
    check_argv(2)
    help()

if first_param == 'deauth':
    check_argv(2)
    deauth()

if first_param == 'auth':
    try:
        second_param = sys.argv[2]
        third_param = sys.argv[3]
    except Exception:
        drop()
    check_argv(4)
    try:
        response = auth(second_param, third_param)
    except Exception:
        sys.exit('Auth failed')
    if 'error' in response:
        sys.exit('Error: %s' % response['error'])
    token = response['access_token']
    f = open(file_with_token, 'w')
    f.write('%s' % token)
    f.close()
    sys.exit('Auth successful')

if first_param == 'collect':
    try:
        second_param = sys.argv[2]
        if (second_param != 'group') and (second_param != 'user'):
            drop()
        third_param = sys.argv[3]
    except Exception:
        drop()
    check_argv(4)
    try:
        f = open(file_with_token, 'r')
        token = f.read()
        f.close()
    except Exception:
        sys.exit('Cannot read token. No user authorized.')
    try:
        verify = check_token(token)
    except Exception:
        pass
    if not verify:
        if 'access_token=' in token:
            pos = token.find('access_token=')
            pos +=13
            token = token[pos:]
            pos = token.find('&')
            token = token[:pos]
        secondary_verify = check_token(token)
        if not secondary_verify:
            sys.exit('not valid token')
    if second_param == 'user':
        uid = third_param
        file_name = 'user_%s.txt' % str(uid)
    elif second_param == 'group':
        uid = '-%s' % third_param
        file_name = 'group_%s.txt' % str(uid)
    else:
        drop()
    create_file(file_name)
    get_photos(uid, token, file_name, f)

if first_param == 'download':
    try:
        second_param = sys.argv[2]
    except Exception:
        drop()
    check_argv(3)

    file_with_photos = second_param

    try:
        f = open(file_with_photos, 'r')
        photos_txt = f.read()
        f.close()
    except Exception:
        sys.exit('Cannot open file. Make sure to type correct file name.')

    directory_name = file_with_photos[:file_with_photos.rfind('.')]
    create_directory(directory_name)
    create_file('errors.txt')

    links = photos_txt.split('\n')
    links = links[:-1]
    total = len(links)

    for number, link in enumerate(links):
        print('downloading %s (%s of %s)' % (link, str(number+1), total))
        try:
            download_photo(directory_name, link)
        except Exception:
            print('failed to download %s' % link)
            f = open('errors.txt', 'a')
            f.write('%s\n' % link)
            f.close()