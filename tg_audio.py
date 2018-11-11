import telepot

from requests import get
from random import randint
from time import sleep
from json import loads
from os import path, mkdir


# Your registered bot's token
bot_token = ''


def get_file_path(token, file_id):
    get_path = get('https://api.telegram.org/bot{}/getFile?file_id={}'.format(token, file_id))
    json_doc = loads(get_path.text)
    try:
        file_path = json_doc['result']['file_path']
    except Exception as e:  # Happens when the file size is bigger than the API condition
        print('Cannot download a file because the size is more than 20MB')
        return None

    return 'https://api.telegram.org/file/bot{}/{}'.format(token, file_path)


def get_file(msg_list, chat_id):
    if len(msg_list) > 1:
        msg_count = len(msg_list)
        print('Total files: {}'.format(msg_count))

    for msg in msg_list:
        try:
            mp3id = msg['message']['audio']['file_id']
        except KeyError:
            continue

        try:
            singer = msg['message']['audio']['performer']
        except:
            singer = 'Unknown'

        # Remove / and - characters to create directory
        singer_dir = singer.replace('/', '-').strip()

        try:
            song_name = msg['message']['audio']['title']
        except:
            song_name = str(randint(120, 1900000000))

        if path.exists('{}/{}_{}.mp3'.format(singer_dir, singer, song_name)):
            print('{} {} --> File exists'.format(singer, song_name))
            continue

        print('Working on --> {} {}'.format(singer, song_name))
        # Get file download path
        download_url = get_file_path(bot_token, mp3id)
        mp3file = get(download_url)
        if download_url is None:
            continue

        if not path.exists(singer_dir):
            mkdir(singer_dir)

        try:
            with open('{}/{}_{}.mp3'.format(singer_dir, singer, song_name), 'wb') as f:
                f.write(mp3file.content)
        except FileNotFoundError:
            with open('{}.mp3'.format(randint(120, 1900000000)), 'wb') as f:
                f.write(mp3file.content)

        bot.sendMessage(chat_id, 'Done: {} {}'.format(singer, song_name))


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    usermsg = bot.getUpdates(allowed_updates='message')
    get_file(usermsg, chat_id)


def main():
    bot.message_loop(handle)
    # Keep the program running
    while 1:
        sleep(10)


if __name__ == '__main__':
    bot = telepot.Bot(bot_token)
    main()

