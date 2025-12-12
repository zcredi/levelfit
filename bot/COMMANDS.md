# ⚡️ Шпаргалка команд для Telegram бота

## 🚀 Быстрый старт (копируй-вставляй)

### 1. Создание .env файла

```bash
cd bot
cat > .env << 'EOF'
BOT_TOKEN=your_bot_token_here
PAYMENT_TOKEN=your_payment_token_here
ADMIN_TELEGRAM_ID=your_telegram_id_here
EOF
```

### 2. Установка зависимостей

```bash
pip3 install -r requirements.txt
```

### 3. Запуск бота

```bash
python3 bot.py
```

---

## 🔑 Получение токенов

### Telegram Bot Token

```bash
# 1. Откройте Telegram
# 2. Найдите @BotFather
# 3. Отправьте: /newbot
# 4. Скопируйте токен
```

### Telegram ID

```bash
# 1. Откройте Telegram
# 2. Найдите @userinfobot
# 3. Нажмите Start
# 4. Скопируйте ваш ID
```

### Payment Token (YooKassa)

```bash
# 1. Регистрация: https://yookassa.ru/
# 2. Настройки → Платежные токены
# 3. Подключите Telegram Payments
# 4. Скопируйте токен
```

---

## 🐳 Docker команды

### Сборка и запуск

```bash
# Сборка образа
docker build -t levelfit-bot .

# Запуск контейнера
docker run -d --name levelfit-bot --env-file .env levelfit-bot

# Просмотр логов
docker logs -f levelfit-bot

# Остановка
docker stop levelfit-bot

# Удаление
docker rm levelfit-bot
```

### Docker Compose

```bash
# Запуск
docker-compose up -d

# Логи
docker-compose logs -f

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Пересборка
docker-compose up -d --build
```

---

## 🖥 VPS команды

### Первичная настройка

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и Git
sudo apt install python3 python3-pip git -y

# Клонирование репозитория
git clone https://github.com/your-repo/levelfit.git
cd levelfit/bot

# Установка зависимостей
pip3 install -r requirements.txt
```

### Настройка systemd сервиса

```bash
# Редактирование файла сервиса
nano levelfit-bot.service

# Замените пути:
# - /path/to/levelfit → ваш реальный путь
# - your_username → ваше имя пользователя

# Копирование в systemd
sudo cp levelfit-bot.service /etc/systemd/system/

# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable levelfit-bot

# Запуск
sudo systemctl start levelfit-bot

# Проверка статуса
sudo systemctl status levelfit-bot
```

### Управление сервисом

```bash
# Запуск
sudo systemctl start levelfit-bot

# Остановка
sudo systemctl stop levelfit-bot

# Перезапуск
sudo systemctl restart levelfit-bot

# Статус
sudo systemctl status levelfit-bot

# Включить автозапуск
sudo systemctl enable levelfit-bot

# Отключить автозапуск
sudo systemctl disable levelfit-bot

# Логи (последние 50 строк)
sudo journalctl -u levelfit-bot -n 50

# Логи в реальном времени
sudo journalctl -u levelfit-bot -f

# Логи с определенного времени
sudo journalctl -u levelfit-bot --since "1 hour ago"
```

---

## 📝 Редактирование файлов

### Создание/редактирование .env

```bash
nano .env
```

Содержимое:
```env
BOT_TOKEN=6234567890:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
PAYMENT_TOKEN=381764678:TEST:123456
ADMIN_TELEGRAM_ID=123456789
```

Сохранение: `Ctrl+X` → `Y` → `Enter`

### Редактирование bot.py

```bash
nano bot.py
```

---

## 🔍 Проверка и отладка

### Проверка, что бот работает

```bash
# Локально
ps aux | grep bot.py

# Systemd
sudo systemctl is-active levelfit-bot

# Docker
docker ps | grep levelfit-bot
```

### Просмотр логов

```bash
# Python (если запущен напрямую)
# Логи выводятся в терминал

# Systemd
sudo journalctl -u levelfit-bot -f

# Docker
docker logs -f levelfit-bot
# или
docker-compose logs -f
```

### Тест подключения к Telegram API

```bash
# Замените YOUR_BOT_TOKEN на ваш токен
curl https://api.telegram.org/botYOUR_BOT_TOKEN/getMe
```

Ответ должен быть примерно таким:
```json
{
  "ok": true,
  "result": {
    "id": 123456789,
    "is_bot": true,
    "first_name": "LEVEL FIT",
    "username": "levelfit_payment_bot"
  }
}
```

---

## 🔄 Обновление бота

### Git pull + перезапуск

```bash
cd ~/levelfit/bot

# Остановка бота
sudo systemctl stop levelfit-bot

# Обновление кода
git pull

# Обновление зависимостей (если были изменения)
pip3 install -r requirements.txt

# Запуск бота
sudo systemctl start levelfit-bot

# Проверка статуса
sudo systemctl status levelfit-bot
```

### Docker обновление

```bash
cd ~/levelfit/bot

# Обновление кода
git pull

# Пересборка и перезапуск
docker-compose down
docker-compose up -d --build

# Проверка логов
docker-compose logs -f
```

---

## 🔒 Безопасность

### Настройка файрвола (UFW)

```bash
# Установка UFW
sudo apt install ufw -y

# Разрешить SSH
sudo ufw allow 22/tcp

# Включить файрвол
sudo ufw enable

# Проверка статуса
sudo ufw status
```

### Создание SSH ключа

```bash
# Генерация ключа
ssh-keygen -t ed25519 -C "your_email@example.com"

# Копирование на сервер
ssh-copy-id user@your_server_ip

# Теперь можно подключаться без пароля
ssh user@your_server_ip
```

---

## 📊 Мониторинг

### Использование ресурсов

```bash
# CPU и RAM
htop

# Использование диска
df -h

# Сетевая активность
sudo nethogs
```

### Размер логов

```bash
# Размер журнала systemd
sudo journalctl --disk-usage

# Очистка старых логов (оставить последние 3 дня)
sudo journalctl --vacuum-time=3d
```

---

## 🧹 Очистка

### Удаление бота

```bash
# Остановка сервиса
sudo systemctl stop levelfit-bot
sudo systemctl disable levelfit-bot

# Удаление файла сервиса
sudo rm /etc/systemd/system/levelfit-bot.service

# Перезагрузка systemd
sudo systemctl daemon-reload

# Удаление кода
rm -rf ~/levelfit
```

### Очистка Docker

```bash
# Остановка и удаление контейнеров
docker-compose down

# Удаление образов
docker rmi levelfit-bot

# Очистка неиспользуемых ресурсов
docker system prune -a
```

---

## 🆘 Решение проблем

### Бот не запускается

```bash
# 1. Проверьте токены
cat .env

# 2. Проверьте логи
sudo journalctl -u levelfit-bot -n 50

# 3. Попробуйте запустить вручную
python3 bot.py

# 4. Проверьте зависимости
pip3 list | grep aiogram
```

### Порт занят

```bash
# Найти процесс
sudo lsof -i :8000

# Убить процесс (замените PID на ID процесса)
sudo kill -9 PID
```

### Нет интернета на сервере

```bash
# Проверка подключения
ping -c 4 8.8.8.8

# Проверка DNS
nslookup google.com

# Проверка подключения к Telegram API
curl https://api.telegram.org
```

---

## 📞 Полезные ссылки

- **BotFather:** https://t.me/BotFather
- **UserInfoBot:** https://t.me/userinfobot
- **YooKassa:** https://yookassa.ru/
- **ЮMoney:** https://yoomoney.ru/
- **Telegram Bot API Docs:** https://core.telegram.org/bots/api
- **aiogram Docs:** https://docs.aiogram.dev/

---

## 💡 Частые команды (TL;DR)

```bash
# Запуск бота
python3 bot.py

# Systemd: запуск
sudo systemctl start levelfit-bot

# Systemd: логи
sudo journalctl -u levelfit-bot -f

# Docker: запуск
docker-compose up -d

# Docker: логи
docker-compose logs -f

# Обновление и перезапуск
git pull && sudo systemctl restart levelfit-bot
```

---

**Сохраните эту шпаргалку для быстрого доступа!** 📌


