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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
        'emoji': '🥉'
    },
    'start': {
        'name': 'СТАРТ',
        'price': 69,
        'old_price': 90,
        'emoji': '🥈'
    },
    'optimal': {
        'name': 'ОПТИМА',
        'price': 119,
        'old_price': 150,
        'emoji': '🥇',
        'recommended': True
    },
    'vip': {
        'name': 'ПРЕМИУМ VIP',
        'price': 299,
        'old_price': 450,
        'emoji': '👑'
    }
}

# Функция для создания клавиатуры с тарифами
def get_plans_keyboard():
    buttons = []
    for plan_id, plan in PLANS.items():
        text = f"{plan['emoji']} {plan['name']} - ${plan['price']}"
        if plan.get('recommended'):
            text += " ⭐️"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"plan_{plan_id}")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


# Функция для создания клавиатуры для тарифа
def get_payment_keyboard(plan_id: str):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Связаться с тренером", callback_data=f"contact_{plan_id}")],
        [InlineKeyboardButton(text="📋 Оставить заявку", callback_data=f"order_{plan_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_plans")]
    ])
    return keyboard


# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    try:
        logger.info(f"Получена команда /start от пользователя {message.from_user.id} (@{message.from_user.username})")
        logger.info(f"Полный текст: {message.text}")
        
        # Проверяем параметр
        args = message.text.split()
        logger.info(f"Аргументы команды: {args}")
        
        if len(args) > 1:
            plan_id = args[1].lower()
            logger.info(f"Получен plan_id: {plan_id}")
            
            if plan_id in PLANS:
                logger.info(f"Показываем тариф: {plan_id}")
                await show_plan_details(message, plan_id)
                return
            else:
                logger.warning(f"Неизвестный plan_id: {plan_id}")
        
        # Показываем все тарифы
        logger.info("Показываем все тарифы")
        
        text = "🏋️ Добро пожаловать в LEVEL FIT!\n\n"
        text += "💪 Онлайн тренировки и персональные программы питания\n\n"
        text += "Выберите подходящий тариф:"
        
        await message.answer(text, reply_markup=get_plans_keyboard())
        logger.info("Сообщение с тарифами отправлено")
        
    except Exception as e:
        logger.error(f"Ошибка в cmd_start: {e}", exc_info=True)
        await message.answer("Произошла ошибка. Попробуйте позже или напишите /help")


# Показать детали тарифа
async def show_plan_details(message_or_callback, plan_id: str):
    try:
        plan = PLANS.get(plan_id)
        
        if not plan:
            logger.error(f"Тариф {plan_id} не найден")
            return
        
        discount = int(((plan['old_price'] - plan['price']) / plan['old_price']) * 100)
        
        # Простой текст без HTML
        text = f"{plan['emoji']} {plan['name']}\n\n"
        
        if plan_id == 'light':
            text += "✨ Готовая программа тренировок\n"
            text += "💪 Варианты для зала и дома\n"
            text += "📋 Стартовая консультация\n"
        elif plan_id == 'start':
            text += "✨ 2 консультации в месяц\n"
            text += "💪 Индивидуальная программа\n"
            text += "🍽 Рекомендации по питанию\n"
        elif plan_id == 'optimal':
            text += "✨ Персональные консультации\n"
            text += "💪 Индивидуальная программа\n"
            text += "🍽 Индивидуальный план питания\n"
            text += "📊 Еженедельный контроль\n"
            text += "🎯 Мотивационные челленджи\n"
        elif plan_id == 'vip':
            text += "✨ Консультации 24/7\n"
            text += "💪 Еженедельная корректировка\n"
            text += "🍽 Детальный план питания\n"
            text += "📊 Ежедневный анализ\n"
            text += "🧠 Психологическая поддержка\n"
            text += "💊 Рекомендации по добавкам\n"
        
        text += f"\n💰 Цена: ${plan['old_price']} → ${plan['price']}/месяц\n"
        text += f"🎁 Скидка: {discount}%\n"
        
        if plan.get('recommended'):
            text += "\n⭐️ РЕКОМЕНДУЕМЫЙ ТАРИФ ⭐️\n"
        
        text += "\n📞 Свяжитесь с тренером или оставьте заявку!"
        
        keyboard = get_payment_keyboard(plan_id)
        
        if isinstance(message_or_callback, types.Message):
            await message_or_callback.answer(text, reply_markup=keyboard)
            logger.info(f"Отправлены детали тарифа {plan_id} пользователю {message_or_callback.from_user.id}")
        else:
            await message_or_callback.message.edit_text(text, reply_markup=keyboard)
            logger.info(f"Обновлены детали тарифа {plan_id}")
            
    except Exception as e:
        logger.error(f"Ошибка в show_plan_details: {e}", exc_info=True)


# Обработка выбора тарифа
@dp.callback_query(F.data.startswith("plan_"))
async def process_plan_selection(callback: types.CallbackQuery):
    try:
        plan_id = callback.data.split("_")[1]
        logger.info(f"Выбран тариф {plan_id} пользователем {callback.from_user.id}")
        await show_plan_details(callback, plan_id)
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в process_plan_selection: {e}", exc_info=True)
        await callback.answer("Ошибка. Попробуйте снова.")


# Кнопка "Назад"
@dp.callback_query(F.data == "back_to_plans")
async def back_to_plans(callback: types.CallbackQuery):
    try:
        text = "Выберите подходящий тариф:"
        await callback.message.edit_text(text, reply_markup=get_plans_keyboard())
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в back_to_plans: {e}", exc_info=True)


# Кнопка "Связаться"
@dp.callback_query(F.data.startswith("contact_"))
async def process_contact(callback: types.CallbackQuery):
    try:
        plan_id = callback.data.split("_")[1]
        plan = PLANS.get(plan_id)
        
        text = f"📞 Связаться с тренером\n\n"
        text += f"Вы выбрали: {plan['name']} (${plan['price']}/мес)\n\n"
        text += f"Напишите тренеру:\n"
        text += f"👤 @denis_levelfit\n\n"
        text += f"Мы ответим в течение часа!"
        
        await callback.message.answer(text)
        await callback.answer("✅ Контакты отправлены!")
        
        # Уведомление админу
        if ADMIN_TELEGRAM_ID:
            admin_text = f"📞 ЗАПРОС НА СВЯЗЬ\n\n"
            admin_text += f"👤 {callback.from_user.full_name}\n"
            admin_text += f"🆔 {callback.from_user.id}\n"
            admin_text += f"📦 Тариф: {plan['name']}\n"
            admin_text += f"💵 ${plan['price']}\n"
            admin_text += f"🔗 @{callback.from_user.username or 'нет'}"
            
            await bot.send_message(ADMIN_TELEGRAM_ID, admin_text)
            
    except Exception as e:
        logger.error(f"Ошибка в process_contact: {e}", exc_info=True)


# Кнопка "Оставить заявку"
@dp.callback_query(F.data.startswith("order_"))
async def process_order(callback: types.CallbackQuery):
    try:
        plan_id = callback.data.split("_")[1]
        plan = PLANS.get(plan_id)
        
        text = f"📋 Оформление заявки\n\n"
        text += f"Тариф: {plan['name']} (${plan['price']}/мес)\n\n"
        text += f"Отправьте сообщением:\n\n"
        text += f"1. Ваше имя\n"
        text += f"2. Возраст\n"
        text += f"3. Цель (похудение/масса/сушка)\n"
        text += f"4. Телефон или email\n\n"
        text += f"Пример:\n"
        text += f"Александр, 28, похудение, +375291234567"
        
        await callback.message.answer(text)
        await callback.answer("✅ Отправьте данные!")
        
        # Уведомление админу
        if ADMIN_TELEGRAM_ID:
            admin_text = f"📋 НОВАЯ ЗАЯВКА\n\n"
            admin_text += f"👤 {callback.from_user.full_name}\n"
            admin_text += f"🆔 {callback.from_user.id}\n"
            admin_text += f"📦 Тариф: {plan['name']}\n"
            admin_text += f"💵 ${plan['price']}\n"
            admin_text += f"⏳ Ожидает данных..."
            
            await bot.send_message(ADMIN_TELEGRAM_ID, admin_text)
            
    except Exception as e:
        logger.error(f"Ошибка в process_order: {e}", exc_info=True)


# Обработка текста
@dp.message(F.text)
async def handle_text(message: types.Message):
    try:
        if message.text.startswith('/'):
            return
        
        logger.info(f"Получено сообщение от {message.from_user.id}: {message.text[:50]}")
        
        text = "✅ Заявка принята!\n\n"
        text += f"Ваши данные:\n{message.text}\n\n"
        text += "Тренер свяжется с вами в ближайшее время!"
        
        await message.answer(text)
        
        # Админу
        if ADMIN_TELEGRAM_ID:
            admin_text = f"📨 НОВАЯ ЗАЯВКА!\n\n"
            admin_text += f"👤 {message.from_user.full_name}\n"
            admin_text += f"🆔 {message.from_user.id}\n"
            admin_text += f"🔗 @{message.from_user.username or 'нет'}\n\n"
            admin_text += f"📝 Данные:\n{message.text}"
            
            await bot.send_message(ADMIN_TELEGRAM_ID, admin_text)
            logger.info(f"Уведомление отправлено админу {ADMIN_TELEGRAM_ID}")
            
    except Exception as e:
        logger.error(f"Ошибка в handle_text: {e}", exc_info=True)


# Команда /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    try:
        text = "ℹ️ Помощь LEVEL FIT\n\n"
        text += "Команды:\n"
        text += "/start - Начать\n"
        text += "/plans - Все тарифы\n"
        text += "/help - Помощь\n\n"
        text += "Напишите, если нужна помощь!"
        
        await message.answer(text)
    except Exception as e:
        logger.error(f"Ошибка в cmd_help: {e}", exc_info=True)


# Команда /plans
@dp.message(Command("plans"))
async def cmd_plans(message: types.Message):
    try:
        text = "🏋️ Тарифы LEVEL FIT:\n\n"
        text += "Выберите подходящий тариф:"
        
        await message.answer(text, reply_markup=get_plans_keyboard())
    except Exception as e:
        logger.error(f"Ошибка в cmd_plans: {e}", exc_info=True)


# Запуск
async def main():
    logger.info("="*50)
    logger.info("🤖 LEVEL FIT БОТ ЗАПУСКАЕТСЯ...")
    logger.info(f"Bot Token: {BOT_TOKEN[:20]}...")
    logger.info(f"Admin ID: {ADMIN_TELEGRAM_ID or 'НЕ УКАЗАН'}")
    logger.info("="*50)
    
    try:
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        logger.info(f"✅ Бот подключен: @{bot_info.username}")
        logger.info(f"Имя: {bot_info.first_name}")
        logger.info(f"ID: {bot_info.id}")
        logger.info("="*50)
        logger.info("🚀 БОТ РАБОТАЕТ! Ожидаю сообщений...")
        logger.info("="*50)
        
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}", exc_info=True)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка запуска: {e}", exc_info=True)


