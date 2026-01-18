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

# Константы курсов валют
USD_TO_BYN = 2.95
USD_TO_RUB = 78
DEFAULT_CURRENCY = 'BYN'

# Символы валют
CURRENCY_SYMBOLS = {
    'USD': '$',
    'BYN': 'Br',
    'RUB': '₽'
}

# Названия валют
CURRENCY_NAMES = {
    'USD': 'Доллары США',
    'BYN': 'Белорусские рубли',
    'RUB': 'Российские рубли'
}

# Функция для экранирования спецсимволов MarkdownV2
def escape_markdown(text):
    """Экранирует спецсимволы для MarkdownV2"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

# Функция конвертации цен
def convert_price(usd_price, currency='BYN'):
    """Конвертирует цену из USD в выбранную валюту"""
    if currency == 'BYN':
        return round(usd_price * USD_TO_BYN)
    elif currency == 'RUB':
        return round(usd_price * USD_TO_RUB)
    elif currency == 'USD':
        return usd_price
    else:
        return round(usd_price * USD_TO_BYN)  # По умолчанию BYN

# Функция форматирования цены
def format_price(price, currency='BYN'):
    """Форматирует цену с символом валюты"""
    symbol = CURRENCY_SYMBOLS.get(currency, 'Br')
    
    if currency == 'USD':
        return f"${price}"
    else:
        return f"{price} {symbol}"

# Состояния FSM для анкеты
class QuestionnaireStates(StatesGroup):
    waiting_for_fio = State()
    waiting_for_activity = State()
    waiting_for_limitations = State()
    waiting_for_experience = State()
    waiting_for_workouts_count = State()
    waiting_for_height = State()
    waiting_for_weight = State()
    waiting_for_phone = State()
    waiting_for_telegram_nick = State()

# Данные о готовых программах
PROGRAMS = {
    'glutes': {
        'name': 'Стройные ягодицы',
        'emoji': '🍑',
        'price': 30,
        'description': 'Комплексная программа для проработки ягодичных мышц',
        'tribute_links': {
            'RUB': 'https://t.me/tribute/app?startapp=sJD6',
            'USD': 'https://t.me/tribute/app?startapp=sJD6'
        }
    },
    'fatloss': {
        'name': 'Жиру нет',
        'emoji': '🔥',
        'price': 30,
        'description': 'Эффективная программа похудения с сохранением мышц',
        'tribute_links': {
            'RUB': 'https://t.me/tribute/app?startapp=sJD6',
            'USD': 'https://t.me/tribute/app?startapp=sJD6'
        }
    },
    'adaptive': {
        'name': 'Адаптивный фитнес',
        'emoji': '♿',
        'price': 30,
        'description': 'Безопасная программа для людей с ограниченными возможностями',
        'tribute_links': {
            'RUB': 'https://t.me/tribute/app?startapp=sJD6',
            'USD': 'https://t.me/tribute/app?startapp=sJD6'
        }
    },
    'anabolism': {
        'name': 'Анаболизм',
        'emoji': '💪',
        'price': 30,
        'description': 'Программа максимального набора мышечной массы',
        'tribute_links': {
            'RUB': 'https://t.me/tribute/app?startapp=sJD6',
            'USD': 'https://t.me/tribute/app?startapp=sJD6'
        }
    }
}

# Данные о тарифах
PLANS = {
    'programs': {
        'name': 'ГОТОВЫЕ ПРОГРАММЫ',
        'price': 30,
        'emoji': '📦',
        'is_programs': True  # Флаг что это готовые программы
    },
    'start': {
        'name': 'СТАРТ',
        'price': 69,
        'old_price': 90,
        'emoji': '🥈',
        'tribute_links': {
            'RUB': 'https://t.me/tribute/app?startapp=sJ8R',
            'USD': 'https://t.me/tribute/app?startapp=sJD8'
        }
    },
    'optimal': {
        'name': 'ОПТИМА',
        'price': 99,
        'old_price': 150,
        'emoji': '🥇',
        'recommended': True,
        'tribute_links': {
            'RUB': 'https://t.me/tribute/app?startapp=sJ8S',
            'USD': 'https://t.me/tribute/app?startapp=sJD3'
        }
    },
    'vip': {
        'name': 'ПРЕМИУМ VIP',
        'price': 199,
        'old_price': 350,
        'emoji': '👑',
        'tribute_links': {
            'RUB': 'https://t.me/tribute/app?startapp=sJ8P',
            'USD': 'https://t.me/tribute/app?startapp=sJDd'
        }
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

# Клавиатура главного меню
def get_main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Выбрать программу", callback_data="choose_program")],
        [InlineKeyboardButton(text="📋 Оставить заявку", callback_data="leave_application")],
        [InlineKeyboardButton(text="💱 Выбрать валюту", callback_data="change_currency")]
    ])
    return keyboard

# Клавиатура выбора валюты
def get_currency_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇧🇾 Белорусские рубли (Br)", callback_data="currency_BYN")],
        [InlineKeyboardButton(text="🇷🇺 Российские рубли (₽)", callback_data="currency_RUB")],
        [InlineKeyboardButton(text="🇺🇸 Доллары США ($)", callback_data="currency_USD")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")]
    ])
    return keyboard

# Клавиатура выбора цели
def get_goals_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💪 Набор мышечной массы", callback_data="goal_mass")],
        [InlineKeyboardButton(text="🔥 Коррекция фигуры", callback_data="goal_correction")],
        [InlineKeyboardButton(text="⚡ Снижение веса", callback_data="goal_weightloss")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")]
    ])
    return keyboard

# Функция для создания клавиатуры с тарифами
def get_plans_keyboard(currency='BYN'):
    buttons = []
    for plan_id, plan in PLANS.items():
        converted_price = convert_price(plan['price'], currency)
        formatted_price = format_price(converted_price, currency)
        text = f"{plan['emoji']} {plan['name']} - {formatted_price}"
        if plan.get('recommended'):
            text += " ⭐️"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"plan_{plan_id}")])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

# Клавиатура выбора программы
def get_programs_keyboard():
    buttons = []
    for program_id, program in PROGRAMS.items():
        text = f"{program['emoji']} {program['name']}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"program_{program_id}")])
    
    buttons.append([InlineKeyboardButton(text="◀️ К тарифам", callback_data="back_to_plans")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

# Клавиатура для оплаты программы
def get_program_payment_keyboard(program_id: str, currency: str = 'BYN'):
    program = PROGRAMS.get(program_id)
    buttons = []
    
    if program:
        # Для RUB и USD - кнопка "Оплатить" ведет на Tribute
        if currency in ['RUB', 'USD']:
            tribute_links = program.get('tribute_links', {})
            tribute_link = tribute_links.get(currency)
            if tribute_link:
                buttons.append([InlineKeyboardButton(text="💳 Оплатить", url=tribute_link)])
        # Для BYN - кнопка "Оплатить" запускает форму
        else:
            buttons.append([InlineKeyboardButton(text="💳 Оплатить (BYN)", callback_data=f"pay_program_byn_{program_id}")])
    
    # Навигация
    buttons.append([InlineKeyboardButton(text="◀️ К программам", callback_data="back_to_programs")])
    buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


# Функция для создания клавиатуры для тарифа
def get_payment_keyboard(plan_id: str, currency: str = 'BYN'):
    plan = PLANS.get(plan_id)
    buttons = []
    
    if plan:
        # Для RUB и USD - кнопка "Оплатить" ведет на Tribute
        if currency in ['RUB', 'USD']:
            tribute_links = plan.get('tribute_links', {})
            tribute_link = tribute_links.get(currency)
            if tribute_link:
                buttons.append([InlineKeyboardButton(text="💳 Оплатить", url=tribute_link)])
        # Для BYN - кнопка "Оплатить" тоже есть, но запускает анкету
        else:
            buttons.append([InlineKeyboardButton(text="💳 Оплатить", callback_data=f"pay_byn_{plan_id}")])
    
    # Кнопка связаться с тренером (запускает анкету)
    buttons.append([InlineKeyboardButton(text="💬 Связаться с тренером", callback_data=f"contact_{plan_id}")])
    
    # Навигация
    buttons.append([InlineKeyboardButton(text="◀️ К тарифам", callback_data="back_to_plans")])
    buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
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
            
            # Парсим валюту из параметра (формат: plan_CURRENCY или goal_CURRENCY)
            selected_currency = DEFAULT_CURRENCY
            if '_' in param:
                parts = param.split('_')
                logger.info(f"Парсинг параметра: {parts}")
                if len(parts) == 2:
                    param = parts[0]  # Первая часть - plan/goal
                    currency_code = parts[1].upper()
                    logger.info(f"Код валюты из параметра: {currency_code}")
                    if currency_code in CURRENCY_SYMBOLS:
                        selected_currency = currency_code
                        logger.info(f"✅ Валюта установлена из сайта: {selected_currency}")
                    else:
                        logger.warning(f"❌ Неизвестный код валюты: {currency_code}")
            else:
                logger.info(f"Валюта не передана, используется по умолчанию: {DEFAULT_CURRENCY}")
            
            # Устанавливаем валюту в state
            await state.update_data(currency=selected_currency)
            logger.info(f"Валюта сохранена в state: {selected_currency}")
            
            # Проверяем, это цель с сайта или тариф
            if param in GOALS:
                # Это цель с сайта (кнопка "НАЧАТЬ ПРОГРАММУ")
                goal_name = GOALS[param]
                logger.info(f"Пользователь выбрал цель с сайта: {goal_name}")
                
                # Сохраняем цель
                await state.update_data(goal=goal_name, goal_id=param, from_website=True)
                
                # Приветствие с экранированием
                goal_name_escaped = escape_markdown(goal_name)
                text = f"🏋️ *Добро пожаловать в LEVEL FIT\\!*\n\n"
                text += f"Вы выбрали цель: *{goal_name_escaped}*\n\n"
                text += f"Давайте заполним анкету, чтобы создать идеальную программу для вас\\.\n\n"
                text += f"📋 Всего 9 вопросов, это займёт 3\\-4 минуты\\."
                
                await message.answer(text, parse_mode="MarkdownV2")
                
                # Задаем первый вопрос
                await asyncio.sleep(1)
                text_q1 = "1️⃣ *Укажите свои ФИО*\n\nНапример: Иванов Иван Иванович"
                await message.answer(text_q1, parse_mode="MarkdownV2")
                await state.set_state(QuestionnaireStates.waiting_for_fio)
                return
                
            elif param in PLANS:
                # Это выбор тарифа с сайта (кнопка "ВЫБРАТЬ ТАРИФ")
                plan = PLANS[param]
                logger.info(f"Пользователь выбрал тариф с сайта: {plan['name']}")
                
                # Получаем валюту из state (уже установлена выше)
                data = await state.get_data()
                currency = data.get('currency', DEFAULT_CURRENCY)
                
                # Приветствие
                text = f"🏋️ *Добро пожаловать в LEVEL FIT\\!*\n\n"
                text += f"Вы выбрали отличный тариф\\!"
                
                await message.answer(text, parse_mode="MarkdownV2")
                
                # Показываем детали тарифа с кнопками
                await asyncio.sleep(0.5)
                await show_plan_details(message, param, currency)
                return
            else:
                logger.warning(f"Неизвестный параметр: {param}")
        
        # Показываем главное меню (если без параметра или неизвестный параметр)
        logger.info("Показываем главное меню")
        
        # Устанавливаем валюту по умолчанию если не была установлена
        data = await state.get_data()
        if 'currency' not in data:
            await state.update_data(currency=DEFAULT_CURRENCY)
        
        text = "🏋️ *Добро пожаловать в LEVEL FIT\\!*\n\n"
        text += "💪 Онлайн тренировки и персональные программы питания\n\n"
        text += "Что вы хотите сделать?"
        
        await message.answer(text, reply_markup=get_main_menu_keyboard(), parse_mode="MarkdownV2")
        logger.info("Главное меню отправлено")
        
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

# Обработка веса
@dp.message(QuestionnaireStates.waiting_for_weight)
async def process_weight(message: types.Message, state: FSMContext):
    try:
        if not message.text.replace('.', '').replace(',', '').isdigit():
            await message.answer("❌ Пожалуйста, укажите вес числом (например: 70)")
            return
        
        await state.update_data(weight=message.text)
        
        # Переходим к номеру телефона
        text = "8️⃣ *Укажите номер телефона для связи*\n\n"
        text += "Формат: \\+375291234567 или просто 375291234567\n"
        text += "Это нужно для связи с тренером\\."
        
        await message.answer(text, parse_mode="MarkdownV2")
        await state.set_state(QuestionnaireStates.waiting_for_phone)
        
    except Exception as e:
        logger.error(f"Ошибка в process_weight: {e}", exc_info=True)

# Обработка номера телефона
@dp.message(QuestionnaireStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    try:
        phone = message.text.strip()
        
        # Базовая валидация номера
        phone_digits = ''.join(filter(str.isdigit, phone))
        if len(phone_digits) < 10:
            await message.answer("❌ Номер телефона слишком короткий. Пожалуйста, укажите полный номер.")
            return
        
        await state.update_data(phone=phone)
        
        # Проверяем, это оплата программы или полная анкета
        data = await state.get_data()
        is_program = data.get('is_program_payment', False)
        
        # Переходим к Telegram никнейму
        if is_program:
            text = "2️⃣ *Укажите ваш никнейм в Telegram*\n\n"
        else:
            text = "9️⃣ *Укажите ваш никнейм в Telegram*\n\n"
        text += "Например: @username или username"
        
        await message.answer(text, parse_mode="MarkdownV2")
        await state.set_state(QuestionnaireStates.waiting_for_telegram_nick)
        
    except Exception as e:
        logger.error(f"Ошибка в process_phone: {e}", exc_info=True)

# Обработка Telegram никнейма (финальный вопрос)
@dp.message(QuestionnaireStates.waiting_for_telegram_nick)
async def process_telegram_nick(message: types.Message, state: FSMContext):
    try:
        telegram_nick = message.text.strip()
        # Убираем @ если пользователь добавил
        if telegram_nick.startswith('@'):
            telegram_nick = telegram_nick[1:]
        await state.update_data(telegram_nick=telegram_nick)
        
        # Получаем все данные
        data = await state.get_data()
        is_program = data.get('is_program_payment', False)
        
        # Формируем сообщение для пользователя
        user_text = "✅ *Заявка отправлена\\!*\n\n"
        user_text += "Спасибо\\! Тренер свяжется с вами в ближайшее время\\.\n\n"
        if is_program:
            user_text += "📦 Скоро вы начнете программу\\!"
        else:
            user_text += "💪 Начинайте готовиться к трансформации\\!"
        
        await message.answer(user_text, parse_mode="MarkdownV2")
        
        # Общие контакты
        phone = escape_markdown(data.get('phone', 'Не указан'))
        telegram_nick_manual = escape_markdown(data.get('telegram_nick', 'Не указан'))
        username_auto = message.from_user.username or None
        username_display = escape_markdown(username_auto if username_auto else 'скрыт в настройках')
        fullname = escape_markdown(message.from_user.full_name)
        
        # Если это заявка на программу (упрощенная)
        if is_program:
            program_name = escape_markdown(data.get('program_name', 'Не указана'))
            program_emoji = data.get('program_emoji', '📦')
            currency = data.get('currency', DEFAULT_CURRENCY)
            price_converted = convert_price(30, currency)  # Все программы по $30
            price_formatted = escape_markdown(format_price(price_converted, currency))
            
            channel_text = "📦 *ЗАЯВКА НА ПРОГРАММУ \\(BYN\\)*\n\n"
            channel_text += f"{program_emoji} *Программа:* {program_name}\n"
            channel_text += f"💰 *Цена:* {price_formatted}/мес\n"
            channel_text += f"\n📞 *КОНТАКТЫ:*\n"
            channel_text += f"☎️ Телефон: {phone}\n"
            channel_text += f"📱 Telegram \\(авто\\): @{username_display}\n"
            channel_text += f"📱 Telegram \\(указал\\): @{telegram_nick_manual}\n"
            channel_text += f"🆔 ID: {message.from_user.id}\n"
            channel_text += f"👤 Имя в TG: {fullname}"
        
        # Иначе полная анкета
        else:
            fio = escape_markdown(data.get('fio', 'Не указано'))
            goal = escape_markdown(data.get('goal', 'Не указана'))
            activity = escape_markdown(data.get('activity', 'Не указана'))
            limitations = escape_markdown(data.get('limitations', 'Не указано'))
            experience = escape_markdown(data.get('experience', 'Не указан'))
            workouts = escape_markdown(data.get('workouts_count', 'Не указано'))
            height = escape_markdown(data.get('height', 'Не указан'))
            weight = escape_markdown(data.get('weight', 'Не указан'))
            
            channel_text = "📋 *НОВАЯ ЗАЯВКА*\n\n"
            channel_text += f"👤 *ФИО:* {fio}\n"
            
            # Добавляем тариф если выбран
            if data.get('plan_name'):
                plan_name = escape_markdown(data.get('plan_name', ''))
                plan_price_usd = data.get('plan_price', 0)
                currency = data.get('currency', DEFAULT_CURRENCY)
                price_converted = convert_price(plan_price_usd, currency)
                price_formatted = escape_markdown(format_price(price_converted, currency))
                channel_text += f"💎 *Тариф:* {plan_name} \\({price_formatted}/мес\\)\n"
            
            # Добавляем цель если выбрана
            if data.get('goal'):
                channel_text += f"🎯 *Цель:* {goal}\n"
            
            channel_text += f"\n📊 *ПАРАМЕТРЫ:*\n"
            channel_text += f"⚡ Активность: {activity}\n"
            channel_text += f"⚠️ Противопоказания: {limitations}\n"
            channel_text += f"📊 Опыт тренировок: {experience}\n"
            channel_text += f"🏋️ Тренировок в неделю: {workouts}\n"
            channel_text += f"📏 Рост: {height} см\n"
            channel_text += f"⚖️ Вес: {weight} кг\n"
            
            channel_text += f"\n📞 *КОНТАКТЫ:*\n"
            channel_text += f"☎️ Телефон: {phone}\n"
            channel_text += f"📱 Telegram \\(авто\\): @{username_display}\n"
            channel_text += f"📱 Telegram \\(указал\\): @{telegram_nick_manual}\n"
            channel_text += f"🆔 ID: {message.from_user.id}\n"
            channel_text += f"👤 Имя в TG: {fullname}"
        
        # Отправляем в канал
        if CHANNEL_ID:
            await bot.send_message(CHANNEL_ID, channel_text, parse_mode="MarkdownV2")
            logger.info(f"Заявка от {message.from_user.id} отправлена в канал {CHANNEL_ID}")
        
        # Очищаем состояние
        await state.clear()
        
    except Exception as e:
        logger.error(f"Ошибка в process_telegram_nick: {e}", exc_info=True)
        await message.answer("Произошла ошибка при отправке анкеты. Попробуйте снова /start")

# ========== КОНЕЦ ОБРАБОТЧИКОВ АНКЕТЫ ==========


# ========== ОБРАБОТЧИКИ ГЛАВНОГО МЕНЮ ==========

# Кнопка "Оставить заявку" - показываем выбор цели
@dp.callback_query(F.data == "leave_application")
async def process_leave_application(callback: types.CallbackQuery):
    try:
        text = "🎯 *Выберите цель тренировок:*"
        await callback.message.edit_text(text, reply_markup=get_goals_keyboard(), parse_mode="MarkdownV2")
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в process_leave_application: {e}", exc_info=True)

# Кнопка "Выбрать программу" - показываем тарифы
@dp.callback_query(F.data == "choose_program")
async def process_choose_program(callback: types.CallbackQuery, state: FSMContext):
    try:
        # Получаем валюту из state
        data = await state.get_data()
        currency = data.get('currency', DEFAULT_CURRENCY)
        
        text = "🎯 *Выберите подходящий тариф:*"
        await callback.message.edit_text(text, reply_markup=get_plans_keyboard(currency), parse_mode="MarkdownV2")
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в process_choose_program: {e}", exc_info=True)

# Кнопка "Назад" в главное меню
@dp.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: types.CallbackQuery, state: FSMContext):
    try:
        # Очищаем состояние если есть
        await state.clear()
        
        text = "🏋️ *Добро пожаловать в LEVEL FIT\\!*\n\n"
        text += "💪 Онлайн тренировки и персональные программы питания\n\n"
        text += "Что вы хотите сделать?"
        
        await callback.message.edit_text(text, reply_markup=get_main_menu_keyboard(), parse_mode="MarkdownV2")
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в back_to_main_menu: {e}", exc_info=True)

# Обработка выбора цели (из бота, не с сайта)
@dp.callback_query(F.data.startswith("goal_"))
async def process_goal_selection(callback: types.CallbackQuery, state: FSMContext):
    try:
        goal_id = callback.data.split("_")[1]  # mass, correction, weightloss
        
        if goal_id not in GOALS:
            await callback.answer("❌ Неизвестная цель")
            return
        
        goal_name = GOALS[goal_id]
        logger.info(f"Пользователь выбрал цель из бота: {goal_name}")
        
        # Сохраняем цель
        await state.update_data(goal=goal_name, goal_id=goal_id, from_bot=True)
        
        # Приветствие
        goal_name_escaped = escape_markdown(goal_name)
        text = f"✅ Вы выбрали: *{goal_name_escaped}*\n\n"
        text += f"Отлично\\! Давайте заполним анкету\\.\n\n"
        text += f"📋 Всего 9 вопросов, это займёт 3\\-4 минуты\\."
        
        await callback.message.edit_text(text, parse_mode="MarkdownV2")
        await callback.answer()
        
        # Задаем первый вопрос
        await asyncio.sleep(1)
        text_q1 = "1️⃣ *Укажите свои ФИО*\n\nНапример: Иванов Иван Иванович"
        await callback.message.answer(text_q1, parse_mode="MarkdownV2")
        await state.set_state(QuestionnaireStates.waiting_for_fio)
        
    except Exception as e:
        logger.error(f"Ошибка в process_goal_selection: {e}", exc_info=True)
        await callback.answer("❌ Произошла ошибка")

# ========== КОНЕЦ ОБРАБОТЧИКОВ ГЛАВНОГО МЕНЮ ==========


# Показать детали тарифа
async def show_plan_details(message_or_callback, plan_id: str, currency='BYN'):
    try:
        plan = PLANS.get(plan_id)
        
        if not plan:
            logger.error(f"Тариф {plan_id} не найден")
            return
        
        # Если это "Готовые программы" - показываем список программ
        if plan.get('is_programs'):
            text = f"{plan['emoji']} *ГОТОВЫЕ ПРОГРАММЫ*\n\n"
            text += "📹 Видеокурсы с планами тренировок и питания\n"
            text += "💬 Консультации в Telegram чате\n"
            text += "📋 План остается навсегда\n\n"
            text += f"💰 Всего *$30/месяц* за программу\n\n"
            text += "👇 Выберите программу:"
            
            if isinstance(message_or_callback, types.Message):
                await message_or_callback.answer(text, reply_markup=get_programs_keyboard(), parse_mode="MarkdownV2")
            else:
                await message_or_callback.message.edit_text(text, reply_markup=get_programs_keyboard(), parse_mode="MarkdownV2")
            return
        
        discount = int(((plan['old_price'] - plan['price']) / plan['old_price']) * 100)
        
        # Конвертируем цены
        current_price = convert_price(plan['price'], currency)
        old_price = convert_price(plan['old_price'], currency)
        formatted_current = format_price(current_price, currency)
        formatted_old = format_price(old_price, currency)
        
        # Используем MarkdownV2 для зачеркивания
        text = f"{plan['emoji']} *{plan['name']}*\n\n"
        
        if plan_id == 'start':
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
        
        # Зачеркнутая старая цена и новая цена (экранируем символы)
        formatted_old_escaped = escape_markdown(formatted_old)
        formatted_current_escaped = escape_markdown(formatted_current)
        
        text += f"\n💰 Цена: ~{formatted_old_escaped}~ → *{formatted_current_escaped}/месяц*\n"
        text += f"🎁 Скидка: *{discount}%*\n"
        
        if plan.get('recommended'):
            text += "\n⭐️ *РЕКОМЕНДУЕМЫЙ ТАРИФ* ⭐️\n"
        
        text += "\n💳 *Оплатите онлайн* или заполните заявку для связи с тренером\\."
        
        keyboard = get_payment_keyboard(plan_id, currency)
        
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
async def process_plan_selection(callback: types.CallbackQuery, state: FSMContext):
    try:
        plan_id = callback.data.split("_")[1]
        logger.info(f"Выбран тариф {plan_id} пользователем {callback.from_user.id}")
        
        # Получаем валюту из state
        data = await state.get_data()
        currency = data.get('currency', DEFAULT_CURRENCY)
        
        await show_plan_details(callback, plan_id, currency)
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в process_plan_selection: {e}", exc_info=True)
        await callback.answer("Ошибка. Попробуйте снова.")


# Кнопка "Назад к тарифам"
@dp.callback_query(F.data == "back_to_plans")
async def back_to_plans(callback: types.CallbackQuery, state: FSMContext):
    try:
        # Получаем валюту из state
        data = await state.get_data()
        currency = data.get('currency', DEFAULT_CURRENCY)
        
        text = "🎯 *Выберите подходящий тариф:*"
        await callback.message.edit_text(text, reply_markup=get_plans_keyboard(currency), parse_mode="MarkdownV2")
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в back_to_plans: {e}", exc_info=True)


# Кнопка "Оплатить" для BYN - запускаем анкету
@dp.callback_query(F.data.startswith("pay_byn_"))
async def process_pay_byn(callback: types.CallbackQuery, state: FSMContext):
    try:
        plan_id = callback.data.split("_")[2]  # pay_byn_light -> light
        plan = PLANS.get(plan_id)
        
        if not plan:
            await callback.answer("❌ Ошибка")
            return
        
        logger.info(f"Оплата BYN для тарифа: {plan['name']}")
        
        # Сохраняем тариф
        await state.update_data(plan_name=plan['name'], plan_id=plan_id, plan_price=plan['price'], from_bot=True)
        
        # Получаем валюту
        data = await state.get_data()
        currency = data.get('currency', DEFAULT_CURRENCY)
        price_converted = convert_price(plan['price'], currency)
        price_formatted = escape_markdown(format_price(price_converted, currency))
        
        # Сообщение о начале анкеты
        plan_name_escaped = escape_markdown(plan['name'])
        text = f"✅ Тариф: {plan['emoji']} *{plan_name_escaped}* \\({price_formatted}/мес\\)\n\n"
        text += f"Отлично\\! Давайте заполним анкету для оформления\\.\n\n"
        text += f"📋 Всего 9 вопросов, это займёт 3\\-4 минуты\\."
        
        await callback.message.edit_text(text, parse_mode="MarkdownV2")
        await callback.answer()
        
        # Задаем первый вопрос
        await asyncio.sleep(1)
        text_q1 = "1️⃣ *Укажите свои ФИО*\n\nНапример: Иванов Иван Иванович"
        await callback.message.answer(text_q1, parse_mode="MarkdownV2")
        await state.set_state(QuestionnaireStates.waiting_for_fio)
            
    except Exception as e:
        logger.error(f"Ошибка в process_pay_byn: {e}", exc_info=True)
        await callback.answer("❌ Произошла ошибка")

# Кнопка "Связаться с тренером" - запускаем анкету с выбранным тарифом
@dp.callback_query(F.data.startswith("contact_"))
async def process_contact(callback: types.CallbackQuery, state: FSMContext):
    try:
        plan_id = callback.data.split("_")[1]
        plan = PLANS.get(plan_id)
        
        if not plan:
            await callback.answer("❌ Ошибка")
            return
        
        logger.info(f"Пользователь хочет связаться по тарифу: {plan['name']}")
        
        # Сохраняем тариф
        await state.update_data(plan_name=plan['name'], plan_id=plan_id, plan_price=plan['price'], from_bot=True)
        
        # Получаем валюту
        data = await state.get_data()
        currency = data.get('currency', DEFAULT_CURRENCY)
        price_converted = convert_price(plan['price'], currency)
        price_formatted = escape_markdown(format_price(price_converted, currency))
        
        # Сообщение о начале анкеты
        plan_name_escaped = escape_markdown(plan['name'])
        text = f"✅ Тариф: {plan['emoji']} *{plan_name_escaped}* \\({price_formatted}/мес\\)\n\n"
        text += f"Отлично\\! Давайте заполним анкету, чтобы тренер мог связаться с вами\\.\n\n"
        text += f"📋 Всего 9 вопросов, это займёт 3\\-4 минуты\\."
        
        await callback.message.edit_text(text, parse_mode="MarkdownV2")
        await callback.answer()
        
        # Задаем первый вопрос
        await asyncio.sleep(1)
        text_q1 = "1️⃣ *Укажите свои ФИО*\n\nНапример: Иванов Иван Иванович"
        await callback.message.answer(text_q1, parse_mode="MarkdownV2")
        await state.set_state(QuestionnaireStates.waiting_for_fio)
            
    except Exception as e:
        logger.error(f"Ошибка в process_contact: {e}", exc_info=True)
        await callback.answer("❌ Произошла ошибка")


# Обработчик кнопки "Выбрать валюту"
@dp.callback_query(F.data == "change_currency")
async def process_change_currency(callback: types.CallbackQuery, state: FSMContext):
    try:
        # Получаем текущую валюту
        data = await state.get_data()
        current_currency = data.get('currency', DEFAULT_CURRENCY)
        currency_name = CURRENCY_NAMES.get(current_currency, CURRENCY_NAMES[DEFAULT_CURRENCY])
        
        text = f"💱 *Выбор валюты*\n\n"
        text += f"Текущая валюта: *{escape_markdown(currency_name)}*\n\n"
        text += f"Выберите валюту для отображения цен:"
        
        await callback.message.edit_text(text, reply_markup=get_currency_keyboard(), parse_mode="MarkdownV2")
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в process_change_currency: {e}", exc_info=True)
        await callback.answer("❌ Произошла ошибка")

# Обработчик выбора валюты
@dp.callback_query(F.data.startswith("currency_"))
async def process_currency_selection(callback: types.CallbackQuery, state: FSMContext):
    try:
        currency = callback.data.split("_")[1]  # BYN, RUB, USD
        
        if currency not in CURRENCY_SYMBOLS:
            await callback.answer("❌ Неизвестная валюта")
            return
        
        # Сохраняем валюту
        await state.update_data(currency=currency)
        
        currency_name = CURRENCY_NAMES.get(currency, currency)
        text = f"✅ Валюта изменена на: *{escape_markdown(currency_name)}*\n\n"
        text += f"Теперь все цены будут отображаться в этой валюте\\."
        
        await callback.message.edit_text(text, parse_mode="MarkdownV2")
        await callback.answer(f"✅ Выбрано: {currency_name}")
        
        # Задержка перед возвратом в главное меню
        await asyncio.sleep(1)
        
        text = "🏋️ *Добро пожаловать в LEVEL FIT\\!*\n\n"
        text += "💪 Онлайн тренировки и персональные программы питания\n\n"
        text += "Что вы хотите сделать?"
        
        await callback.message.edit_text(text, reply_markup=get_main_menu_keyboard(), parse_mode="MarkdownV2")
        
    except Exception as e:
        logger.error(f"Ошибка в process_currency_selection: {e}", exc_info=True)
        await callback.answer("❌ Произошла ошибка")

# Обработка текста (только если нет активной анкеты)
@dp.message(F.text)
async def handle_text(message: types.Message, state: FSMContext):
    try:
        if message.text.startswith('/'):
            return
        
        # Проверяем, есть ли активная анкета
        current_state = await state.get_state()
        if current_state:
            # Если анкета активна, этот текст будет обработан соответствующим state handler
            return
        
        logger.info(f"Получено сообщение вне анкеты от {message.from_user.id}: {message.text[:50]}")
        
        text = "ℹ️ Чтобы оставить заявку, нажмите /start и выберите нужный вариант."
        await message.answer(text)
            
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


# ========== ОБРАБОТЧИКИ ГОТОВЫХ ПРОГРАММ ==========

# Обработка выбора программы
@dp.callback_query(F.data.startswith("program_"))
async def process_program_selection(callback: types.CallbackQuery, state: FSMContext):
    try:
        program_id = callback.data.split("_")[1]  # glutes, fatloss, adaptive, anabolism
        program = PROGRAMS.get(program_id)
        
        if not program:
            await callback.answer("❌ Программа не найдена")
            return
        
        logger.info(f"Выбрана программа {program['name']} пользователем {callback.from_user.id}")
        
        # Получаем валюту
        data = await state.get_data()
        currency = data.get('currency', DEFAULT_CURRENCY)
        
        # Конвертируем цену
        price_converted = convert_price(program['price'], currency)
        formatted_price = format_price(price_converted, currency)
        formatted_price_escaped = escape_markdown(formatted_price)
        
        # Формируем описание программы
        text = f"{program['emoji']} *{escape_markdown(program['name'])}*\n\n"
        text += f"{escape_markdown(program['description'])}\n\n"
        text += f"💰 *Цена:* {formatted_price_escaped}/месяц\n\n"
        text += "📦 *Что входит:*\n"
        text += "• Видеокурс с тренировками\n"
        text += "• План тренировок и питания\n"
        text += "• Консультации в Telegram\n"
        text += "• Рекомендации по спортпиту\n"
        text += "• План остается навсегда\n\n"
        text += "Выберите способ оплаты:"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_program_payment_keyboard(program_id, currency),
            parse_mode="MarkdownV2"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в process_program_selection: {e}", exc_info=True)
        await callback.answer("❌ Произошла ошибка")

# Оплата программы для BYN (запрос контактов)
@dp.callback_query(F.data.startswith("pay_program_byn_"))
async def process_pay_program_byn(callback: types.CallbackQuery, state: FSMContext):
    try:
        program_id = callback.data.split("_")[3]  # pay_program_byn_glutes -> glutes
        program = PROGRAMS.get(program_id)
        
        if not program:
            await callback.answer("❌ Ошибка")
            return
        
        logger.info(f"Оплата программы BYN: {program['name']}")
        
        # Сохраняем программу
        await state.update_data(
            program_name=program['name'],
            program_id=program_id,
            program_price=program['price'],
            program_emoji=program['emoji'],
            is_program_payment=True
        )
        
        # Получаем валюту
        data = await state.get_data()
        currency = data.get('currency', DEFAULT_CURRENCY)
        price_converted = convert_price(program['price'], currency)
        price_formatted = escape_markdown(format_price(price_converted, currency))
        
        # Сообщение
        program_name_escaped = escape_markdown(program['name'])
        text = f"✅ Программа: {program['emoji']} *{program_name_escaped}*\n"
        text += f"💰 Цена: {price_formatted}/мес\n\n"
        text += "Для оплаты в белорусских рублях оставьте свои контакты, и тренер свяжется с вами\\.\n\n"
        text += "📋 Это займет всего 2 минуты\\."
        
        await callback.message.edit_text(text, parse_mode="MarkdownV2")
        await callback.answer()
        
        # Задаем первый вопрос - номер телефона
        await asyncio.sleep(1)
        text_q1 = "1️⃣ *Укажите номер телефона для связи*\n\n"
        text_q1 += "Формат: \\+375291234567 или просто 375291234567"
        await callback.message.answer(text_q1, parse_mode="MarkdownV2")
        await state.set_state(QuestionnaireStates.waiting_for_phone)
            
    except Exception as e:
        logger.error(f"Ошибка в process_pay_program_byn: {e}", exc_info=True)
        await callback.answer("❌ Произошла ошибка")

# Кнопка "Назад к программам"
@dp.callback_query(F.data == "back_to_programs")
async def back_to_programs(callback: types.CallbackQuery):
    try:
        text = f"📦 *ГОТОВЫЕ ПРОГРАММЫ*\n\n"
        text += "📹 Видеокурсы с планами тренировок и питания\n"
        text += "💬 Консультации в Telegram чате\n"
        text += "📋 План остается навсегда\n\n"
        text += f"💰 Всего *$30/месяц* за программу\n\n"
        text += "👇 Выберите программу:"
        
        await callback.message.edit_text(text, reply_markup=get_programs_keyboard(), parse_mode="MarkdownV2")
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в back_to_programs: {e}", exc_info=True)

# ========== КОНЕЦ ОБРАБОТЧИКОВ ГОТОВЫХ ПРОГРАММ ==========


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

