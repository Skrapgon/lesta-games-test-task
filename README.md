# Тестовое задание Lesta Games
## Структура проекта
```
project/
├── app/
│   ├── application/
│   │   ├── api/
│   │   │   ├── info.py
│   │   │   └── texts.py
│   │   ├── static/js
│   │   │   └── main.js
│   │   └── templates/
│   │       └── index.html
│   ├── core/
│   │   ├── config.py
│   │   └── version.py
│   ├── domain/entities
│   │   └── texts.py
│   ├── infra/
│   │   ├── base.py
│   │   └── database.py
│   ├── logic/
│   │   ├── text_utils.py
│   │   └── tf_idf.py
│   └── main.py
├── nginx/
│   └── default.conf
├── .env
├── .gitignore
├── CHANGELOG.md
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

## Установка и запуск
### 1. Установка зависимостей (установка на Ubuntu):
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

### 4. Запуск проекта
```
sudo docker compose up --build
```

После запуска приложение будет доступно по адресу: http://localhost

## Версия приложения 1.0.0 

## Изменения в сравнении с тестовым заданием
[Изменения](CHANGELOG.md)