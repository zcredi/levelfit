import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN', '8029053288:AAHZdSBMbp_1bEr8DgU_n6qrxl6kkkVuScc')
ADMIN_TELEGRAM_ID = os.getenv('ADMIN_TELEGRAM_ID')

# Создаем бота и диспетчер
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Данные о тарифах
PLANS = {
    'light': {
        'name': 'ЛАЙТ',
        'price': 39,
        'old_price': 50,
        'currency': 'USD',
        'description': '✨ Готовая программа тренировок\n💪 Несколько вариантов упражнений (зал и дом)\n📋 Стартовая консультация-анкетирование',
        'emoji': '🥉'
    },
    'start': {
        'name': 'СТАРТ',
        'price': 69,
        'old_price': 90,
        'currency': 'USD',
        'description': '✨ 2 персональные онлайн-консультации в месяц (30-45 мин)\n💪 Индивидуальная программа тренировок (обновление 1 раз в месяц)\n🍽 Общие рекомендации по питанию',
        'emoji': '🥈'
    },
    'optimal': {
        'name': 'ОПТИМА',
        'price': 119,
        'old_price': 150,
        'currency': 'USD',
        'description': '✨ Персональные онлайн-консультации (в рабочие часы)\n💪 Полностью индивидуальная программа (корректировка каждые 2 недели)\n🍽 Индивидуальный план питания\n📊 Еженедельный контроль результатов\n🎯 Мотивационные челленджи',
        'emoji': '🥇',
        'recommended': True
    },
    'vip': {
        'name': 'ПРЕМИУМ VIP',
        'price': 299,
        'old_price': 450,
        'currency': 'USD',
        'description': '✨ Неограниченные консультации 24/7 с моментальным ответом\n💪 Еженедельная корректировка программы\n🍽 Детализированный план питания с ежедневными корректировками\n📊 Ежедневный анализ дневника питания\n🧠 Психологическая поддержка\n💊 Персональные рекомендации по добавкам\n🎁 Особые бонусы',
        'emoji': '👑'
    }
}

# Функция для создания клавиатуры с тарифами
def get_plans_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{plan['emoji']} {plan['name']} - ${plan['price']}{' ⭐️ РЕКОМЕНДУЕМ' if plan.get('recommended') else ''}",
            callback_data=f"plan_{plan_id}"
        )] for plan_id, plan in PLANS.items()
    ])
    return keyboard


# Функция для создания клавиатуры для конкретного тарифа
def get_payment_keyboard(plan_id: str):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Связаться с тренером", callback_data=f"contact_{plan_id}")],
        [InlineKeyboardButton(text="📋 Оставить заявку", callback_data=f"order_{plan_id}")],
        [InlineKeyboardButton(text="◀️ Назад к тарифам", callback_data="back_to_plans")]
    ])
    return keyboard


# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Проверяем, есть ли параметр с выбранным тарифом
    args = message.text.split()
    
    # Логируем для отладки
    logger.info(f"Start command from user {message.from_user.id}, args: {args}")
    
    if len(args) > 1:
        plan_id = args[1].lower()  # Приводим к нижнему регистру
        logger.info(f"Plan ID from start: {plan_id}")
        
        if plan_id in PLANS:
            # Если передан конкретный тариф, сразу показываем его
            logger.info(f"Showing plan: {plan_id}")
            await show_plan_details(message, plan_id)
            return
        else:
            logger.warning(f"Unknown plan ID: {plan_id}, available: {list(PLANS.keys())}")
    
    # Иначе показываем все тарифы
    welcome_text = (
        "🏋️ Добро пожаловать в <b>LEVEL FIT</b>! 🏋️\n\n"
        "💪 Онлайн тренировки и персональные программы питания от профессионального тренера!\n\n"
        "Выберите подходящий тариф подписки для начала вашей трансформации:\n\n"
        "💡 Все тарифы включают персональный подход и профессиональное сопровождение!"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_plans_keyboard(),
        parse_mode="HTML"
    )


# Показать детали тарифа
async def show_plan_details(message_or_callback, plan_id: str):
    plan = PLANS.get(plan_id)
    
    if not plan:
        return
    
    discount_percent = int(((plan['old_price'] - plan['price']) / plan['old_price']) * 100)
    
    text = (
        f"{plan['emoji']} <b>{plan['name']}</b>\n\n"
        f"<b>Что входит:</b>\n{plan['description']}\n\n"
        f"💰 Цена: <s>${plan['old_price']}</s> → <b>${plan['price']}/месяц</b>\n"
        f"🎁 Скидка: <b>{discount_percent}%</b>\n\n"
        f"{'⭐️ <b>РЕКОМЕНДУЕМЫЙ ТАРИФ</b> ⭐️\n\n' if plan.get('recommended') else ''}"
        f"📞 Для оформления подписки свяжитесь с тренером или оставьте заявку!"
    )
    
    keyboard = get_payment_keyboard(plan_id)
    
    if isinstance(message_or_callback, types.Message):
        await message_or_callback.answer(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await message_or_callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")


# Обработка выбора тарифа
@dp.callback_query(F.data.startswith("plan_"))
async def process_plan_selection(callback: types.CallbackQuery):
    plan_id = callback.data.split("_")[1]
    await show_plan_details(callback, plan_id)
    await callback.answer()


# Обработка кнопки "Назад"
@dp.callback_query(F.data == "back_to_plans")
async def back_to_plans(callback: types.CallbackQuery):
    welcome_text = (
        "🏋️ <b>Выберите подходящий тариф:</b>\n\n"
        "💡 Все тарифы включают персональный подход и профессиональное сопровождение!"
    )
    
    await callback.message.edit_text(
        welcome_text,
        reply_markup=get_plans_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


# Обработка кнопки "Связаться с тренером"
@dp.callback_query(F.data.startswith("contact_"))
async def process_contact(callback: types.CallbackQuery):
    plan_id = callback.data.split("_")[1]
    plan = PLANS.get(plan_id)
    
    contact_text = (
        f"📞 <b>Связаться с тренером</b>\n\n"
        f"Вы выбрали тариф: <b>{plan['name']}</b> (${plan['price']}/мес)\n\n"
        f"Напишите тренеру Денису напрямую:\n"
        f"👤 @denis_levelfit\n\n"
        f"Или используйте чат поддержки на сайте!\n\n"
        f"💬 Мы ответим в течение 1 часа и подберем программу специально для вас!"
    )
    
    await callback.message.answer(contact_text, parse_mode="HTML")
    await callback.answer("✅ Контакты отправлены!")
    
    # Уведомление админу
    if ADMIN_TELEGRAM_ID:
        admin_message = (
            f"📞 <b>Запрос на связь с тренером!</b>\n\n"
            f"👤 Пользователь: {callback.from_user.full_name}\n"
            f"🆔 User ID: {callback.from_user.id}\n"
            f"📦 Интересует тариф: <b>{plan['name']}</b>\n"
            f"💵 Цена: ${plan['price']}\n"
            f"🔗 Telegram: @{callback.from_user.username if callback.from_user.username else 'не указан'}"
        )
        try:
            await bot.send_message(ADMIN_TELEGRAM_ID, admin_message, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление админу: {e}")


# Обработка кнопки "Оставить заявку"
@dp.callback_query(F.data.startswith("order_"))
async def process_order(callback: types.CallbackQuery):
    plan_id = callback.data.split("_")[1]
    plan = PLANS.get(plan_id)
    
    order_text = (
        f"📋 <b>Оформление заявки</b>\n\n"
        f"Тариф: <b>{plan['name']}</b> (${plan['price']}/мес)\n\n"
        f"Пожалуйста, отправьте следующую информацию:\n\n"
        f"1️⃣ Ваше имя\n"
        f"2️⃣ Возраст\n"
        f"3️⃣ Ваша цель (похудение/набор массы/сушка)\n"
        f"4️⃣ Контактный телефон или email\n\n"
        f"📝 <i>Например:</i>\n"
        f"<code>Александр, 28 лет, похудение, +375291234567</code>\n\n"
        f"После отправки с вами свяжется тренер для обсуждения деталей!"
    )
    
    await callback.message.answer(order_text, parse_mode="HTML")
    await callback.answer("✅ Отправьте ваши данные сообщением!")
    
    # Уведомление админу
    if ADMIN_TELEGRAM_ID:
        admin_message = (
            f"📋 <b>Новая заявка на подписку!</b>\n\n"
            f"👤 Пользователь: {callback.from_user.full_name}\n"
            f"🆔 User ID: {callback.from_user.id}\n"
            f"📦 Выбран тариф: <b>{plan['name']}</b>\n"
            f"💵 Цена: ${plan['price']}\n"
            f"🔗 Telegram: @{callback.from_user.username if callback.from_user.username else 'не указан'}\n\n"
            f"⏳ Ожидает отправки данных..."
        )
        try:
            await bot.send_message(ADMIN_TELEGRAM_ID, admin_message, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление админу: {e}")


# Обработка текстовых сообщений (данные клиента)
@dp.message(F.text)
async def handle_text_message(message: types.Message):
    # Игнорируем команды
    if message.text.startswith('/'):
        return
    
    # Подтверждение пользователю
    confirmation_text = (
        f"✅ <b>Заявка принята!</b>\n\n"
        f"📝 Ваши данные:\n"
        f"<code>{message.text}</code>\n\n"
        f"💬 Тренер свяжется с вами в ближайшее время!\n\n"
        f"Обычно мы отвечаем в течение 1 часа. 🚀"
    )
    await message.answer(confirmation_text, parse_mode="HTML")
    
    # Пересылка админу
    if ADMIN_TELEGRAM_ID:
        admin_message = (
            f"📨 <b>НОВАЯ ЗАЯВКА!</b>\n\n"
            f"👤 От: {message.from_user.full_name}\n"
            f"🆔 User ID: {message.from_user.id}\n"
            f"🔗 Username: @{message.from_user.username if message.from_user.username else 'не указан'}\n\n"
            f"📝 <b>Данные клиента:</b>\n"
            f"{message.text}\n\n"
            f"⚡️ Свяжитесь с клиентом: /start_{message.from_user.id}"
        )
        try:
            await bot.send_message(ADMIN_TELEGRAM_ID, admin_message, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление админу: {e}")


# Команда помощи
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "ℹ️ <b>Помощь по боту LEVEL FIT</b>\n\n"
        "<b>Доступные команды:</b>\n"
        "/start - Начать работу и выбрать тариф\n"
        "/plans - Посмотреть все тарифы\n"
        "/help - Показать это сообщение\n"
        "/contact - Контакты тренера\n\n"
        "❓ <b>Если у вас есть вопросы:</b>\n"
        "Напишите нам, и мы обязательно поможем!"
    )
    await message.answer(help_text, parse_mode="HTML")


# Команда для просмотра тарифов
@dp.message(Command("plans"))
async def cmd_plans(message: types.Message):
    welcome_text = (
        "🏋️ <b>Доступные тарифы LEVEL FIT:</b>\n\n"
        "💡 Выберите подходящий тариф для начала вашей трансформации!"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_plans_keyboard(),
        parse_mode="HTML"
    )


# Команда контактов
@dp.message(Command("contact"))
async def cmd_contact(message: types.Message):
    contact_text = (
        "📞 <b>Контакты LEVEL FIT</b>\n\n"
        "👤 Тренер: Денис\n"
        "💬 Telegram: @denis_levelfit\n"
        "📧 Email: info@levelfit.com\n\n"
        "🌐 Наш сайт: levelfit.com\n\n"
        "💬 Мы на связи 24/7!"
    )
    await message.answer(contact_text, parse_mode="HTML")


# Запуск бота
async def main():
    logger.info("🤖 LEVEL FIT Бот запущен (версия без платежей)!")
    logger.info(f"Bot username: @levelfitbot")
    if ADMIN_TELEGRAM_ID:
        logger.info(f"Admin ID: {ADMIN_TELEGRAM_ID}")
    else:
        logger.warning("⚠️ ADMIN_TELEGRAM_ID не указан в .env - уведомления не будут отправляться!")
    
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

