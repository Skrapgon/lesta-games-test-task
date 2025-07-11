# Тестовое задание Lesta Games
## Структура проекта
```
project/
├── app/
│   ├── api/
│   │   ├── collection.py
│   │   ├── document.py
│   │   ├── info.py
│   │   └── user.py
│   ├── auth/
│   │   ├── auth.py
│   │   └── blacklist.py
│   ├── core/
│   │   ├── config.py
│   │   └── version.py
│   ├── infra/
│   │   ├── base.py
│   │   ├── database.py
│   │   └── models.py
│   ├── logic/
│   │   ├── collection.py
│   │   ├── document.py
│   │   ├── huffman.py
│   │   └── text_utils.py
│   ├── schema/
│   │   ├── collection.py
│   │   ├── document.py
│   │   ├── huffman.py
│   │   ├── info.py
│   │   ├── token.py
│   │   └── user.py
│   ├── exceptions.py
│   └── main.py
├── images/
│   └── diagram.png
├── nginx/
│   ├── default.conf
│   └── nginx.conf
├── .env
├── .gitignore
├── CHANGELOG.md
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

## Структура таблиц сущностей в БД
![Диаграмма](./images/diagram.png)

## Установка и запуск
### 1. Установка зависимостей:
Длы запуска проекта должны быть установлены `git`, `Docker` и `Docker Compose`.

Установка зависимостей на Ubuntu:
* Установка git
    ```
    sudo apt install git
    ```

* Установка Docker
    ```
    sudo apt install -y ca-certificates curl gnupg
    sudo install -m 0755 -d /etc/apt/keyrings

    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    echo \
    "deb [arch=$(dpkg --print-architecture) \
    signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io
    ```

* Установка Docker Compose
    ```
    sudo apt install docker-compose
    ```

### 2. Клонирование проекта
```
git clone https://github.com/Skrapgon/lesta-games-test-task.git
cd lesta-games-test-task
```

### 3. Создание `.env` файла в корне проекта
```
nano .env
```

Для настройки доступны следующие параметры:
| Параметр      | Пример значения |
| ----------- | ----------- |
| POSTGRES_USER      | user       |
| POSTGRES_PASSWORD   | password        |
| POSTGRES_DB   | db_name        |
| POSTGRES_HOST   | db (хост должен совпадать с именем сервиса БД)        |
| POSTGRES_PORT   | 5432        |
| REDIS_HOST   | redis (хост должен совпадать с именем сервиса Redis)        |
| REDIS_PORT   | 6379        |
| REDIS_DB   | 0-15        |
| SECRET_KEY   | secret_key        |

Для генерации сложного <b>SECRET_KEY</b> можно воспользоваться: `python -c "import secrets; print(secrets.token_urlsafe(64))"`

### 4. Запуск проекта
```
sudo docker compose up --build
```

Документация будет доступна по адресу: http://localhost:8000/docs

## используемые метрики

| Название метрики      | Назначение |
| ----------- | ----------- |
| files_processed      | Общее число загруженных/обработанных файлов       |
| min_time_processed   | Минимальное время обработки файла        |
| max_time_processed   | Максимальное время обработки файла        |
| avg_time_processed   | Среднее время обработки файла        |
| latest_file_processed_timestamp   | Время загрузки последнего файла в виде timestamp        |
| avg_words_per_file   | Среднее число слов в файле        |
| avg_files_per_user   | Среднее число файлов на пользователя        |

## Версия приложения 1.2.3 

## Изменения в версиях
[Изменения](CHANGELOG.md)