# import necessary libraries
import telebot
import requests
import time
import os

from bs4 import BeautifulSoup

# set Telegram API token
token = "TELEGRAM_BOT_TOKEN"
bot = telebot.TeleBot(token)

# check if the file to store the latest news URL exists, if not create it
if not os.path.exists("latest_news_url.txt"):
    with open("latest_news_url.txt", "w") as f:
        f.write("")

# define function to get the latest news URL from the file
def get_latest_news_url():
    with open("latest_news_url.txt", "r") as f:
        latest_news_url = f.read().strip()
    return latest_news_url

# define function to save the latest news URL to the file
def save_latest_news_url(latest_news_url):
    with open("latest_news_url.txt", "w") as f:
        f.write(latest_news_url)

# define handler function for the '/start' command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # send welcome message and menu to the user
    bot.send_message(message.chat.id,
                     "Вітаю! За допомогою цього бота Ви зможете відсвідковувати новини з порталу LB.ua.\nНатисніть на [Останні новини], щоб почати отримувати новини.",
                     reply_markup=get_menu())

# define handler function for any message
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == "📰 Останні новини":
        latest_news_url = get_latest_news_url()
        while True:
            post_text = parser(latest_news_url)
            if post_text is not None:
                title, post_description, url = post_text
                bot.send_message(message.chat.id,
                                 f"❗ {title}\n\n{post_description}\n______________________\nДеталі за посиланням ⬇ \n{url}")
                latest_news_url = url
                save_latest_news_url(latest_news_url)
            time.sleep(120)
    elif message.text == "🤖 Що робить цей бот?":
        # send a brief description of what the bot does
        bot.send_message(message.chat.id, "Цей бот надсилає новини з порталу LB.ua")
    else:
        # send an error message and the menu to the user
        bot.send_message(message.chat.id,
                         "Незрозуміла команда. Будь ласка, використовуйте меню. Для відображення меню введіть /start.",
                         reply_markup=get_menu())

# define a function to scrape the latest news

def parser(latest_news_url):
# define the URL of the news portal
    URL = "https://lb.ua/newsfeed"
    # send a request to the URL and get the HTML content
    page = requests.get(URL)

    # parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(page.content, "html.parser")

    # find the first news item on the page
    post = soup.find("li", class_="item-news")

    # extract the post description
    post_description = post.find("span", class_="summary").text.strip()

    # extract the URL of the news item
    url = post.find("div", class_="title").find("a")["href"]

    # check if the latest news URL is different from the current URL
    if url != latest_news_url:
        # extract the news title
        title = post.find("div", class_="title").text.strip()
        return title, post_description, url
    else:
        return None

# define a function to create the menu
def get_menu():
    menu = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu.add(telebot.types.KeyboardButton("📰 Останні новини"))
    menu.add(telebot.types.KeyboardButton("🤖 Що робить цей бот?"))
    return menu

# start polling for new messages from the user
bot.polling()
