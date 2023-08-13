import telebot
import threading
import instaloader  # pip install instaloader
from os import walk
import zipfile
import os
import shutil

API_TOKEN = "YOUR-API-TOKEN"
bot = telebot.TeleBot(API_TOKEN)
username = ""
password = ""
account_set = False


@bot.message_handler(commands=['start'])
def start_choice(message):
    msg_to_send = "hello!" \
                  "\nthis is insta downloader!" \
                  "\nplease set your /setting to start downloading by just sending the link!" \
                  "\nto start downloading use /download and send your link"
    bot.reply_to(message, msg_to_send)


@bot.message_handler(commands=['setting'])
def account_setup(message):
    msg_to_send = "please send us your instagram username"
    sent_msg = bot.send_message(message.chat.id, msg_to_send)
    # print("ok " * 10)
    bot.register_next_step_handler(sent_msg, username_get)


def username_get(message):
    global username
    username = message.text
    msg_to_send = f"ok so your username is: {message.text}" \
                  f"\nplease send us your password and we are good to go"
    sent_msg = bot.send_message(message.chat.id, msg_to_send)
    bot.register_next_step_handler(sent_msg, password_get)


def password_get(message):
    global password
    password = message.text
    msg_to_send = f"username: {username}" \
                  f"\npassword: {password}" \
                  f"\nis this true?(yes or no)"
    sent_msg = bot.send_message(message.chat.id, msg_to_send)
    bot.register_next_step_handler(sent_msg, confirm_info)


def confirm_info(message):
    if message.text.lower() == 'no':
        msg_to_send = "ok so let's try again /setting"
        sent_msg = bot.send_message(message.chat.id, msg_to_send)
        # bot.register_next_step_handler(sent_msg, account_setup_again)
    elif message.text.lower() == 'yes':
        global account_set
        account_set = True
        msg_to_send = "alright let's start downloading stuff /download" \
                      "\nby the way you can change your account /setting later"
        bot.send_message(message.chat.id, msg_to_send)
    else:
        msg_to_send = "not recognized command, try again(yes or no)"
        sent_msg = bot.send_message(message.chat.id, msg_to_send)
        bot.register_next_step_handler(sent_msg, confirm_info)


# def account_setup_again(message):
#     msg_to_send = "please send us your instagram user name(e.g. insta_downloader)"
#     sent_msg = bot.send_message(message.chat.id, msg_to_send)
#     bot.register_next_step_handler(sent_msg, username_get)


@bot.message_handler(commands=['download'])
def download_link(message):
    if account_set:
        msg_to_send = "ok send a valid link"
        sent_msg = bot.send_message(message.chat.id, msg_to_send)
        bot.register_next_step_handler(sent_msg, start_download)
    else:
        msg_to_send = "you should set your instagram account info first using /setting"
        bot.send_message(message.chat.id, msg_to_send)


def start_download(message):
    link = message.text  # e.g. https://www.instagram.com/reel/CvwxH3loPRk

    def download():
        if 'www.instagram.com' in link:
            try:
                index = link.find('www.instagram.com/') + len('www.instagram.com/')
                selected_link = link[index:]
                # print(selected_link)
                index = 1
                counter = -1
                for letter in selected_link:
                    counter += 1
                    if not letter.isalpha():
                        index = counter
                        break
                post_type = selected_link[:index]  # stories can't be downloaded (available soon)
                selected_link = selected_link[index + 1:]
                url = ""
                if "/" in selected_link:
                    url = selected_link[:selected_link.find('/')]
                else:
                    url = selected_link
                insta_loader = instaloader.Instaloader()
                # insta_loader.login(user=username, passwd=password)
                # print("login ok")
                insta_loader.load_session_from_file(username)
                post = instaloader.Post.from_shortcode(insta_loader.context, url)
                insta_loader.download_post(post, target=url)
                filenames = next(walk(f"./{url}"), (None, None, []))[2]
                names = []
                # for name in filenames:
                #     dot_index = -1
                #     counter = 0
                #     for letter in range(0, len(name), -1):
                #         counter += 1
                #         if letter == '.':
                #             dot_index = counter
                #             break
                #     new_name = name[:-1 * dot_index]
                #     names.append(new_name)
                zip_file = zipfile.ZipFile(f'.\\{url}.zip', 'w')
                for folder, subfolders, files in os.walk(f'.\\{url}'):
                    for file in files:
                        if not file.endswith('.xy') or not file.endswith('.txt'):
                            zip_file.write(os.path.join(folder, file),
                                           os.path.relpath(os.path.join(folder, file), f'.\\{url}'),
                                           compress_type=zipfile.ZIP_DEFLATED)
                zip_file.close()
                with open(f"{url}.zip", "rb") as file:
                    bot.send_document(message.chat.id, file)
                file_to_remove = f"{url}.zip"
                containing_location = ".\\"
                path = os.path.join(containing_location, file_to_remove)
                os.remove(path)
                # print("removing folder")
                directory = f"{url}"
                parent = ".\\"
                path = os.path.join(parent, directory)
                shutil.rmtree(path)
                # print("folder removed")
                msg_to_send = "done! you can download another using /download"
                bot.send_message(message.chat.id, msg_to_send)
                print("a post downloaded successfully")
            except:
                msg_to_send = f"something went wrong while downloading, please try again using /download"
                bot.send_message(message.chat.id, msg_to_send)
        else:
            msg_to_send = "it seems you have entered a invalid link, please try again using /download"
            bot.send_message(message.chat.id, msg_to_send)

    threading.Thread(target=download).start()


bot.infinity_polling()
