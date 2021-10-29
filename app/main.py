import threading

import bot
import googleParser

if __name__ == '__main__':

    bot_thread = threading.Thread(target=bot.start)
    bot_thread.start()

    parser_thread = threading.Thread(target=googleParser.start, args=(bot.vk,))
    parser_thread.start()
