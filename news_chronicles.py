from sys import exit as abort
from urllib.error import URLError
from urllib.request import urlopen
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Progressbar
from re import *
from webbrowser import open as urldisplay
from datetime import datetime
from os.path import *
from os import getcwd

news_archive = 'NewsArchive'
timestamp = ''
news_archive_filename = ''
latest_timestamp = ''
file_names = [] 

def save_file_names():
    with open('saved_file_names.txt', 'w') as file:
        for name in file_names:
            file.write(name + '\n')

def read_saved_file_names():
    global file_names
    try:
        with open('saved_file_names.txt', 'r') as file:
            file_names = file.read().splitlines()
    except FileNotFoundError:
        file_names = []

def current_news_archive():
    from urllib.error import HTTPError
    url = 'https://www.gamespot.com/feeds/game-news'
    try:
        web_page = urlopen(url)
    except (ValueError, HTTPError, URLError, Exception) as message:
        error_message_box.insert(END, f"\nError: {message}")
        error_message_box.config(bg="red", fg="white")
        return
    else:
        global timestamp, news_archive_filename, latest_timestamp
        timestamp = datetime.now().strftime('%A, %d %B %Y')
        news_archive_filename = f'{news_archive}/{timestamp}'
        latest_timestamp = timestamp
        web_page_chars = web_page.read().decode('utf-8')
        with open(news_archive_filename + '.xml', 'w', encoding='utf-8') as file:
            file.write(web_page_chars)
        file_names.append(news_archive_filename)
        save_file_names()
        news_list_box.delete(0, END)
        display_file_names(news_list_box)

def generate_news_item(title, media_url, full_story_link, description, pubdate):
    return f"""
        <item>
            <h2 style="color: white; text-align: center;">{title}</h2>
            <div style="text-align: center; color: white;">
                <img src="{media_url}" Alt = "Images">
            </div>
            <h4 style="color: white;">Description: {description}</h4>
            <strong style="color: white;">Full story: <a href="{full_story_link}">{full_story_link}</a></strong>
            <h4 style="color: white;">Public Date: {pubdate}</h4>
        </item>
    """

def generate_html_page(selected_title, selected_media, full_story_link, selected_description, selected_pubdate):
    html_items = "".join(generate_news_item(selected_title[i], selected_media[i], full_story_link[i], selected_description[i], selected_pubdate[i]) for i in range(5))
    return f"""
    <html>
    <body style="background-image: url('html_background.gif'); background-size: cover; max-width: 800px; margin: auto;">
        <h1 style="text-align: center; color: white">GameSpot - Game News</h1>
        <h2 style="text-align: center; color: white">{file_name_without_extension}</h2>
        <div style="text-align: center">
            <img src="Gamespot-logo.png" alt="Gamespot_logo" width="200" height="200">
        </div>
        <h3 style="color: white;" >News source: <a href="{selected_link}">https://www.gamespot.com/feeds/game-news</a></h3>
        <h3 style="color: white;">Chronicler: Your Name</h3>
        {html_items}
    </body>
    </html>
    """

def parse_page(selected_item):
    global file_name_without_extension
    file_name_without_extension = splitext(selected_item)[0]
    file_path = f'{news_archive}/{selected_item}'
    try:
        with open(file_path + '.xml', 'r') as open_file_html:
            file_content = open_file_html.read()
    except FileNotFoundError:
        print("File not found!")
        return

    try:
        title_pattern, media_pattern, link_pattern, description_pattern, pubdate_pattern = '<title>(.*?)</title>', '<media:content url="([^"]+)"', '<link>(.*?)</link>', '<p>(.*?)</p>', '<pubDate>(.*?)</pubDate>'
        selected_title = findall(title_pattern, file_content)[1:6]
        selected_media = findall(media_pattern, file_content)[0:5]
        global selected_link
        selected_link = findall(link_pattern, file_content)[0]
        full_story_link = findall(link_pattern, file_content)[1:6]
        selected_description = findall(description_pattern, file_content)[0:5]
        selected_pubdate = findall(pubdate_pattern, file_content)[0:5]
        html_page = generate_html_page(selected_title, selected_media, full_story_link, selected_description, selected_pubdate)
        with open("summary.html", "w") as html_file:
            html_file.write(html_page)
    except Exception as e:
        print(f"Error parsing page: {e}")
        return

    urldisplay(f'file:///{getcwd()}/summary.html')

def display_file_names(news_list_box):
    for name in file_names:
        text_file_name = name.split("/")[1]
        news_list_box.insert(END, 'latest' if text_file_name == latest_timestamp else text_file_name)

def selected_item_listbox():
    selected_index = news_list_box.curselection()
    if selected_index:
        selected_item = news_list_box.get(selected_index)
        if selected_item == 'latest':
            selected_item = latest_timestamp if latest_timestamp else 'No file found'
        parse_page(selected_item)

news_window = Tk()
news_window.geometry("500x500")
news_window.title('Gamespot News')

website_logo = PhotoImage(file='Gamespot-logo.png')
image = Label(news_window, image=website_logo)
title = Label(news_window, text='GameSpot', font=('Courier New', 40))
archive_news = Button(news_window, text='Archive current news from the web', command=current_news_archive)
summary_news = Button(news_window, text='Scrape and Display summary', command=selected_item_listbox)
news_list_box = Listbox(news_window, height=10, width=40, bg='brown2', fg='white', font='Helvetica 18 bold')
error_message_box = Listbox(news_window, height=5, width=60)

image.pack()
title.pack()
news_list_box.pack()
error_message_box.pack(padx=20)
archive_news.pack(side=LEFT)
summary_news.pack(side=RIGHT)
read_saved_file_names()
display_file_names(news_list_box)
news_window.mainloop()
