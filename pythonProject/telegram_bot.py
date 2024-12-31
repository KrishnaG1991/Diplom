import telebot
from telebot import types
from random import choice
import logging
from googletrans import Translator

bot = telebot.TeleBot("8146419335:AAEEdHIpEIr5XtkM7B-oy9XvOlR9c5g4aIA")  # Замените "YOUR_TOKEN_HERE" на ваш токен

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальная переменная для хранения выбранного языка
user_languages = {}
user_translation_status = {}  # Словарь для отслеживания статуса перевода
questions = {
    "Какой язык программирования используется для создания этого бота?": "python",
    "Сколько дней в неделе?": "7",
    "Какой цвет получается при смешивании красного и синего?": "фиолетовый",
    "Какой самый большой океан на Земле?": "тихий",
}

user_scores = {}


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn_1 = types.InlineKeyboardButton("Послушать случайную музыку 😎", callback_data="music")
    btn_4 = types.InlineKeyboardButton("Открыть меню 👨‍💻HELP👨‍💻", callback_data="help")
    btn_3 = types.InlineKeyboardButton("🧞‍♂️Перевод текста🧞‍♂️", callback_data="translate")
    btn_2 = types.InlineKeyboardButton("🎮️Сыграем в игру?🎮️", callback_data="start_game")
    markup.row(btn_1)
    markup.row(btn_2)
    markup.row(btn_3)
    markup.row(btn_4)
    bot.send_message(message.chat.id, f"{message.from_user.first_name}, смотри, я кое что могу! жмакай кнопки!🤓🤓🤓",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def handle_callback(callback):
    if callback.data == "music":
        bot.send_message(callback.message.chat.id,
                         f'{callback.from_user.first_name}! Отправь мне команду /music для прослушивания музыки.')
    elif callback.data == "translate":
        bot.send_message(callback.message.chat.id,
                         f'{callback.from_user.first_name}! Отправь мне текст для перевода или используй '
                         'команду /setlang для выбора языка перевода.')
    elif callback.data == "help":
        bot.send_message(callback.message.chat.id, f'{callback.from_user.first_name}! Отправь мне команду /help')
    elif callback.data == "start_game":
        bot.send_message(callback.message.chat.id,
                         f'{callback.from_user.first_name}! Отправь мне команду /start_game')
    else:
        bot.send_message(callback.message.chat.id, f'{callback.from_user.first_name}, сорян, скоро добавлю еще что-то!')


@bot.message_handler(commands=['music'])
def music(message):
    music_list = ["nh.mp3", "gtdjiu.mp3", "kavkaz.mp3", "koni.mp3", "last.mp3", "lesnik.mp3", "molodost.mp3",
                  "obojau.mp3"]
    file = open(f"music/{choice(music_list)}", "rb")
    bot.send_audio(message.chat.id, file)


@bot.message_handler(commands=['translate'])
def translate(message):
    bot.send_message(message.chat.id,
                     "Отправь мне текст для перевода или используй команду /setlang для выбора языка перевода.")


@bot.message_handler(commands=['setlang'])
def set_language(message):
    # Проверяем, был ли передан аргумент
    if len(message.text.split()) > 1:
        lang = message.text.split()[1].lower()
        if lang in ['en', 'de']:
            user_languages[message.from_user.id] = lang
            bot.reply_to(message,
                         f'Язык перевода установлен на: {"Английский" if lang == "en" else "Немецкий"}.\n'
                         f'Чтобы  включить перевод, используйте команду /start_translation.')
        else:
            bot.reply_to(message,
                         'Пожалуйста, выберите язык, добавив в конец /setlang: "en" для английского или '
                         '"de" для немецкого.\n'
                         'Чтобы  включить перевод, используйте команду /start_translation.')
    else:
        bot.reply_to(message, 'Пожалуйста, укажите язык: Английский - "/setlang en" или Немецкий - "/setlang de".')


@bot.message_handler(commands=['stop_translation'])
def stop_translation(message):
    user_id = message.from_user.id
    user_translation_status[user_id] = False  # Останавливаем перевод
    bot.reply_to(message,
                 "Перевод текста остановлен. Чтобы снова включить перевод, используйте команду /start_translation.\n"
                 "Либо используй команду /start")


@bot.message_handler(commands=['start_translation'])
def start_translation(message):
    user_id = message.from_user.id
    user_translation_status[user_id] = True  # Запускаем перевод
    bot.reply_to(message, "Перевод текста включен. Теперь вы можете отправлять текст для перевода.\n"
                          "Чтобы  остановить перевод, используйте команду /stop_translation.")


@bot.message_handler(content_types=['text'])
def translate_text(message):
    user_id = message.from_user.id

    # Проверяем, включен ли перевод для данного пользователя
    if user_translation_status.get(user_id, True):  # По умолчанию перевод включен
        translator = Translator()
        text_to_translate = message.text

        # Получаем язык перевода из глобальной переменной или устанавливаем английский по умолчанию
        target_language = user_languages.get(user_id, 'en')

        # Устанавливаем немецкий как целевой язык, если текст содержит "привет"
        if 'привет' in text_to_translate.lower():
            target_language = 'de'

        if not text_to_translate:
            bot.reply_to(message, "Пожалуйста, введите текст для перевода.")
            return

        try:
            # Выполняем перевод
            translated = translator.translate(text_to_translate, src='ru', dest=target_language)
            bot.reply_to(message, f'Переведенный текст: {translated.text}')
        except Exception as e:
            bot.reply_to(message, f"Произошла ошибка при переводе: {str(e)}")
    else:
        bot.reply_to(message, "Перевод текста остановлен. Используйте команду /start_translation для его включения.")


@bot.message_handler(commands=["help"])
def help_info(message):
    bot.send_message(message.chat.id, "<b>Вот, что я могу тебе предложить</b>:\n"
                                      "1. <em>Перевести текст с русского на Английский или Немецкий - "
                                      "'/translate'</em>\n"
                                      "2. <em>Послушать случайную музыку из секретного списка песен - '/music'</em>\n"
                                      "3. <em>Сыграть в игру - '/start_game'</em>", parse_mode='html')


@bot.message_handler(commands=['start_game'])
def start_game(message):
    user_scores[message.from_user.id] = 0  # Инициализируем счет пользователя
    bot.send_message(message.chat.id,
                     f"{message.from_user.first_name}, добро пожаловать в викторину! Напишите /quiz, чтобы начать.")


@bot.message_handler(commands=['quiz'])
def quiz(message):
    question = list(questions.keys())[0]  # Получаем первый вопрос
    bot.send_message(message.chat.id, question)

    # Сохраняем текущий вопрос для пользователя
    bot.register_next_step_handler(message, check_answer, question)


def check_answer(message, question):
    user_answer = message.text.lower()  # Приводим ответ к нижнему регистру
    correct_answer = questions[question].lower()  # Получаем правильный ответ

    if user_answer == correct_answer:
        user_scores[message.from_user.id] += 1  # Увеличиваем счет, если ответ правильный
        bot.send_message(message.chat.id, "Правильно! 🎉")
    else:
        bot.send_message(message.chat.id, f"Неправильно. Правильный ответ: {questions[question]}.")

    # Удаляем вопрос из списка
    del questions[question]

    if questions:  # Если есть еще вопросы
        next_question = list(questions.keys())[0]
        bot.send_message(message.chat.id, next_question)
        bot.register_next_step_handler(message, check_answer, next_question)
    else:
        # Игра окончена
        final_score = user_scores[message.from_user.id]
        bot.send_message(message.chat.id, f"Игра окончена! Ваш результат: {final_score} из {len(user_scores)}.")
        del user_scores[message.from_user.id]  # Удаляем пользователя из словаря


@bot.message_handler(commands=['help_message'])
def help_message(message):
    bot.send_message(message.chat.id,
                     "Используйте команды:\n/start_game - начать игру\n/quiz - начать викторину\n/help_message - помощь")


bot.infinity_polling()
