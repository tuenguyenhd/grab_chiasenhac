import cookielib
import re
import sys
import requests
import hashlib
import json
import urllib
import smtplib
from datetime import datetime
import time
import os
from urlparse import urlparse
from os.path import splitext, basename

def check_m4a(url):
    url = url.replace('[MP3%20320kbps].mp3', '[M4A%20500kbps].m4a')
    url = url.replace('[MP3 320kbps].mp3', '[M4A 500kbps].m4a')
    url = url.replace('/320/', '/m4a/')
    r = requests.head(url)    
    if (r.status_code == requests.codes.ok):
        return url
    else:
        return None
    

def download_file(url):
    print url
    url2=urllib.unquote(url).decode('utf8')     
    local_filename = url2.split('/')[-1]    
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
    return local_filename

def get_extension_url(url):
    disassembled = urlparse(url)    
    filename, file_ext = splitext(basename(disassembled.path))
    return file_ext

def grab_m4a(url):    
    result = requests.get(url)
    urls = re.findall(r'href=[\'"]?([^\'">]+)', result.text)
    for url in urls:
        if (get_extension_url(url) == '.mp3' and (('320kbps' in url) or ('128kbps'))):
            m4a_url = check_m4a(url)
            if (m4a_url != None):
                download_file(m4a_url)
            else:                
                download_file(url)

def unique(seq):
    seen = set()
    return [seen.add(x) or x for x in seq if x not in seen]
            
if len(sys.argv) > 1:
    url = sys.argv[1]
    multiple_file = True
    if (len(sys.argv) > 2):
        multiple_file = False
    result = requests.get(url)
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+~/\[//\]/]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', result.text)    
    urls = unique(urls)
    for url in urls:
        download_url = re.search('http://download.chiasenhac.com/mp3', url, re.IGNORECASE)
        if (download_url != None):            
            grab_m4a(url)
            if (multiple_file != True):
                break
else:
    print 'usage: python download.py album_link'