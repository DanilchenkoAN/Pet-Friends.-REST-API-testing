import requests
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder

class PetFriends:
    def __init__(self):
        self.base_url='https://petfriends.skillfactory.ru/'

    def get_key(self,email,password):
        """Метод делает запрос к API сервера и возвращает статус запроса, а также в формате json уникальный ключ пользователя
        который входит с определенным логином и паролем"""
        headers={      # вводим словарь с заголовками запроса - логином и паролем
            'email':email,
            'password':password
        }
        res=requests.get(self.base_url+'api/key',headers=headers)
        status=res.status_code
        result=''
        try:
            result=res.json()
        except:
            result=res.text
        return status,result

    def get_pet_list(self,auth_key,filter):
        """Метод делает запрос к серверу API и возвращает статус запроса и результат в формате JSON
        с питомцами, совпадающими с фильтром. На данный момент фильтр может иметь
        либо пустое значение - получить список всех питомцев, либо 'my_pets' - получить список
        возможно питомцев"""
        headers={'auth_key':auth_key['key']}
        filter={'filter':filter}
        res=requests.get(self.base_url+'api/pets',headers=headers,params=filter)
        status = res.status_code
        result = ''
        try:
            result = res.json()
        except:
            result = res.text
        return status, result

    def add_new_pet(self,auth_key:json,name,animal_type,age,pet_photo)->json:
        """Метод отправляет (постит) на сервер данных о загрузке питомце и возвращает статус
                запрос на сервер и результат в формате JSON с данными добавленного питомца"""
        # заводим словарь с данными питомца, котрого хотим добавить
        data = MultipartEncoder(
            fields={
                'name': name,
                'animal_type': animal_type,
                'age': age,
                'pet_photo': (pet_photo, open(pet_photo, 'rb'), 'image/jpeg')
            })
        headers={'auth_key':auth_key['key'],'Content-Type': data.content_type}  # передаем формат данных объекта data в ключ Content-Type:
        res=requests.post(self.base_url+'api/pets',headers=headers,data=data)  # запрос на добавление данных с заголовками (ключ) и данными
        status = res.status_code
        result=''
        try:
            result = res.json()
        except:
            result = res.text
        return status, result

    def delete_pet(self,auth_key:json,pet_id:str):
        """Метод отправляет на сервер запрос на удаление питомца по указанному ID и возвращает
                статус запроса и результат в формате JSON с текстом соглашения о успешном удалении.
                На сегодняшний день тут есть баг - в результате приходит пустая строка, но статус при этом = 200"""
        headers = {'auth_key': auth_key['key']}
        res=requests.delete(self.base_url+'api/pets/'+pet_id,headers=headers)
        status = res.status_code
        result=''
        try:
            result = res.json()
        except:
            result = res.text
        return status, result

    def update_pet_info(self,auth_key:json,pet_id:str,name,animal_type,age):
        """Метод отправляет запрос на сервер о обновлении данных питомца по указанному идентификатору и
                возвращает статус запроса и результат в формате JSON с обновлёнными данными питомца"""
        # вводим словарь данных, которые хотим обновить у питомца
        data = {
                'name': name,
                'animal_type': animal_type,
                'age': age,
            }
        headers = {'auth_key': auth_key['key']}
        res = requests.put(self.base_url+'api/pets/'+pet_id,headers=headers,data=data)
        status = res.status_code
        result = ''
        try:
            result = res.json()
        except:
            result = res.text
        return status, result
    
    def add_new_pet_without_photo(self,auth_key:json,name,animal_type,age):
        """Метод отправляет (постит) на сервер данных о загрузке питомца без фото и возвращает статус
         ответа и результат в формате JSON с данными добавленного питомца"""
        data = {
                'name': name,
                'animal_type': animal_type,
                'age': age
            }
        headers = {'auth_key': auth_key['key']}
        res = requests.post(self.base_url + 'api/create_pet_simple', headers=headers,
                            data=data)  # запрос на добавление данных с заголовками (ключ) и данными
        status = res.status_code
        try:
            result = res.json()
        except:
            result = res.text
        return status, result

    def add_pet_photo(self,auth_key:json,pet_id,pet_photo):
        data = MultipartEncoder(
            fields={
                'pet_photo': (pet_photo, open(pet_photo, 'rb'), 'image/jpeg')
            })
        headers = {'auth_key': auth_key['key'], 'Content-Type': data.content_type}
        res=requests.post(self.base_url+'api/pets/set_photo/'+pet_id,headers=headers,data=data)
        status = res.status_code
        try:
            result = res.json()
        except:
            result = res.text
        return status, result

