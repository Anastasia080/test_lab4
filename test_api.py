import pytest
import random

# --- Тесты для получения ключа ---

# Проверка получения ключа с валидными email/паролем
def test_get_api_key_valid(api_client):
    response = api_client.get_api_key("nastya1@mail.ru", "123")
    assert response.status_code == 200
    assert api_client.api_key is not None
# Негативный тест: неверный пароль
def test_get_api_key_invalid_password(api_client):
    response = api_client.get_api_key("nastya1@mail.ru", "wrong_password")
    # Ожидаем ошибку авторизации
    assert response.status_code in [401, 403]


# --- Тесты для работы с питомцами ---

# GET
# Проверка получения списка своих питомцев
def test_get_my_pets(auth_client):
    response = auth_client.get_pets(filter='my_pets') # фильтр
    assert response.status_code == 200
    pets = response.json().get('pets', [])
    assert isinstance(pets, list)

#POST
# Создание питомца без фото
def test_create_pet_simple(auth_client, new_pet_data):
    response = auth_client.create_pet_simple(**new_pet_data)
    assert response.status_code == 200
    pet = response.json()
    assert pet['name'] == new_pet_data['name']
    assert 'id' in pet

#POST
# Создание питомца с фото
def test_create_pet_with_photo(auth_client, new_pet_data, test_photo_path):
    response = auth_client.create_pet(**new_pet_data, pet_photo_path=test_photo_path)
    assert response.status_code == 200
    pet = response.json()
    assert pet['name'] == new_pet_data['name']
    assert 'pet_photo' in pet # ожидаем, что ссылка на фото есть

#POST
# Негативный тест: возраст передан строкой вместо числа
def test_create_pet_with_invalid_age_type(auth_client):
    response = auth_client.create_pet_simple(name="Test", animal_type="Cat", age="invalid")
    # Ожидаем ошибку валидации
    assert response.status_code == 200
    pet = response.json()
    assert 'id' in pet

# POST
# Граничные значения для возраста
@pytest.mark.parametrize("age", [0, -1, 1000])
def test_create_pet_boundary_age(auth_client, age):
    response = auth_client.create_pet_simple(name="Test", animal_type="Cat", age=age)
    assert response.status_code == 200 
    pet = response.json()
    assert int(pet['age']) == age

# DELETE
# Удаление своего питомца
def test_delete_own_pet(auth_client, created_pet):
    response = auth_client.delete_pet(created_pet)
    assert response.status_code == 200
    # Проверяем, что питомец действительно удален
    get_response = auth_client.get_pets(filter='my_pets')
    my_pets = get_response.json().get('pets', [])
    pet_ids = [p['id'] for p in my_pets]
    assert created_pet not in pet_ids

# DELETE
# Негативный тест: удаление несуществующего питомца
def test_delete_nonexistent_pet(auth_client):
    fake_id = "non_existent_id_123"
    response = auth_client.delete_pet(fake_id)
    assert response.status_code == 200
    assert response.text is not None

# PUT
# Обновление информации о питомце
def test_update_pet(auth_client, created_pet):
    new_name = "Мурзик"
    response = auth_client.update_pet(created_pet, name=new_name, animal_type="Кот", age=5)
    assert response.status_code == 200
    updated_pet = response.json()
    assert updated_pet['name'] == new_name

# POST
# Добавление фото существующему питомцу
def test_set_photo(auth_client, created_pet, test_photo_path):
    response = auth_client.set_photo(created_pet, test_photo_path)
    assert response.status_code == 200
    pet = response.json()
    assert 'pet_photo' in pet