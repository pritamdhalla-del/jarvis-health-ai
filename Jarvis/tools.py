import webbrowser
import os

def open_chrome():
    os.system("start chrome")
    return "Chrome Opened"

def play_youtube(query):

    url = f"https://www.youtube.com/results?search_query={query}"

    webbrowser.open(url)

    return f"Playing {query}"

def search_google(query):

    url = f"https://www.google.com/search?q={query}"

    webbrowser.open(url)

    return f"Searching Google for {query}"