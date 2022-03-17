import requests
import sys
import errno
import logging

logging.basicConfig(filename='exception.log', level=logging.INFO)
logger = logging.getLogger('ex')


class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def _get_upload_link(self, disk_file_path: str):
        try:
            upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
            headers = self.get_headers()
            params = {"path": disk_file_path, "overwrite": "true"}
            response = requests.get(upload_url, headers=headers, params=params)
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

    def _create_folder(self, dir_name: str):
        try:
            upload_url = "https://cloud-api.yandex.net/v1/disk/resources/"
            headers = self.get_headers()
            params = {"path": dir_name, "overwrite": "true"}
            response = requests.put(upload_url, headers=headers, params=params)
            return response.status_code
        except ConnectionError as e:
            logger.exception("ERROR: HTTP connection")
            sys.exit(errno.ECONNABORTED)
        except requests.ConnectTimeout as e:
            logger.exception("ERROR: HTTP connection timeout")
            sys.exit(errno.ETIMEDOUT)
        except Exception as e:
            logger.exception("ERROR:" + str(e))
            sys.exit(1)

    def upload(self, file_path: str):
        try:
            """Метод загружает файлы по списку file_list на яндекс диск"""
            disk_file_path = "netology/upload.txt"
            dir_name = disk_file_path.rstrip(file_path)
            resp = self._create_folder(dir_name=dir_name)
            href = self._get_upload_link(disk_file_path=disk_file_path).get("href", "")
            response = requests.put(href, data=open(file_path, 'rb'))
            response.raise_for_status()
        except ConnectionError as e:
            logger.exception("ERROR: HTTP connection")
            sys.exit(errno.ECONNABORTED)
        except requests.ConnectTimeout as e:
            logger.exception("ERROR: HTTP connection timeout")
            sys.exit(errno.ETIMEDOUT)
        except Exception as e:
            logger.exception("ERROR:" + str(e))
            sys.exit(1)

    def upload_url_to_disk(self, url_photo: str, filename: str):
        try:
            dir_name = "vk_profile"
            resp = self._create_folder(dir_name=dir_name)
            upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
            headers = self.get_headers()
            disk_file_path = dir_name + "/" + filename + ".jpg"
            params = {"path": disk_file_path, "url": url_photo}
            response = requests.post(url=upload_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
        except ConnectionError as e:
            logger.exception("ERROR: HTTP connection")
            sys.exit(errno.ECONNABORTED)
        except requests.ConnectTimeout as e:
            logger.exception("ERROR: HTTP connection timeout")
            sys.exit(errno.ETIMEDOUT)
        except Exception as e:
            logger.exception("ERROR:" + str(e))
            sys.exit(1)
