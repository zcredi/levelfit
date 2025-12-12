#!/bin/bash
# Скрипт быстрой настройки LEVEL FIT Telegram бота
# Использование: bash SETUP_COMMANDS.sh

echo "🤖 LEVEL FIT - Настройка Telegram бота"
echo "========================================"
echo ""

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не установлен. Установите Python 3.9+ и попробуйте снова."
    exit 1
fi

echo "✅ Python $(python3 --version) обнаружен"
echo ""

# Проверка наличия pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 не установлен. Установите pip3 и попробуйте снова."
    exit 1
fi

echo "✅ pip3 обнаружен"
echo ""

# Проверка .env файла
if [ -f ".env" ]; then
    echo "⚠️  Файл .env уже существует."
    read -p "Перезаписать? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Пропускаю создание .env"
    else
        rm .env
        CREATE_ENV=true
    fi
else
    CREATE_ENV=true
fi

# Создание .env файла
if [ "$CREATE_ENV" = true ]; then
    echo ""
    echo "📝 Создание .env файла..."
    echo ""
    
    # BOT_TOKEN уже есть
    BOT_TOKEN="8029053288:AAHZdSBMbp_1bEr8DgU_n6qrxl6kkkVuScc"
    
    # Запрос PAYMENT_TOKEN
    echo "Введите PAYMENT_TOKEN (от YooKassa или Stripe):"
    echo "Если нет - оставьте пустым (можно добавить позже)"
    read -p "PAYMENT_TOKEN: " PAYMENT_TOKEN
    if [ -z "$PAYMENT_TOKEN" ]; then
        PAYMENT_TOKEN="your_payment_token_here"
    fi
    
    echo ""
    
    # Запрос ADMIN_TELEGRAM_ID
    echo "Введите ваш Telegram ID (узнайте у @userinfobot):"
    echo "Если не знаете - оставьте пустым (можно добавить позже)"
    read -p "ADMIN_TELEGRAM_ID: " ADMIN_ID
    if [ -z "$ADMIN_ID" ]; then
        ADMIN_ID="your_telegram_id_here"
    fi
    
    # Создание файла
    cat > .env << EOF
# Токен вашего Telegram бота
BOT_TOKEN=$BOT_TOKEN

# Токен платежного провайдера
PAYMENT_TOKEN=$PAYMENT_TOKEN

# Ваш Telegram ID
ADMIN_TELEGRAM_ID=$ADMIN_ID
EOF
    
    echo ""
    echo "✅ Файл .env создан!"
fi

echo ""
echo "📦 Установка зависимостей..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Зависимости установлены!"
else
    echo "❌ Ошибка при установке зависимостей"
    exit 1
fi

echo ""
echo "✅ Настройка завершена!"
echo ""
echo "🚀 Запустите бота командой:"
echo "   python3 bot.py"
echo ""
echo "📖 Или прочитайте документацию:"
echo "   - START_HERE.md - быстрый старт"
echo "   - SETUP.md - подробная настройка"
echo ""

