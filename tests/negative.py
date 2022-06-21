from api import PetFriends
import os
import pytest
from settings import valid_email,valid_password,invalid_email,invalid_password
from requests_toolbelt.multipart.encoder import MultipartEncoder

pf = PetFriends()
def russian_chars():
   return 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'

def chinese_chars():
   return '的一是不了人我在有他这为之大来以个中上们'

def special_chars():
   return '|\\/!@#$%^&*()-_=+`~?"№;:[]{}'

def generate_string(n):
    return n*'x'

# проверяем возможность получения ключа c неверными параметрами
@pytest.mark.parametrize("email", ['', 'sva-yuliana@yandex.ru',generate_string(255), russian_chars(), chinese_chars(),
      special_chars(), '123'], ids=['empty string', 'uncorrect email','255 symbols', 'russian','chinese', 'specials', 'digit'])
@pytest.mark.parametrize("password", ['', '7Fevrulu7',generate_string(255), russian_chars(), chinese_chars(),
      special_chars(), '123'], ids= ['empty string', 'uncorrect password','255 symbols', 'russian','chinese', 'specials', 'digit'])
def test_get_api_key_for_invalid_email(email, password):
    status, result = pf.get_key(email, password)
    assert status == 403

# проверяем возможность добавления питомца с неверными параметрами
@pytest.mark.parametrize("auth_key", ['', '5354688569:AAEzsVM46oAIxt5V12juByoD_wtg1gFqNBY',generate_string(255), generate_string(1001),russian_chars(), chinese_chars(),
      special_chars(), '123'], ids=['empty string', 'uncorrect token','255 symbols','more 1000 symbols','russian','chinese', 'specials', 'digit'])
@pytest.mark.parametrize("name", [''], ids=['empty'])
@pytest.mark.parametrize("animal_type", [''], ids=['empty'])
@pytest.mark.parametrize("age",
                        ['', '-1', '0', '100', '1.5', '2147483647', '2147483648', special_chars(), russian_chars(),
                         russian_chars().upper(), chinese_chars()]
   , ids=['empty', 'negative', 'zero', 'greater than max', 'float', 'int_max', 'int_max + 1', 'specials',
          'russian', 'RUSSIAN', 'chinese'])
@pytest.mark.parametrize("pet_photo",
                        ['', 'testfile.txt', 'images/fedor.jpg']
   , ids=['empty', 'textfile', 'the file does not exist', ])
def test_add_new_pet_with_invalid_params(auth_key,name, animal_type, age, pet_photo):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 403

# проверяем возможность добавления питомца без фото с неверными параметрами
@pytest.mark.parametrize("auth_key", ['', '5354688569:AAEzsVM46oAIxt5V12juByoD_wtg1gFqNBY',generate_string(255), generate_string(1001),russian_chars(), chinese_chars(),
      special_chars(), '123'], ids=['empty string', 'uncorrect token','255 symbols','more 1000 symbols','russian','chinese', 'specials', 'digit'])
@pytest.mark.parametrize("name", [''], ids=['empty'])
@pytest.mark.parametrize("animal_type", [''], ids=['empty'])
@pytest.mark.parametrize("age",
                        ['', '-1', '0', '100', '1.5', '2147483647', '2147483648', special_chars(), russian_chars(),
                         russian_chars().upper(), chinese_chars()]
   , ids=['empty', 'negative', 'zero', 'greater than max', 'float', 'int_max', 'int_max + 1', 'specials',
          'russian', 'RUSSIAN', 'chinese'])
def test_add_new_pet_without_photo_whis_valid_key(auth_key,name, animal_type, age):
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
    assert status == 400

# проверяем возможность добавления фото питомца с неверными параметрами
@pytest.mark.parametrize("invalid_auth_key", ['', '5354688569:AAEzsVM46oAIxt5V12juByoD_wtg1gFqNBY',generate_string(255), generate_string(1001),russian_chars(), chinese_chars(),
      special_chars(), '123'], ids=['empty string', 'uncorrect token','255 symbols','more 1000 symbols','russian','chinese', 'specials', 'digit'])
@pytest.mark.parametrize("pet_photo",
                        ['', 'testfile.txt', 'images/fedor.jpg']
   , ids=['empty', 'textfile', 'the file does not exist', ])
def test_add_pet_photo(invalid_auth_key,pet_photo):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_key(valid_email, valid_password)
    # получаем список питомцев
    _, my_pets = pf.get_pet_list(auth_key, "my_pets")
    pet_id = my_pets['pets'][0]['id']
    if len(my_pets['pets']) > 0:  # проверяем, что в списке есть питомцы
        status, result = pf.add_pet_photo(invalid_auth_key, pet_id, pet_photo)
        data = MultipartEncoder(fields={'pet_photo': (pet_photo, open(pet_photo, 'rb'), 'image/jpeg')
                                        })  # записываем в переменную битовый код фотографии с компьютера
        assert status == 400

# проверяем возможность удаления питомца с неверными параметрами
@pytest.mark.parametrize("invalid_auth_key", ['', '5354688569:AAEzsVM46oAIxt5V12juByoD_wtg1gFqNBY',generate_string(255), generate_string(1001),russian_chars(), chinese_chars(),
      special_chars(), '123'], ids=['empty string', 'uncorrect token','255 symbols','more 1000 symbols','russian','chinese', 'specials', 'digit'])
@pytest.mark.parametrize("pet_id", ['',1234567890,generate_string(255) ], ids=['empty string', 'uncorrect id','string with 255 symbols'])
def test_successful_delete_self_pet_with_invalid_params(invalid_auth_key,pet_id):
    #получаем действующий токен и с ним получаем список животных
    _, auth_key = pf.get_key(valid_email, valid_password)
    _, my_pets = pf.get_pet_list(auth_key,
                                 "my_pets")  # запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:  # если у меня нет никаких питомцев, добавляем питомца
        pf.add_new_pet(auth_key, 'Жора', 'горный козел', 5, 'images/zhora.jpg')
        _, my_pets = pf.get_pet_list(auth_key, "my_pets")  # снова получаем список питомцев - он будет один
    status, _ = pf.delete_pet(invalid_auth_key,pet_id)  # получаем статус-код ответа на запрос удаления питомца с испорченным ключом
    assert status == 403
    # проверяем, что id питомца остался в базе
    for i in my_pets['pets']:
        assert pet_id in i.values()

# проверяем возможность обновления питомца с неверными параметрами
@pytest.mark.parametrize("invalid_auth_key", ['', '5354688569:AAEzsVM46oAIxt5V12juByoD_wtg1gFqNBY',generate_string(255), generate_string(1001),russian_chars(), chinese_chars(),
      special_chars(), '123'], ids=['empty string', 'uncorrect token','255 symbols','more 1000 symbols','russian','chinese', 'specials', 'digit'])
@pytest.mark.parametrize("name", [''], ids=['empty'])
@pytest.mark.parametrize("animal_type", [''], ids=['empty'])
@pytest.mark.parametrize("age",
                        ['', '-1', '0', '100', '1.5', '2147483647', '2147483648', special_chars(), russian_chars(),
                         russian_chars().upper(), chinese_chars()]
   , ids=['empty', 'negative', 'zero', 'greater than max', 'float', 'int_max', 'int_max + 1', 'specials',
          'russian', 'RUSSIAN', 'chinese'])
def test_update_pet(invalid_auth_key,name, animal_type, age):
    _, auth_key = pf.get_key(valid_email, valid_password)
    _, my_pets = pf.get_pet_list(auth_key, "my_pets")  # получаем список питомцев c корректным ключом
    if len(my_pets['pets']) > 0:  # проверяем, есть ли животные в моем списке
        status, result = pf.update_pet_info(invalid_auth_key, my_pets['pets'][0]['id'], name, animal_type,
                                            age)  # выполняем метод обновления инфы

        assert status == 400


