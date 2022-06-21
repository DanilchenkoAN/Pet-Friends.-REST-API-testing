from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password
import os
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import pytest

pf = PetFriends()

def russian_chars():
   return 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'

def chinese_chars():
   return '的一是不了人我在有他这为之大来以个中上们'

def special_chars():
   return '|\\/!@#$%^&*()-_=+`~?"№;:[]{}'

def generate_string(n):
    return n*'x'

@pytest.fixture(scope="module")
def get_api_key():
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""
    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_key(valid_email, valid_password)
    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result
    return result

@pytest.mark.parametrize("filter", ['', 'my_pets'], ids= ['empty string', 'only my pets'])
def test_get_all_pets_with_valid_key(filter):
   pytest.status, result = pf.get_pet_list(get_api_key, filter)
   assert len(result['pets']) > 0


@pytest.mark.parametrize("name"
   , [generate_string(255), generate_string(1001), russian_chars(), russian_chars().upper(), chinese_chars(),
      special_chars(), '123']
   , ids=['255 symbols', 'more than 1000 symbols', 'russian', 'RUSSIAN', 'chinese', 'specials', 'digit'])
@pytest.mark.parametrize("animal_type"
   , [generate_string(255), generate_string(1001), russian_chars(), russian_chars().upper(), chinese_chars(), special_chars(), '123']
   , ids=['255 symbols', 'more than 1000 symbols', 'russian', 'RUSSIAN', 'chinese', 'specials', 'digit'])
@pytest.mark.parametrize("age", ['1'], ids=['min'])
@pytest.mark.parametrize("pet_photo", ['images\zhora.jpg'], ids=['photo'])
def test_add_new_pet_with_valid_key(name, animal_type, age, pet_photo):
    status, result = pf.add_new_pet(get_api_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert result['name'] == name

#проверяем возможность обновить информацию о питомце
@pytest.mark.parametrize("name"
   , [generate_string(255), generate_string(1001), russian_chars(), russian_chars().upper(), chinese_chars(),
      special_chars(), '123']
   , ids=['255 symbols', 'more than 1000 symbols', 'russian', 'RUSSIAN', 'chinese', 'specials', 'digit'])
@pytest.mark.parametrize("animal_type"
   , [generate_string(255), generate_string(1001), russian_chars(), russian_chars().upper(), chinese_chars(), special_chars(), '123']
   , ids=['255 symbols', 'more than 1000 symbols', 'russian', 'RUSSIAN', 'chinese', 'specials', 'digit'])
@pytest.mark.parametrize("age", ['1'], ids=['min'])
def test_update_pet(name,animal_type,age):
    _, auth_key = pf.get_key(valid_email, valid_password)
    _, my_pets = pf.get_pet_list(auth_key, "my_pets")  # получаем список питомцев
    if len(my_pets['pets']) > 0:  # проверяем, есть ли животные в моем списке
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type,
                                            age)  # выполняем метод обновления инфы

        assert status == 200
        assert result['name'] == name
    else:
        raise Exception("There is no my pets")

#проверяем возможность добавить фото питомца
@pytest.mark.parametrize("pet_photo", ['images\zhora.jpg'], ids= ['photo'])
def test_add_pet_photo(pet_photo):
    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    # получаем список питомцев
    _, my_pets = pf.get_pet_list(get_api_key, "my_pets")
    pet_id = my_pets['pets'][0]['id'] # получаем id питомца, которого будем удалять
    if len(my_pets['pets']) > 0:  # проверяем, что в списке есть питомцы
        status, result = pf.add_pet_photo(get_api_key, pet_id, pet_photo)
        assert status == 200
    else:
        raise Exception("There is no my pets")

# проверяем возможность удаления питомца
def test_successful_delete_self_pet_with_valid_params(get_api_key):
    _, my_pets = pf.get_pet_list(get_api_key,"my_pets")  # запрашиваем список своих питомцев

    if len(my_pets['pets']) == 0:  # если у меня нет никаких питомцев, добавляем питомца
        pf.add_new_pet(get_api_key, 'Жора', 'горный козел', 5, 'images\zhora.jpg')
        _, my_pets = pf.get_pet_list(get_api_key, "my_pets")  # снова получаем список питомцев - он будет один
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(get_api_key,pet_id)  # получаем статус-код ответа на запрос удаления питомца
    _, my_pets = pf.get_pet_list(get_api_key, "my_pets")
    assert status == 200
    # проверяем, что id питомца нет в базе, т.к. он удален
    for i in my_pets['pets']:
        assert pet_id not in i.values()

