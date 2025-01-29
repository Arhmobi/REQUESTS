import requests
import configparser
import json
from tqdm import tqdm

def writing_file(n_1, n_2):
    """Записываю в файл данные по фоткам."""
    json_data = {n_1: n_2}
    try:
        with open("info.json", 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []
    data.append(json_data)
    with open("info.json", 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

config = configparser.ConfigParser()
config.read('settings.ini')
vk_token = config['TOKEN']['token']
ya_disk = config['TOKEN']['ydisk_token']

class VK:
    def __init__(self, token, version='5.199'):
        self.params = {
            'access_token': token,
            'v': version
        }
        self.baseurl = 'https://api.vk.com/method/'

    def photo_get(self, user_id, ya_disk_uploader, count=5):
        """Получаю фотографии из профиля VK."""
        with open('info.json', 'w') as f:   # создаю файл для информации
            f.write(json.dumps([], indent=2, ensure_ascii=False))
        url = f"{self.baseurl}photos.get"
        params = {
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1,
            'count': count
        }
        params.update(self.params)
        try:
            response = requests.get(url, params=params).json()
            if 'error' in response:
                print(f"Ошибка VK API: {response['error']['error_msg']}")
                return
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к VK API: {e}")
            return

        for i in tqdm(response['response']['items']):
            url_foto = i['sizes'][-1]['url']  # Используем URL фотографии максимального размера
            likes_photo = i['likes']['count']
            file_image = f"{likes_photo}_likes.jpg"
            writing_file('File_name', file_image)  # записываю в файл результат на каждой итерации
            ya_disk_uploader.upload_file(url_foto, file_image)

class YandexDiskUploader:
    def __init__(self, ya_disk_token):
        """Инициализация класса с токеном Яндекс.Диска."""
        self.ya_disk_token = ya_disk_token
        self.headers = {
            'Authorization': self.ya_disk_token
        }

    def create_folder(self, folder_name):
        """Создание папки на Яндекс.Диске."""
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {
            'path': folder_name
        }
        try:
            response = requests.put(url, params=params, headers=self.headers)
            if response.status_code == 201:
                print(f"Папка '{folder_name}' успешно создана на Яндекс.Диске.")
            elif response.status_code == 409:
                print(f"Папка '{folder_name}' уже существует.")
            else:
                print(f"Ошибка при создании папки: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при создании папки: {e}")

    def upload_file(self, file_url, file_name, folder_name='PhotoS_VK'):
        """Загрузка файла на Яндекс.Диск."""
        # Создаем папку, если она еще не существует
        self.create_folder(folder_name)

        # Получаем URL для загрузки файла
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        params = {
            'path': f'{folder_name}/{file_name}',
            'overwrite': 'true'
        }
        try:
            response = requests.get(url, params=params, headers=self.headers)
            upload_url = response.json().get('href')
            if upload_url:
                # Загружаем файл
                file_response = requests.get(file_url)
                upload_response = requests.put(upload_url, data=file_response.content)
                if upload_response.status_code == 201:
                    print(f"Файл '{file_name}' успешно загружен в папку '{folder_name}'.")
                else:
                    print(f"Ошибка при загрузке файла: {upload_response.status_code}")
            else:
                print("Не удалось получить URL для загрузки файла.")
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при загрузке файла: {e}")

# Основной код
user_input = int(input('Введите ваш id: '))

# Создаем экземпляр YandexDiskUploader
ya_disk_uploader = YandexDiskUploader(ya_disk)

# Создаем экземпляр VK и передаем ему YandexDiskUploader
vk = VK(vk_token)
vk.photo_get(user_input, ya_disk_uploader)