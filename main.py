
import requests
import configparser
import os

congig = configparser.ConfigParser()
congig.read('settings.ini')
vk_token = congig['TOKEN']['token']
ya_disk = congig['TOKEN']['ydisk_token']
photos_dict = {}
class VK:
    def __init__(self, token, version=5.199):
        self.params = {
            'access_token': token,
            'v': version
        }
        self.baseurl = 'https://api.vk.com/method/'

    def photo_get(self, user_id, count=5):
        url = f"{self.baseurl}photos.get"
        params = {
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1,
            'count': count
        }
        params.update(self.params)
        response = requests.get(url, params=params).json()
        # if not os.path.exists('images_vk'):
        #     os.mkdir('images_vk')
        for i in response['response']['items']:
            url_foto = i['orig_photo']['url']
            likes_photo = i['likes']['count']
            if likes_photo >= 1:
                file_image = f"{likes_photo}_likes.jpg"
                with open('images_vk/'f"{file_image}", 'wb') as f:
                    response = requests.get(url_foto)
                    f.write(response.content)
                url_yad = 'https://cloud-api.yandex.net/v1/disk/resources' # создаю папку на яндекс диске
                params = {
                    'path': 'PhotoS_VK'
                }
                headers = {
                    'Authorization': ya_disk
                }
                response = requests.put(url_yad, params=params, headers=headers)

                url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
                headers = {'Content-Type': 'application/json',
                           'Authorization': ya_disk}
                params = {'path': f'PhotoS_VK/{file_image}',
                          'overwrite': 'true'}
                response = requests.get(url, params=params, headers=headers)
                upload_url = response.json()['href']
                url = url_foto
                r = requests.get(url)
                requests.put(url=upload_url, data=r)

vk = VK(vk_token)
vk.photo_get(76261581)