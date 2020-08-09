import praw
import pdb
import re
import os
import requests
from bs4 import BeautifulSoup
import csv
from praw.models import MoreComments
import time
from datetime import date
import config

today = date.today()

QUERY = ["covid", "covid-19", "positive cases",
         "social distancing", "corona", "coronavirus", "outbreak"]


def stats():
    URL = 'https://tompkinscountyny.gov/health'
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')

    stats = soup.find_all("td", class_="nbr")

    current = int(stats[2].text) - int(stats[4].text)
    pending_tests = int(stats[1].text.strip())

    print("current positive cases: " +
          str(int(stats[2].text) - int(stats[4].text)))

    print("pending tests: " + stats[1].text.strip())

    # append Cases stats to a text file
    with open("cases.txt", "a") as f:
        f.write(str({str(today): {
            "current_positive": int(stats[2].text) - int(stats[4].text),
            "current_pending_tests": int(stats[1].text.strip())
        }
        }) + ",\n")

    # append Cases stats to a csv file
    with open('cases.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        # column headers: writer.writerow(["Date", "Current_Positive_Cases", "Cumulative_Positive_Cases",  "Total_Recoverd", "Pending_Tests"])

        writer.writerow([str(today), int(stats[2].text) - int(stats[4].text),
                         int(stats[2].text), int(stats[4].text), int(stats[1].text.strip())])

    return current, pending_tests


def login():
    reddit = praw.Reddit(client_id=config.client_id,
                         client_secret=config.client_secret,
                         password=config.password,
                         redirect_uri="http://localhost:8080",
                         user_agent="tompkins_covid_stats by u/dr_hippie",
                         username=config.username)

    print(reddit.user.me())

    return reddit


def run_bot(reddit, posts_replied_to):

    subreddit = reddit.subreddit("Cornell")
    cases, pending = stats()

    for comment in subreddit.comments(limit=200):
        if isinstance(comment, MoreComments):
            continue
        comment_text = comment.body.lower()
        for word in QUERY:
            if word in comment_text and comment.author != reddit.user.me() and comment.id not in posts_replied_to:
                comment.reply("Current Positive Cases in Tompkins County on " +
                              str(today) + " : " +
                              str(cases) + "\n\n Tests Pending : " + str(pending) +
                              "\n\nFor more details visit https://tompkinscountyny.gov/health"
                              )
                print("Bot replying to : ", comment.body)
                posts_replied_to.append(comment.id)

                break

    for submission in subreddit.stream.submissions():
        if len(submission.title.split()) > 100:
            break

        normalized_title = submission.title.lower()

        if submission.id not in posts_replied_to:
            for word in QUERY:
                if word in normalized_title:
                    submission.reply(
                        "Current Positive Cases in Tompkins County on " +
                        str(today) + " : " +
                        str(cases) + "\n\n Tests Pending : " + str(pending) +
                        "\n\nFor more details visit https://tompkinscountyny.gov/health"
                    )

                    print("Bot replying to : ", submission.title)

                # Store the current id into our list
                    posts_replied_to.append(submission.id)
                    break

    with open("posts_replied_to.txt", "w") as f:
        for post_id in posts_replied_to:
            f.write(post_id + "\n")

    time.sleep(10)


def get_saved_items():
    # Create a list
    if not os.path.isfile("posts_replied_to.txt"):
        posts_replied_to = []

    # Or load the list of posts we have replied to
    else:
        with open("posts_replied_to.txt", "r") as f:
            posts_replied_to = f.read()
            posts_replied_to = posts_replied_to.split("\n")
            posts_replied_to = list(filter(None, posts_replied_to))

    return posts_replied_to


reddit = login()
posts_replied_to = get_saved_items()

# print comments_replied_to

while True:
    run_bot(reddit, posts_replied_to)
