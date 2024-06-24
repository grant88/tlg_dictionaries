# tlg_dictionaries

## Installation

### Клонируем репозиторий
```bash
mkdir /apps
cd /apps
git clone https://github.com/grant88/tlg_dictionaries.git
```

###  Создаем виртуальное окружение `python`
```bash
python -m venv /opt/tlg_dictionaries_venv
```

###  Устанавливаем необходимые библиотеки
```bash
source /opt/tlg_dictionaries_venv/bin/activate
pip install -r requirements.txt
sudo pip install python-dotenv
```

### Настраиваем переменные окружения
Создаем файл `/apps/tlg_dictionaries/.env`
с содержимым, в котором поменяем параметры БД
```text
BANKS_LIST_TOKEN=<Your bot token>
DB_HOST=localhost
DB_PORT=5432
DB_NAME=<yourdb>
DB_USER=<youruser>
DB_PASS=<yourpassword>
BANKS_URL=https://www.cbr.ru/scripts/XML_bic.asp
```

### Инициализация справочников
```bash
mkdir  /apps/tlg_dictionaries/downloads
```
В каталог /apps/tlg_dictionaries/downloads перекидываем (например, с помощью [FileZilla](https://filezilla.ru/)) свежий справочник mcc_codes.xlsx, например, с сайта [mcc-codes](https://mcc-codes.ru/code)

Загружаем справочники в БД
```bash
python import.py
```

### Создание сервиса
Создаем файл tlg_bot.service
```bash
sudo vim /etc/systemd/system/tlg_bot.service
```

Прописываем в нем содержимое:
```text
[Unit]
Description=Telegram bot tlg_dictionaries
After=network.target auditd.service

[Service]
EnvironmentFile=/apps/tlg_dictionaries/.env
ExecStart=/opt/tlg_dictionaries_venv/bin/python /apps/tlg_dictionaries/app.py
WorkingDirectory=/apps/tlg_dictionaries/
Restart=always
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=%n
Type=simple

[Install]
WantedBy=multi-user.target
Alias=tlg_bot.service
```

### Запуск сервиса
```bash
sudo systemctl daemon-reload
sudo systemctl start tlg_bot.service
```

## Troubleshooting
```bash
sudo systemctl status tlg_bot.service
sudo journalctl -f -u tlg_bot.service
```