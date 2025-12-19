import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
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
CHANNEL_ID = os.getenv('CHANNEL_ID')

# Создаем бота и диспетчер
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Названия целей
GOALS = {
    'mass': 'Набор мышечной массы',
    'correction': 'Коррекция фигуры (сушка)',
    'weightloss': 'Снижение веса (похудение)'
}

# Состояния FSM для анкеты
class QuestionnaireStates(StatesGroup):
    waiting_for_fio = State()
    waiting_for_activity = State()
    waiting_for_limitations = State()
    waiting_for_experience = State()
    waiting_for_workouts_count = State()
    waiting_for_height = State()
    waiting_for_weight = State()

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

# Клавиатура для уровня активности
def get_activity_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Низкий")],
            [KeyboardButton(text="Средний")],
            [KeyboardButton(text="Высокий")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

# Клавиатура для количества тренировок
def get_workouts_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1"), KeyboardButton(text="2"), KeyboardButton(text="3")],
            [KeyboardButton(text="4"), KeyboardButton(text="5"), KeyboardButton(text="6")],
            [KeyboardButton(text="7")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

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
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    try:
        logger.info(f"Получена команда /start от пользователя {message.from_user.id} (@{message.from_user.username})")
        logger.info(f"Полный текст: {message.text}")
        
        # Очищаем предыдущее состояние
        await state.clear()
        
        # Проверяем параметр
        args = message.text.split()
        logger.info(f"Аргументы команды: {args}")
        
        if len(args) > 1:
            param = args[1].lower()
            logger.info(f"Получен параметр: {param}")
            
            # Проверяем, это цель с сайта или тариф
            if param in GOALS:
                # Это цель с сайта - запускаем анкету
                goal_name = GOALS[param]
                logger.info(f"Пользователь выбрал цель с сайта: {goal_name}")
                
                # Сохраняем цель
                await state.update_data(goal=goal_name, goal_id=param)
                
                # Приветствие
                text = f"🏋️ *Добро пожаловать в LEVEL FIT\\!*\n\n"
                text += f"Вы выбрали: *{goal_name}*\n\n"
                text += f"Давайте заполним анкету, чтобы создать идеальную программу для вас\\.\n\n"
                text += f"📋 Всего 7 вопросов, это займёт 2\\-3 минуты\\."
                
                await message.answer(text, parse_mode="MarkdownV2")
                
                # Задаем первый вопрос
                await asyncio.sleep(1)
                text_q1 = "1️⃣ *Укажите свои ФИО*\n\nНапример: Иванов Иван Иванович"
                await message.answer(text_q1, parse_mode="MarkdownV2")
                await state.set_state(QuestionnaireStates.waiting_for_fio)
                return
                
            elif param in PLANS:
                # Это прямая ссылка на тариф
                logger.info(f"Показываем тариф: {param}")
                await show_plan_details(message, param)
                return
            else:
                logger.warning(f"Неизвестный параметр: {param}")
        
        # Показываем все тарифы (если без параметра или неизвестный параметр)
        logger.info("Показываем все тарифы")
        
        text = "🏋️ *Добро пожаловать в LEVEL FIT\\!*\n\n"
        text += "💪 Онлайн тренировки и персональные программы питания\n\n"
        text += "Выберите подходящий тариф:"
        
        await message.answer(text, reply_markup=get_plans_keyboard(), parse_mode="MarkdownV2")
        logger.info("Сообщение с тарифами отправлено")
        
    except Exception as e:
        logger.error(f"Ошибка в cmd_start: {e}", exc_info=True)
        await message.answer("Произошла ошибка. Попробуйте позже или напишите /help")


# ========== ОБРАБОТЧИКИ АНКЕТЫ ==========

# Обработка ФИО
@dp.message(QuestionnaireStates.waiting_for_fio)
async def process_fio(message: types.Message, state: FSMContext):
    try:
        await state.update_data(fio=message.text)
        
        text = "2️⃣ *Укажите свой уровень активности в течение дня*"
        await message.answer(text, reply_markup=get_activity_keyboard(), parse_mode="MarkdownV2")
        await state.set_state(QuestionnaireStates.waiting_for_activity)
        
    except Exception as e:
        logger.error(f"Ошибка в process_fio: {e}", exc_info=True)

# Обработка уровня активности
@dp.message(QuestionnaireStates.waiting_for_activity)
async def process_activity(message: types.Message, state: FSMContext):
    try:
        if message.text not in ["Низкий", "Средний", "Высокий"]:
            await message.answer("❌ Пожалуйста, выберите один из вариантов на клавиатуре")
            return
        
        await state.update_data(activity=message.text)
        
        text = "3️⃣ *Противопоказания, ограничения, травмы*\n\n"
        text += "Если есть \\- укажите какие\\.\n"
        text += "Если нет \\- напишите: Нет"
        
        await message.answer(text, reply_markup=ReplyKeyboardRemove(), parse_mode="MarkdownV2")
        await state.set_state(QuestionnaireStates.waiting_for_limitations)
        
    except Exception as e:
        logger.error(f"Ошибка в process_activity: {e}", exc_info=True)

# Обработка противопоказаний
@dp.message(QuestionnaireStates.waiting_for_limitations)
async def process_limitations(message: types.Message, state: FSMContext):
    try:
        await state.update_data(limitations=message.text)
        
        text = "4️⃣ *Опыт тренировок*\n\n"
        text += "Если есть \\- укажите сколько месяцев или лет\\.\n"
        text += "Если нет опыта \\- напишите: Нет опыта"
        
        await message.answer(text, parse_mode="MarkdownV2")
        await state.set_state(QuestionnaireStates.waiting_for_experience)
        
    except Exception as e:
        logger.error(f"Ошибка в process_limitations: {e}", exc_info=True)

# Обработка опыта тренировок
@dp.message(QuestionnaireStates.waiting_for_experience)
async def process_experience(message: types.Message, state: FSMContext):
    try:
        await state.update_data(experience=message.text)
        
        text = "5️⃣ *Сколько тренировок в неделю вы планируете выполнять?*"
        
        await message.answer(text, reply_markup=get_workouts_keyboard(), parse_mode="MarkdownV2")
        await state.set_state(QuestionnaireStates.waiting_for_workouts_count)
        
    except Exception as e:
        logger.error(f"Ошибка в process_experience: {e}", exc_info=True)

# Обработка количества тренировок
@dp.message(QuestionnaireStates.waiting_for_workouts_count)
async def process_workouts_count(message: types.Message, state: FSMContext):
    try:
        if not message.text.isdigit() or int(message.text) < 1 or int(message.text) > 7:
            await message.answer("❌ Пожалуйста, выберите число от 1 до 7 на клавиатуре")
            return
        
        await state.update_data(workouts_count=message.text)
        
        text = "6️⃣ *Укажите ваш рост в сантиметрах*\n\nНапример: 175"
        
        await message.answer(text, reply_markup=ReplyKeyboardRemove(), parse_mode="MarkdownV2")
        await state.set_state(QuestionnaireStates.waiting_for_height)
        
    except Exception as e:
        logger.error(f"Ошибка в process_workouts_count: {e}", exc_info=True)

# Обработка роста
@dp.message(QuestionnaireStates.waiting_for_height)
async def process_height(message: types.Message, state: FSMContext):
    try:
        if not message.text.replace('.', '').replace(',', '').isdigit():
            await message.answer("❌ Пожалуйста, укажите рост числом (например: 175)")
            return
        
        await state.update_data(height=message.text)
        
        text = "7️⃣ *Укажите ваш вес в килограммах*\n\nНапример: 70"
        
        await message.answer(text, parse_mode="MarkdownV2")
        await state.set_state(QuestionnaireStates.waiting_for_weight)
        
    except Exception as e:
        logger.error(f"Ошибка в process_height: {e}", exc_info=True)

# Обработка веса (финальный вопрос)
@dp.message(QuestionnaireStates.waiting_for_weight)
async def process_weight(message: types.Message, state: FSMContext):
    try:
        if not message.text.replace('.', '').replace(',', '').isdigit():
            await message.answer("❌ Пожалуйста, укажите вес числом (например: 70)")
            return
        
        await state.update_data(weight=message.text)
        
        # Получаем все данные
        data = await state.get_data()
        
        # Формируем сообщение для пользователя
        user_text = "✅ *Анкета заполнена\\!*\n\n"
        user_text += "Спасибо\\! Тренер свяжется с вами в ближайшее время\\.\n\n"
        user_text += "💪 Начинайте готовиться к трансформации\\!"
        
        await message.answer(user_text, parse_mode="MarkdownV2")
        
        # Формируем сообщение для канала
        channel_text = "📋 *НОВАЯ ЗАЯВКА*\n\n"
        channel_text += f"👤 *ФИО:* {data.get('fio', 'Не указано')}\n"
        channel_text += f"🎯 *Цель:* {data.get('goal', 'Не указана')}\n"
        channel_text += f"⚡ *Активность:* {data.get('activity', 'Не указана')}\n"
        channel_text += f"⚠️ *Противопоказания:* {data.get('limitations', 'Не указано')}\n"
        channel_text += f"📊 *Опыт тренировок:* {data.get('experience', 'Не указан')}\n"
        channel_text += f"🏋️ *Тренировок в неделю:* {data.get('workouts_count', 'Не указано')}\n"
        channel_text += f"📏 *Рост:* {data.get('height', 'Не указан')} см\n"
        channel_text += f"⚖️ *Вес:* {data.get('weight', 'Не указан')} кг\n\n"
        channel_text += f"📱 *Telegram:* @{message.from_user.username or 'нет'}\n"
        channel_text += f"🆔 *ID:* {message.from_user.id}\n"
        channel_text += f"👤 *Имя в TG:* {message.from_user.full_name}"
        
        # Отправляем в канал
        if CHANNEL_ID:
            await bot.send_message(CHANNEL_ID, channel_text, parse_mode="MarkdownV2")
            logger.info(f"Заявка от {message.from_user.id} отправлена в канал {CHANNEL_ID}")
        
        # Очищаем состояние
        await state.clear()
        
    except Exception as e:
        logger.error(f"Ошибка в process_weight: {e}", exc_info=True)
        await message.answer("Произошла ошибка при отправке анкеты. Попробуйте снова /start")

# ========== КОНЕЦ ОБРАБОТЧИКОВ АНКЕТЫ ==========


# Показать детали тарифа
async def show_plan_details(message_or_callback, plan_id: str):
    try:
        plan = PLANS.get(plan_id)
        
        if not plan:
            logger.error(f"Тариф {plan_id} не найден")
            return
        
        discount = int(((plan['old_price'] - plan['price']) / plan['old_price']) * 100)
        
        # Используем MarkdownV2 для зачеркивания
        text = f"{plan['emoji']} *{plan['name']}*\n\n"
        
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
        
        # Зачеркнутая старая цена и новая цена
        text += f"\n💰 Цена: ~${plan['old_price']}~ → *${plan['price']}/месяц*\n"
        text += f"🎁 Скидка: *{discount}%*\n"
        
        if plan.get('recommended'):
            text += "\n⭐️ *РЕКОМЕНДУЕМЫЙ ТАРИФ* ⭐️\n"
        
        text += "\n📞 Свяжитесь с тренером или оставьте заявку\\!"
        
        keyboard = get_payment_keyboard(plan_id)
        
        if isinstance(message_or_callback, types.Message):
            await message_or_callback.answer(text, reply_markup=keyboard, parse_mode="MarkdownV2")
            logger.info(f"Отправлены детали тарифа {plan_id} пользователю {message_or_callback.from_user.id}")
        else:
            await message_or_callback.message.edit_text(text, reply_markup=keyboard, parse_mode="MarkdownV2")
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
        
        # Уведомление админу и в канал
        admin_text = f"📞 ЗАПРОС НА СВЯЗЬ\n\n"
        admin_text += f"👤 {callback.from_user.full_name}\n"
        admin_text += f"🆔 {callback.from_user.id}\n"
        admin_text += f"📦 Тариф: {plan['name']}\n"
        admin_text += f"💵 ${plan['price']}\n"
        admin_text += f"🔗 @{callback.from_user.username or 'нет'}"
        
        if ADMIN_TELEGRAM_ID:
            await bot.send_message(ADMIN_TELEGRAM_ID, admin_text)
        
        if CHANNEL_ID:
            await bot.send_message(CHANNEL_ID, admin_text)
            
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
        
        # Уведомление админу и в канал
        admin_text = f"📋 НОВАЯ ЗАЯВКА\n\n"
        admin_text += f"👤 {callback.from_user.full_name}\n"
        admin_text += f"🆔 {callback.from_user.id}\n"
        admin_text += f"📦 Тариф: {plan['name']}\n"
        admin_text += f"💵 ${plan['price']}\n"
        admin_text += f"⏳ Ожидает данных..."
        
        if ADMIN_TELEGRAM_ID:
            await bot.send_message(ADMIN_TELEGRAM_ID, admin_text)
        
        if CHANNEL_ID:
            await bot.send_message(CHANNEL_ID, admin_text)
            
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
        
        # Админу и в канал
        admin_text = f"📨 НОВАЯ ЗАЯВКА!\n\n"
        admin_text += f"👤 {message.from_user.full_name}\n"
        admin_text += f"🆔 {message.from_user.id}\n"
        admin_text += f"🔗 @{message.from_user.username or 'нет'}\n\n"
        admin_text += f"📝 Данные:\n{message.text}"
        
        if ADMIN_TELEGRAM_ID:
            await bot.send_message(ADMIN_TELEGRAM_ID, admin_text)
            logger.info(f"Уведомление отправлено админу {ADMIN_TELEGRAM_ID}")
        
        if CHANNEL_ID:
            await bot.send_message(CHANNEL_ID, admin_text)
            logger.info(f"Заявка сохранена в канал {CHANNEL_ID}")
            
    except Exception as e:
        logger.error(f"Ошибка в handle_text: {e}", exc_info=True)


# Команда /cancel
@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    try:
        current_state = await state.get_state()
        if current_state is None:
            await message.answer("❌ Нет активной анкеты для отмены")
            return
        
        await state.clear()
        await message.answer("✅ Анкета отменена. Начните заново: /start", reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        logger.error(f"Ошибка в cmd_cancel: {e}", exc_info=True)

# Команда /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    try:
        text = "ℹ️ Помощь LEVEL FIT\n\n"
        text += "Команды:\n"
        text += "/start - Начать\n"
        text += "/cancel - Отменить анкету\n"
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
    logger.info(f"Channel ID: {CHANNEL_ID or 'НЕ УКАЗАН'}")
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

