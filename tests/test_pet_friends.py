from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password
import os
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import pytest
from datetime import datetime

pf = PetFriends()

@pytest.fixture(autouse=True)
def time_delta():
    start_time = datetime.now()
    yield
    end_time = datetime.now()
    print (f"\nТест шел: {end_time - start_time}")

#проверка возможности получения ключа с корректными логином и паролем
def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    status, result = pf.get_key(email, password)
    assert status == 200
    assert 'key' in result

@pytest.fixture(scope="function")
def get_key(request):
    response = requests.post(url='https://petfriends1.herokuapp.com/login',
                             data={"email": valid_email, "pass": valid_password})
    assert response.status_code == 200, 'Запрос выполнен неуспешно'
    assert 'Cookie' in response.request.headers, 'В запросе не передан ключ авторизации'
    print("\nreturn auth_key")
    return response.request.headers.get('Cookie')

@pytest.mark.pozitive
def test_get_pet_list_with_valid_key(get_key):
    response = requests.get(url='https://petfriends1.herokuapp.com/api/pets',
                            headers={"Cookie": get_key})
    assert response.status_code == 200
    assert len(response.json().get('pets')) > 0

@pytest.mark.pozitive
def test_add_new_pet_with_valid_key(name='Жора', animal_type='горный козел', age='5', pet_photo='images/zhora.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 200
    assert result['name'] == name

@pytest.mark.pozitive
def test_test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""
    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_key(valid_email, valid_password)
    _, my_pets = pf.get_pet_list(auth_key, "my_pets")
    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    _, auth_key = pf.get_key(valid_email, valid_password)
    _, my_pets = pf.get_pet_list(auth_key,
                                 "my_pets")  # Получаем правильный ключ auth_key и запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:  # если у меня нет никаких питомцев, добавляем питомца
        pf.add_new_pet(auth_key, 'Жора', 'горный козел', 5, 'images/zhora.jpg')
        _, my_pets = pf.get_pet_list(auth_key, "my_pets")  # снова получаем список питомцев - он будет один

    pet_id = my_pets['pets'][0]['id']  # достаем идентификатор последнего добавленного питомца - через словарь
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_pet_list(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    for i in my_pets['pets']:
        assert pet_id not in i.values()

@pytest.mark.pozitive
def test_update_pet(name='Рюрик', animal_type='баран', age='6'):
    _, auth_key = pf.get_key(valid_email, valid_password)  # получаем ключ
    _, my_pets = pf.get_pet_list(auth_key, "my_pets")  # получаем список питомцев
    if len(my_pets['pets']) > 0:  # проверяем, есть ли животные в моем списке
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type,
                                            age)  # выполняем метод обновления инфы

        assert status == 200
        assert result['name'] == name
    else:
        raise Exception("There is no my pets")

@pytest.mark.pozitive
def test_add_new_pet_without_photo_whis_valid_key(name='Игорь', animal_type='Баран', age='7'):
    _, auth_key = pf.get_key(valid_email, valid_password)  # Запрашиваем ключ api и сохраняем в переменую auth_key
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
    assert status == 200
    assert result['name'] == name

@pytest.mark.pozitive
def test_add_pet_photo(pet_photo='images/Igor.jpg'):
    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_key(valid_email, valid_password)
    # получаем список питомцев
    _, my_pets = pf.get_pet_list(auth_key, "my_pets")
    pet_id = my_pets['pets'][0]['id']
    if len(my_pets['pets']) > 0:  # проверяем, что в списке есть питомцы
        status, result = pf.add_pet_photo(auth_key, pet_id, pet_photo)
        data = MultipartEncoder(fields={'pet_photo': (pet_photo, open(pet_photo, 'rb'), 'image/jpeg')
                                        })  # записываем в переменную битовый код фотографии с компьютера
        assert status == 200
        assert data == result[
            'pet_photo']  # сравниваем битовый код фотографии с компьютера с кодом фотографии на сервере
    else:
        raise Exception("There is no my pets")


# проверяем возможность входа с неверным логином
@pytest.mark.negative
def test_get_api_key_for_invalid_email(email=invalid_email, password=valid_password):
    status, result = pf.get_key(email, password)
    assert status == 403

# проверяем возможность входа с неверным паролем
@pytest.mark.negative
def test_get_api_key_for_invalid_password(email=valid_email, password=invalid_password):
    status, result = pf.get_key(email, password)
    assert status == 403

# проверяем возможность добавления питомца с неверным ключом
@pytest.mark.negative
def test_add_new_pet_with_invalid_key(name='Жора', animal_type='горный козел', age='5', pet_photo='images/zhora.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_key(valid_email, valid_password)
    auth_key = auth_key + 'a'
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 403

    # проверяем возможность удаления питомца с неверным ключом
@pytest.mark.negative
def test_successful_delete_self_pet_with_invalid_key():
    _, auth_key = pf.get_key(valid_email, valid_password)
    _, my_pets = pf.get_pet_list(auth_key,
                                 "my_pets")  # Получаем правильный ключ auth_key и запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:  # если у меня нет никаких питомцев, добавляем питомца
        pf.add_new_pet(auth_key, 'Жора', 'горный козел', 5, 'images/zhora.jpg')
        _, my_pets = pf.get_pet_list(auth_key, "my_pets")  # снова получаем список питомцев - он будет один
    pet_id = my_pets['pets'][0]['id']  # достаем идентификатор последнего добавленного питомца - через словарь
    auth_key = auth_key + 'a'  # "портим" ключ
    status, _ = pf.delete_pet(auth_key,pet_id)  # получаем статус-код ответа на запрос удаления питомца с испорченным ключом
    assert status == 403
    # проверяем, что id питомца остался в базе
    for i in my_pets['pets']:
        assert pet_id in i.values()

# проверяем возможность добавления питомца без имени
@pytest.mark.negative
def test_add_new_pet_without_name(animal_type='горный козел', age='5', pet_photo='images/zhora.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, animal_type, age, pet_photo)
    assert status == 400

# проверяем возможность добавления питомца без типа
@pytest.mark.negative
def test_add_new_pet_without_animal_type(name='Жора', age='5', pet_photo='images/zhora.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, age, pet_photo)
    assert status == 400

# проверяем возможность добавления питомца без возраста
@pytest.mark.negative
def test_add_new_pet_without_age(name='Жора', animal_type='горный козел', pet_photo='images/zhora.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, pet_photo)
    assert status == 400

# проверяем возможность добавления питомца, с очень длинным именем
@pytest.mark.negative
def test_add_new_pet_with_long_name_lengt(name='Жора' * 100000, animal_type='горный козел', age='5',
                                          pet_photo='images/zhora.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 400

# проверяем возможность добавления питомца, с очень длинным типом
@pytest.mark.negative
def test_add_new_pet_with_long_animal_type_lengt(name='Жора', animal_type='горный козел' * 100000, age='5',
                                                 pet_photo='images/zhora.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 400

# проверяем возможность добавления питомца, с очень длинным возрастом
@pytest.mark.negative
def test_add_new_pet_with_long_age_lengt(name='Жора', animal_type='горный козел', age='5' * 1000000,
                                         pet_photo='images/zhora.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 400

# проверяем возможность добавления питомца, если такого фото в директории не существует
@pytest.mark.negative
def test_add_new_pet_with_invalid_photo(name='Федор', animal_type='лось', age='6', pet_photo='images/fedor.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 400
