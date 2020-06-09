import requests as r
import telebot as tb
from telebot.types import *

token = "tokeno"
bot = tb.TeleBot(token)


@bot.message_handler(commands=['start', "help"])
def say_hello(message):
    bot.send_message(message.chat.id,
                     "Привет. Этот бот парсит картинки и видео с 2ch.hk. Для использования введи /parse, для парсинга по ссылке - /link")


@bot.message_handler(commands=['parse'])
def spizd(message):
    board = bot.send_message(message.chat.id, "Введи имя доски")
    bot.register_next_step_handler(board, get_board)


@bot.message_handler(commands=['link'])
def spizd_by_link(message):
    answer = bot.send_message(message.chat.id,
                              "Скинь ссылку на тред")
    bot.register_next_step_handler(answer, link_process)


def get_board(message):
    board = message.text;
    thread = bot.send_message(message.chat.id, "Введи номер треда")
    bot.register_next_step_handler(thread, get_thread_proceed, board)


def get_thread_proceed(message, *board):
    thread = str(message.text).replace(".html", "")
    parsePictures(message, board[0], thread)


def link_process(message):
    url = str(message.text).replace(".html", ".json")
    data = r.get(url).json()
    links = download(data)
    reply(links, message)


def parsePictures(message, board, thread):
    data = r.get('https://2ch.hk/' + board + '/res/' + thread + '.json').json()
    links = download(data)
    reply(links, message)


def reply(links, message):
    links = set(links)
    videos = set(filter(lambda val: str(val).endswith(("mp4")), links))
    videos_webm = set(filter(lambda val: str(val).endswith(("webm")), links))
    photos = (links - videos) - videos_webm
    videos = parse_list(videos)
    photos = parse_list(photos)
    webms = parse_list(videos_webm)
    print(photos)
    print(videos)
    try:
        for p in photos:
            bot.send_media_group(message.chat.id, map(lambda val: InputMediaPhoto(val), p))
        # for v in videos:
            # bot.send_media_group(message.chat.id, map(lambda val: InputMediaVideo(val), v))
        for t in webms:
            bot.send_message(message.chat.id, str(t))
    except Exception as e:
        print(e.with_traceback())


def parse_list(info, n=10):
    info = list(info)
    info = [info[i * n:(i + 1) * n] for i in range((len(info) + n - 1) // n)]
    info = list(filter(lambda v: v != [], info))
    return info


def download(data):
    links = []
    for post in data['threads'][0]['posts']:
        for f in post['files']:
            links.append("https://2ch.hk" + f['path'])
    return links


bot.polling()
