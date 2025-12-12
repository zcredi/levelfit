import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, PreCheckoutQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токены
BOT_TOKEN = os.getenv('BOT_TOKEN')
PAYMENT_TOKEN = os.getenv('PAYMENT_TOKEN')  # Токен провайдера (YooKassa, ЮMoney и т.д.)

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
        'description': '✨ Готовая программа тренировок\n💪 Несколько вариантов упражнений\n📋 Стартовая консультация-анкетирование',
        'emoji': '🥉'
    },
    'start': {
        'name': 'СТАРТ',
        'price': 69,
        'old_price': 90,
        'currency': 'USD',
        'description': '✨ 2 персональные онлайн-консультации в месяц\n💪 Индивидуальная программа тренировок\n🍽 Общие рекомендации по питанию',
        'emoji': '🥈'
    },
    'optimal': {
        'name': 'ОПТИМА',
        'price': 119,
        'old_price': 150,
        'currency': 'USD',
        'description': '✨ Персональные онлайн-консультации\n💪 Полностью индивидуальная программа\n🍽 Индивидуальный план питания\n📊 Еженедельный контроль результатов\n🎯 Мотивационные челленджи',
        'emoji': '🥇',
        'recommended': True
    },
    'vip': {
        'name': 'ПРЕМИУМ VIP',
        'price': 299,
        'old_price': 450,
        'currency': 'USD',
        'description': '✨ Неограниченные консультации 24/7\n💪 Еженедельная корректировка программы\n🍽 Детализированный план питания с ежедневными корректировками\n📊 Ежедневный анализ дневника питания\n🧠 Психологическая поддержка\n💊 Персональные рекомендации по добавкам\n🎁 Особые бонусы',
        'emoji': '👑'
    }
}

# Состояния для FSM
class OrderState(StatesGroup):
    waiting_for_payment = State()


# Функция для создания клавиатуры с тарифами
def get_plans_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{plan['emoji']} {plan['name']} - ${plan['price']}{' (РЕКОМЕНДУЕМ!)' if plan.get('recommended') else ''}",
            callback_data=f"plan_{plan_id}"
        )] for plan_id, plan in PLANS.items()
    ])
    return keyboard


# Функция для создания клавиатуры для конкретного тарифа
def get_payment_keyboard(plan_id: str):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить", callback_data=f"pay_{plan_id}")],
        [InlineKeyboardButton(text="◀️ Назад к тарифам", callback_data="back_to_plans")]
    ])
    return keyboard


# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Проверяем, есть ли параметр с выбранным тарифом
    args = message.text.split()
    
    if len(args) > 1 and args[1] in PLANS:
        # Если передан конкретный тариф, сразу показываем его
        plan_id = args[1]
        await show_plan_details(message, plan_id)
    else:
        # Иначе показываем все тарифы
        welcome_text = (
            "🏋️ Добро пожаловать в <b>LEVEL FIT</b>! 🏋️\n\n"
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
        f"{plan['description']}\n\n"
        f"💰 Цена: <s>${plan['old_price']}</s> <b>${plan['price']}</b>\n"
        f"🎁 Скидка: <b>{discount_percent}%</b>\n\n"
        f"{'⭐️ РЕКОМЕНДУЕМЫЙ ТАРИФ ⭐️' if plan.get('recommended') else ''}"
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
        "🏋️ Выберите подходящий тариф:\n\n"
        "💡 Все тарифы включают персональный подход и профессиональное сопровождение!"
    )
    
    await callback.message.edit_text(
        welcome_text,
        reply_markup=get_plans_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


# Обработка платежа
@dp.callback_query(F.data.startswith("pay_"))
async def process_payment(callback: types.CallbackQuery):
    plan_id = callback.data.split("_")[1]
    plan = PLANS.get(plan_id)
    
    if not plan:
        await callback.answer("Ошибка: тариф не найден", show_alert=True)
        return
    
    # Создаем инвойс для оплаты
    prices = [LabeledPrice(label=f"Тариф {plan['name']}", amount=plan['price'] * 100)]  # Сумма в копейках/центах
    
    try:
        await bot.send_invoice(
            chat_id=callback.from_user.id,
            title=f"LEVEL FIT - {plan['name']}",
            description=f"Подписка на тариф {plan['name']} на 1 месяц",
            payload=f"plan_{plan_id}",
            provider_token=PAYMENT_TOKEN,
            currency='USD',
            prices=prices,
            start_parameter=f"plan_{plan_id}",
            photo_url="https://i.imgur.com/placeholder.jpg",  # Замените на реальное изображение
            photo_width=512,
            photo_height=512,
            need_name=True,
            need_email=True,
            need_phone_number=True,
            is_flexible=False,
        )
        await callback.answer("✅ Счет отправлен!")
    except Exception as e:
        logger.error(f"Ошибка при создании инвойса: {e}")
        await callback.answer("❌ Ошибка при создании счета. Попробуйте позже.", show_alert=True)


# Обработка pre-checkout запроса
@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# Обработка успешного платежа
@dp.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    payment_info = message.successful_payment
    
    # Извлекаем информацию о тарифе
    plan_id = payment_info.invoice_payload.split("_")[1]
    plan = PLANS.get(plan_id)
    
    # Здесь можно сохранить информацию о платеже в базу данных
    user_id = message.from_user.id
    user_name = payment_info.order_info.name if payment_info.order_info else message.from_user.full_name
    user_email = payment_info.order_info.email if payment_info.order_info else "Не указан"
    user_phone = payment_info.order_info.phone_number if payment_info.order_info else "Не указан"
    
    logger.info(
        f"Успешный платеж: User ID: {user_id}, Plan: {plan['name']}, "
        f"Amount: {payment_info.total_amount / 100} {payment_info.currency}, "
        f"Name: {user_name}, Email: {user_email}, Phone: {user_phone}"
    )
    
    # Отправляем подтверждение пользователю
    success_message = (
        f"🎉 <b>Поздравляем с успешной оплатой!</b> 🎉\n\n"
        f"Ваша подписка на тариф <b>{plan['name']}</b> активирована!\n\n"
        f"📧 <b>Что дальше?</b>\n"
        f"В течение 24 часов с вами свяжется персональный тренер для:\n"
        f"• Заполнения анкеты о ваших целях\n"
        f"• Создания индивидуальной программы тренировок\n"
        f"• Разработки плана питания\n\n"
        f"📱 Тренер напишет вам в этом чате или на указанный email: {user_email}\n\n"
        f"💪 Добро пожаловать в команду <b>LEVEL FIT</b>!\n"
        f"Ваша трансформация начинается прямо сейчас! 🚀"
    )
    
    await message.answer(success_message, parse_mode="HTML")
    
    # Отправляем уведомление администратору (замените на реальный ID админа)
    ADMIN_ID = os.getenv('ADMIN_TELEGRAM_ID')  # Добавьте в .env
    if ADMIN_ID:
        admin_message = (
            f"💰 <b>НОВАЯ ПОДПИСКА!</b>\n\n"
            f"👤 Пользователь: {user_name}\n"
            f"🆔 User ID: {user_id}\n"
            f"📧 Email: {user_email}\n"
            f"📱 Телефон: {user_phone}\n"
            f"📦 Тариф: {plan['name']}\n"
            f"💵 Сумма: ${payment_info.total_amount / 100}\n"
            f"🔗 Telegram: @{message.from_user.username if message.from_user.username else 'Не указан'}"
        )
        try:
            await bot.send_message(ADMIN_ID, admin_message, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление админу: {e}")


# Команда помощи
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "ℹ️ <b>Помощь по боту LEVEL FIT</b>\n\n"
        "<b>Доступные команды:</b>\n"
        "/start - Начать работу с ботом и выбрать тариф\n"
        "/plans - Посмотреть все доступные тарифы\n"
        "/help - Показать это сообщение\n\n"
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


# Запуск бота
async def main():
    logger.info("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

