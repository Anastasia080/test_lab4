import pytest
import os
from api import PetFriendsClient

VALID_EMAIL = "nastya1@mail.ru"
VALID_PASS = "123"

# возвращает клиент API
@pytest.fixture(scope="session")
def api_client():
    return PetFriendsClient()

# выполняет аутентификацию и возвращает клиент с сохранённым API-ключом
@pytest.fixture(scope="session")
def auth_client(api_client):
    response = api_client.get_api_key(VALID_EMAIL, VALID_PASS)
    assert response.status_code == 200, "Не удалось получить API-ключ"
    assert api_client.api_key is not None, "API-ключ не сохранен в клиенте"
    return api_client

# Тестовые данные для питомца
@pytest.fixture
def new_pet_data():
    return {
        "name": "Барсик",
        "animal_type": "Кот",
        "age": 3
    }

# Тестовое фото
@pytest.fixture
def test_photo_path():
    # создаем тестовое изображение, если его нет
    photo_path = "test_photo.jpg"
    if not os.path.exists(photo_path):
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='red')
        img.save(photo_path)
    return photo_path

# Cоздает питомца без фото и возвращает его ID
@pytest.fixture
def created_pet(auth_client, new_pet_data):
    response = auth_client.create_pet_simple(**new_pet_data)
    assert response.status_code == 200
    pet_id = response.json().get('id')
    yield pet_id
    # удаляем питомца
    auth_client.delete_pet(pet_id)