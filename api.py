import requests
from requests import Response
import os

BASE_URL = "https://petfriends.skillfactory.ru"

# Клиент для работы с PetFriends API
class PetFriendsClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()

        # базовые заголовки
        self.session.headers.update({
            'accept': 'application/json',
            'Content-Type': 'application/json'
        })
        self.api_key = None # ключ

    # Автоматически добавляет API-ключ в заголовки, если он известен
    def _request(self, method: str, endpoint: str, **kwargs) -> Response:
        url = f"{self.base_url}{endpoint}"
    
        # Берем заголовки из сессии как основу
        headers = self.session.headers.copy()
        
        # Если есть дополнительные заголовки в kwargs, добавляем их
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']
        
        # Если ключ получен, добавляем его в заголовки
        if self.api_key:
            headers['auth_key'] = self.api_key
        
        # Выполняем запрос с объединенными заголовками
        response = self.session.request(method, url, headers=headers, **kwargs)
        return response

    
    # --- Методы API ---

    # GET /api/key - получение API-ключа
    def get_api_key(self, email: str, password: str) -> Response:
        # Временные заголовки только для этого запроса
        request_headers = {
            'email': email,
            'password': password,
            'accept': 'application/json'
        }
        
        # Выполняем запрос через _request для единообразия
        response = self._request("GET", "/api/key", headers=request_headers)
        
        # Если ключ получен успешно, сохраняем его в клиенте
        if response.status_code == 200:
            try:
                self.api_key = response.json().get('key')
                print(f"DEBUG: Получен API ключ: {self.api_key}")
            except Exception as e:
                print(f"DEBUG: Ошибка при парсинге ответа: {e}")
        
        return response

    # GET /api/pets - получение списка питомцев
    def get_pets(self, filter: str = 'my_pets') -> Response:
        params = {'filter': filter}
        return self._request("GET", "/api/pets", params=params)

    #  POST /api/create_pet_simple - добавление информации о новом питомце без фото
    def create_pet_simple(self, name: str, animal_type: str, age: int) -> Response:
        data = {
            'name': name,
            'animal_type': animal_type,
            'age': age
        }
        # для этого запроса Content-Type должен быть application/json
        return self._request("POST", "/api/create_pet_simple", json=data)

    # POST /api/pets - добавление питомца с фото
    def create_pet(self, name: str, animal_type: str, age: int, pet_photo_path: str) -> Response:
        data = {
            'name': name,
            'animal_type': animal_type,
            'age': age
        }
        # Файл для загрузки
        files = {'pet_photo': open(pet_photo_path, 'rb')}
        original_content_type = self.session.headers.pop('Content-Type', None)
        response = self._request("POST", "/api/pets", data=data, files=files)
        # Возвращаем заголовок, если он был
        if original_content_type:
            self.session.headers.update({'Content-Type': original_content_type})
        return response

    #POST /api/pets/set_photo/{pet_id} - добавление фото существующему питомцу
    def set_photo(self, pet_id: str, pet_photo_path: str) -> Response:
        files = {'pet_photo': open(pet_photo_path, 'rb')}
        original_content_type = self.session.headers.pop('Content-Type', None)
        response = self._request("POST", f"/api/pets/set_photo/{pet_id}", files=files)
        if original_content_type:
            self.session.headers.update({'Content-Type': original_content_type})
        return response

    # DELETE /api/pets/{pet_id} - удаление питомца
    def delete_pet(self, pet_id: str) -> Response:
        return self._request("DELETE", f"/api/pets/{pet_id}")

    # PUT /api/pets/{pet_id} - обновление информации о питомце
    def update_pet(self, pet_id: str, name: str, animal_type: str, age: int) -> Response:
        data = {
            'name': name,
            'animal_type': animal_type,
            'age': age
        }
        return self._request("PUT", f"/api/pets/{pet_id}", json=data)