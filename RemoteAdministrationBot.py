import os
from subprocess import PIPE, Popen
import telebot
import pam
import getpass


bot = telebot.TeleBot(TOKEN)

help_message = '/start - start bot\n/download - download file\n/help - show this message'

home_dir = os.path.expanduser('~')
os.chdir(home_dir)


@bot.message_handler(commands=['help'])
def start_handler(message):
    bot.reply_to(message, help_message)


@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.reply_to(message, help_message)
    msg = bot.send_message(message.chat.id, 'Password:')
    bot.register_next_step_handler(msg, login)


def login(message):
    password = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if not pam.authenticate(getpass.getuser(), password):
        msg = bot.send_message(message.chat.id, 'Password:')
        bot.register_next_step_handler(msg, login)
        return
    bot.send_message(message.chat.id, os.getcwd())


@bot.message_handler(commands=['download'])
def file_downloader(message):
    try:
        path = message.text.split(maxsplit=1)[1]
        doc = open(path, 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_document(message.chat.id, "FILEID")
    except Exception as e:
        bot.reply_to(message, e)


@bot.message_handler(content_types='document')
def command_executor(message):
    file_info = bot.get_file(message.document.file_id)
    file_content = bot.download_file(file_info.file_path)
    file_name = message.document.file_name
    with open(file_name, 'wb') as f:
        f.write(file_content)
    bot.reply_to(message, 'Uploaded')


@bot.message_handler()
def command_executor(message):
    try:
        command = message.text
        if command.split(maxsplit=1)[0] == 'cd':
            if command.split(maxsplit=1)[1] == '~':
                path = home_dir
            else:
                path = os.path.abspath(command.split(maxsplit=1)[1])
            os.chdir(path)
            bot.reply_to(message, path)
        else:
            popen = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
            stdout, stderr = popen.communicate()
            if stdout.decode():
                bot.reply_to(message, stdout.decode())
            else:
                bot.reply_to(message, stderr.decode())
    except Exception as e:
        bot.reply_to(message, e)


bot.enable_save_next_step_handlers()
bot.load_next_step_handlers()
bot.infinity_polling()
