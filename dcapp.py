from bs4 import BeautifulSoup
from collections import OrderedDict
from datetime import timedelta, datetime
from sc_exceptions import *
from sc_helpers import render_page
import re
import requests
import requests_cache

req_expire_after = timedelta(seconds=600)
cached_req_session = requests_cache.CachedSession('sc_cache', backend='sqlite', expire_after=req_expire_after)


def dc_app(path):
    """Get HQ pictures from DC app"""

    # request DC app webpage
    try:
        try:
            response = cached_req_session.get(path, timeout=30)
        except requests.exceptions.MissingSchema:
            path = 'https://' + path
            response = cached_req_session.get(path, timeout=30)
    except requests.exceptions.Timeout:
        raise DCAppError('Request timed out')

    if response.status_code != 200:
        raise DCAppError(f'Error code {response.status_code}')

    app_images = None
    app_video = None
    app_video_poster = None

    source = response.text
    parsed_html = BeautifulSoup(source, features='html.parser')

    # match image urls
    regex = r"((http://|https://)?file\.candlemystar\.com/cache/.*(_\d+x\d+)\.\w+)"

    try:
        # try to find video
        app_video = parsed_html.body.find('video').find('source').attrs['src']
        app_video_poster = parsed_html.body.find('video').attrs['poster']
    except:
        # find all images from app post
        images_html = ''.join([str(h) for h in parsed_html.body.find_all('div', attrs={'class': 'img-box'})])
        x = re.findall(regex, images_html)

        # create urls for full-size images
        files = []
        for url in x:
            temp = url[0]
            temp = temp.replace('cache/', '')
            temp = temp.replace('thumb-', '')
            temp = temp.replace(url[2], '')
            files.append(temp)

        # remove duplicates
        app_images = list(OrderedDict.fromkeys(files))

    # find post username and text
    app_poster = parsed_html.body.find('div', attrs={'class': 'card-name'}).text.strip()
    app_text = parsed_html.body.find('div', attrs={'class': 'card-text'}).text.strip()

    # find profile picture
    profile_pic = parsed_html.body.find('div', attrs={'class': 'profile-img'}).find('img').attrs['src']
    try:
        x = re.findall(regex, profile_pic)[0]
        temp = x[0]
        temp = temp.replace('cache/', '')
        temp = temp.replace('thumb-', '')
        temp = temp.replace(x[2], '')
        profile_pic = temp
    except Exception as e:
        print(f"Error getting full size profile picture {e}")

    kwargs = {}
    kwargs['app_video'] = app_video
    kwargs['app_video_poster'] = app_video_poster
    kwargs['app_images'] = app_images
    kwargs['app_poster'] = app_poster
    kwargs['app_text'] = app_text
    kwargs['profile_pic'] = profile_pic
    kwargs['url'] = path

    return render_page('dc_app.html', **kwargs)

def dc_app_image(path):
    """Get HQ version of DC app picture"""
    # verify link
    x = re.match(r"((http://|https://)?file\.candlemystar\.com/cache/.*(_\d+x\d+)\.\w+$)", path)
    if x is None:
        raise FullSizeDCAppImage
    else:
        # get full size image
        image_link = path.replace('cache/', '')
        image_link = image_link.replace('thumb-', '')
        image_link = image_link.replace(x.groups()[2], '')

        # request image link
        if False:
            try:
                response = cached_req_session.get(image_link, timeout=30)
            except requests.exceptions.MissingSchema:
                image_link = 'https://' + image_link
                response = cached_req_session.get(image_link, timeout=30)

            if response.status_code == 200:
                app_direct_image = True
            else:
                error_msg = 'Error: Image could not be found'
                raise InvalidDCAppLink


        app_images = f'<img class="app_img" src={image_link}>\n'

        kwargs = {}
        kwargs['image_link'] = image_link
        kwargs['url'] = path

        return render_page('dc_app_image.html', **kwargs)


