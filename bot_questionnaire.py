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
CHANNEL_ID = os.getenv('CHANNEL_ID', '-1002370103949')  # Замените на ваш канал

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

# Состояния FSM
class QuestionnaireStates(StatesGroup):
    waiting_for_fio = State()
    waiting_for_activity = State()
    waiting_for_limitations = State()
    waiting_for_experience = State()
    waiting_for_workouts_count = State()
    waiting_for_height = State()
    waiting_for_weight = State()

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

# Команда /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    try:
        logger.info(f"Получена команда /start от {message.from_user.id} (@{message.from_user.username})")
        
        # Очищаем предыдущее состояние
        await state.clear()
        
        # Проверяем параметр цели
        args = message.text.split()
        goal_id = args[1] if len(args) > 1 else None
        
        if goal_id and goal_id in GOALS:
            goal_name = GOALS[goal_id]
            logger.info(f"Пользователь выбрал цель: {goal_name}")
            
            # Сохраняем цель
            await state.update_data(goal=goal_name, goal_id=goal_id)
            
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
            
        else:
            # Если цель не выбрана
            text = "🏋️ *Добро пожаловать в LEVEL FIT\\!*\n\n"
            text += "Выберите цель на сайте и нажмите кнопку НАЧАТЬ ПРОГРАММУ\\.\n\n"
            text += "🌐 Сайт: https://zcredi\\.github\\.io/levelfit/"
            
            await message.answer(text, parse_mode="MarkdownV2")
            
    except Exception as e:
        logger.error(f"Ошибка в cmd_start: {e}", exc_info=True)
        await message.answer("Произошла ошибка. Попробуйте позже.")

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
        await bot.send_message(CHANNEL_ID, channel_text, parse_mode="MarkdownV2")
        logger.info(f"Заявка от {message.from_user.id} отправлена в канал {CHANNEL_ID}")
        
        # Очищаем состояние
        await state.clear()
        
    except Exception as e:
        logger.error(f"Ошибка в process_weight: {e}", exc_info=True)
        await message.answer("Произошла ошибка при отправке анкеты. Попробуйте снова /start")

# Команда /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    try:
        text = "ℹ️ *Помощь LEVEL FIT*\n\n"
        text += "Команды:\n"
        text += "/start \\- Начать заполнение анкеты\n"
        text += "/cancel \\- Отменить текущую анкету\n"
        text += "/help \\- Помощь\n\n"
        text += "🌐 Сайт: https://zcredi\\.github\\.io/levelfit/"
        
        await message.answer(text, parse_mode="MarkdownV2")
    except Exception as e:
        logger.error(f"Ошибка в cmd_help: {e}", exc_info=True)

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

# Запуск
async def main():
    logger.info("="*50)
    logger.info("🤖 LEVEL FIT БОТ (АНКЕТА) ЗАПУСКАЕТСЯ...")
    logger.info(f"Bot Token: {BOT_TOKEN[:20]}...")
    logger.info(f"Channel ID: {CHANNEL_ID}")
    logger.info("="*50)
    
    try:
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

