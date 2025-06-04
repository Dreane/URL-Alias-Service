# URL Alias Service

Сервис преобразования длинных URL в короткие уникальные URL.

## Требования

*   Python 3.10+
*   Flask
*   Flask-SQLAlchemy
*   Flask-HTTPAuth
*   Flask-Swagger-UI
*   Werkzeug

## Установка и запуск

### С использованием `Makefile`

1.  **Клонируйте репозиторий (если это репозиторий):**
    ```bash
    git clone https://github.com/Dreane/URL-Alias-Service
    cd URL-Alias-Service
    ```
2.  **Установите зависимости и создайте виртуальное окружение:**
    ```bash
    make install 
    ```

3.  **Создайте администратора:**
    После установки, активируйте виртуальное окружение, если оно еще не активно:
    ```bash
    # Для Windows
    venv\Scripts\activate
    # Для macOS/Linux
    source venv/bin/activate
    ```
    Затем выполните команду для создания пользователя (по умолчанию `admin`): 
    ```bash
    python manage_users.py createadmin
    ```
    Вам будет предложено ввести и подтвердить пароль.
    Или укажите имя пользователя и пароль напрямую:
    ```bash
    python manage_users.py createadmin --username ваш_логин --password ваш_пароль
    ```

4.  **Запустите приложение:**
    ```bash
    make run
    ```
    Сервис будет доступен по адресу `http://127.0.0.1:5000/`.
    Документация API (Swagger UI) доступна по адресу `http://127.0.0.1:5000/api/docs/`.

### Ручная установка

1.  **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/Dreane/URL-Alias-Service
    cd URL-Alias-Service
    ```

2.  **Создайте и активируйте виртуальное окружение:**
    ```bash
    python -m venv venv
    # Для Windows
    venv\Scripts\activate
    # Для macOS/Linux
    source venv/bin/activate
    ```

3.  **Установите зависимости:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Создайте администратора:**
    ```bash
    python manage_users.py createadmin
    ```
    Вам будет предложено ввести и подтвердить пароль.

5.  **Запустите приложение:**
    ```bash
    python run.py
    ```
    Сервис будет доступен по адресу `http://127.0.0.1:5000/`.
    Документация API (Swagger UI) доступна по адресу `http://127.0.0.1:5000/api/docs/`.

## API Эндпоинты

Все приватные эндпоинты требуют Basic Auth. Учетные данные создаются с помощью скрипта `manage_users.py`.

### Публичные эндпоинты

*   **`GET /<short_code>`**
    *   Перенаправляет на оригинальный URL.
    *   Пример: `http://127.0.0.1:5000/XyZ123a`

### Приватные эндпоинты

*   **`POST /shorten`**
    *   Создает новую короткую ссылку.
    *   Тело запроса (JSON):
        ```json
        {
            "url": "<длинный_URL>",
            "days_to_expire": <количество_дней_до_истечения_срока_действия> (по умолчанию 1)
        }
        ```
    *   Пример ответа (201 Created):
        ```json
        {
            "original_url": "<длинный_URL>",
            "short_code": "<сгенерированный_код>",
            "short_url": "http://127.0.0.1:5000/<сгенерированный_код>",
            "created_at": "<ISO_timestamp>",
            "expires_at": "<ISO_timestamp>"
        }
        ```

*   **`GET /urls`**
    *   Возвращает список всех созданных ссылок.
    *   Параметры запроса (опционально):
        *   `page`: номер страницы (по умолчанию 1)
        *   `per_page`: количество элементов на странице (по умолчанию 10)
        *   `active`: фильтрация по активным ссылкам (`true` или `false`)
    *   Пример ответа:
        ```json
        {
            "urls": [
                {
                    "id": 1,
                    "original_url": "...",
                    "short_code": "...",
                    "short_url": "...",
                    "created_at": "...",
                    "expires_at": "...",
                    "is_active": true,
                    "clicks": 0
                }
            ],
            "total_urls": 1,
            "current_page": 1,
            "total_pages": 1
        }
        ```

*   **`DELETE /urls/<short_code>`**
    *   Деактивирует указанную короткую ссылку (не удаляет физически).
    *   Пример ответа (200 OK):
        ```json
        {
            "message": "Ссылка <short_code> была деактивирована."
        }
        ```

*   **`GET /stats`**
    *   (Приватный) Возвращает статистику по переходам для ссылок, у которых был хотя бы один переход, отсортированную по убыванию количества переходов.
    *   Пример ответа:
        ```json
        [
            {
                "short_code": "abc",
                "original_url": "http://example.com",
                "short_url": "http://127.0.0.1:5000/abc",
                "clicks": 10,
                "created_at": "...",
                "expires_at": "...",
                "is_active": true
            }
        ]
        ```

## Makefile команды

*   `make help`: Отображает список доступных команд.
*   `make install`: Создает виртуальное окружение (если не существует) и устанавливает зависимости.
*   `make run`: Запускает сервер разработки Flask.
*   `make clean`: Удаляет виртуальное окружение и каталог `instance`.
