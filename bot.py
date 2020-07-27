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

today = date.today()

QUERY = ["covid", "covid-19", "positive cases",
         "social distancing", "corona", "coronavirus"]


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

    with open("cases.txt", "a") as f:
        f.write(str({str(today): {
            "current_positive": int(stats[2].text) - int(stats[4].text),
            "current_pending_tests": int(stats[1].text.strip())
        }
        }) + ",\n")

    with open('cases.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        # writer.writerow(["Date", "Current_Positive_Cases", "Cumulative_Positive_Cases",  "Total_Recoverd", "Pending_Tests"])

        writer.writerow([str(today), int(stats[2].text) - int(stats[4].text),
                         int(stats[2].text), int(stats[4].text), int(stats[1].text.strip())])

    return [current, pending_tests]


def login():
    reddit = praw.Reddit(client_id="Fl_aoSHEnmdt2Q",
                         client_secret="lNe7fNE9_-4ltl2urRQoIGPsF-0",
                         password="Chickoo@1607",
                         redirect_uri="http://localhost:8080",
                         user_agent="tompkins_covid_bot by u/dr_hippie 0.1",
                         username="dr_hippie")

    print(reddit.user.me())

    return reddit


#print(reddit.auth.url(["identity"], "...", "permanent"))

# reddit = praw.Reddit('bot')

# reddit.login(REDDIT_USERNAME, REDDIT_PASS)
def run_bot(reddit, posts_replied_to):

    subreddit = reddit.subreddit("Cornell")

    for submission in subreddit.stream.submissions():
        if len(submission.title.split()) > 15:
            break

        normalized_title = submission.title.lower()

        if submission.id not in posts_replied_to:
            for word in QUERY:
                if word in normalized_title:
                    submission.reply(
                        "Current Positive Cases in Tompkins County on " +
                        str(today) + " : " +
                        str(stats()[0])
                    )
                    print("Bot replying to : ", submission.title)

                # Store the current id into our list
                    posts_replied_to.append(submission.id)
                    break

    for comment in subreddit.comments(limit=1000):
        if isinstance(comment, MoreComments):
            continue
        comment = comment.body.lower()
        if word in comment and comment.author != reddit.user.me and comment.id not in posts_replied_to:
            comment.reply("Current Positive Cases in Tompkins County on " +
                          str(today) + " : " +
                          str(stats()[0])
                          )
            posts_replied_to.append(comment.id)

            break

    with open("posts_replied_to.txt", "w") as f:
        for post_id in posts_replied_to:
            f.write(post_id + "\n")

    time.sleep(10)

    # for comment in subreddit.stream.comments():
    #    print(comment.body)
    #    if re.search("covid", comment.body, re.IGNORECASE):
    #        reply = "Current Positive Cases in Tompkins County on " +
    #        str(today) + " : " + str()
    #        comment.reply(reply)
    #        print(reply)


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


reddit = login()
posts_replied_to = get_saved_items()

# print comments_replied_to

while True:
    run_bot(reddit, posts_replied_to)