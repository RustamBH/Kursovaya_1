import json
import requests
import sys
import errno
import logging

from ya_disk import YaUploader
from datetime import datetime
from tqdm import tqdm
from time import sleep

VK_TOKEN = ''
YA_TOKEN = ''
VK_VERSION = '5.131'

logging.basicConfig(filename='exception.log', level=logging.INFO)
logger = logging.getLogger('ex')


def id_get_request(vk_name):
    try:
        url = "https://api.vk.com/method/users.get?"
        url += f"&access_token={VK_TOKEN}"
        url += f"&v={VK_VERSION}"
        params = None
        response = requests.get(url=url, params=params, timeout=5)
        response.raise_for_status()
        user_id = response.json().get('response')[0].get('id')
        return user_id
    except ConnectionError as e:
        logger.exception("ERROR: HTTP connection")
        sys.exit(errno.ECONNABORTED)
    except requests.ConnectTimeout as e:
        logger.exception("ERROR: HTTP connection timeout")
        sys.exit(errno.ETIMEDOUT)
    except Exception as e:
        logger.exception("ERROR:" + str(e))
        sys.exit(1)


def photo_get_request(id_client):
    try:
        url = "https://api.vk.com/method/photos.get?"
        url += f"&access_token={VK_TOKEN}"
        url += f"&v={VK_VERSION}"
        params = {
            'owner_id': f'{id_client}',
            'album_id': 'profile',
            'extended': 1,
        }
        response = requests.get(url=url, params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except ConnectionError as e:
        logger.exception("ERROR: HTTP connection")
        sys.exit(errno.ECONNABORTED)
    except requests.ConnectTimeout as e:
        logger.exception("ERROR: HTTP connection timeout")
        sys.exit(errno.ETIMEDOUT)
    except Exception as e:
        logger.exception("ERROR:" + str(e))
        sys.exit(1)


def get_profile_photos(usr_items_list):
    max_profile_photo_list = []
    user_params_list = []
    for item in usr_items_list:
        photo_params_dict = {}        
        photo_params_dict['id'] = item['id']
        photo_params_dict['date'] = item['date']
        photo_params_dict['user_likes'] = item['likes']['count']
        user_params_list.append(item['likes']['count'])
        photo_params_list = item['sizes']

        max_size = max([photo_sz_dict['height'] * photo_sz_dict['width'] for photo_sz_dict in photo_params_list
                        if photo_sz_dict['height'] > 0 and photo_sz_dict['width'] > 0])
        for photo_param in photo_params_list:
            if photo_param['height'] > 0 and photo_param['width'] > 0:
                if photo_param['height'] * photo_param['width'] == max_size:                    
                    photo_params_dict['url'] = photo_param['url']
                    photo_params_dict['height'] = photo_param['height']
                    photo_params_dict['width'] = photo_param['width']
                    break
        max_profile_photo_list.append(photo_params_dict)
    return max_profile_photo_list, user_params_list


def upload_files(photos_max_profile_list, users_param_list, n_photos=5):
    log_upload_files_list = []
    if n_photos < len(photos_max_profile_list):
        photos_max_profile_list = photos_max_profile_list[:n_photos]

    for photo_profile in tqdm(photos_max_profile_list):
        log_file_dict = {}
        if 'url' in photo_profile:
            url_photo = photo_profile['url']
            count_likes = users_param_list.count(photo_profile['user_likes'])
            if count_likes > 1:
                timestamp = photo_profile['date']
                current_date_string = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d_%H-%M-%S')
                filename = str(photo_profile['user_likes']) + f"_{current_date_string}"
            else:
                filename = str(photo_profile['user_likes'])
            log_file_dict['file_name'] = filename + ".jpg"
            log_file_dict['size'] = str(photo_profile['width'] * photo_profile['height'])
            log_upload_files_list.append(log_file_dict)
            uploader = YaUploader(token=YA_TOKEN)
            result = uploader.upload_url_to_disk(url_photo, filename)
    sleep(0.1)
    return log_upload_files_list


if __name__ == '__main__':
    vk_user_id = int(input('Введите id пользователя: '))

    # вариант с тестовым аккаунтом https://vk.com/begemot_korovin
    # vk_username = "begemot_korovin"
    # vk_user_id = id_get_request(vk_username)
    count_photos = 5
    user_items_list = photo_get_request(vk_user_id)['response']['items']
    photo_max_profile_list, user_param_list = get_profile_photos(user_items_list)    
    log_upload_files_json_list = upload_files(photo_max_profile_list, user_param_list, count_photos)
    
    with open('log_upload_files.json', 'w') as json_file:
        json.dump(log_upload_files_json_list, json_file, ensure_ascii=False, indent=4)
