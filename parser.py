import requests
from bs4 import BeautifulSoup
import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter

# Most code here inspired by 
# https://www.youtube.com/watch?v=KJ5bFv-IRFM&list=PLzMcBGfZo4-kqyzTzJWCV6lyK-ZMYECDc
# https://www.youtube.com/watch?v=6gHvqXrfjuo&list=PLzMcBGfZo4-kqyzTzJWCV6lyK-ZMYECDc&index=2

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET'], '/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel_id')
    ts = event.get('ts')
    text = event.get('text')
    parsed = parse_text(text)
    # client.chat_postMessage(channel=channel_id, ts=ts, text=parsed)
    client.chat_postMessage(channel='#na', text=parsed)

def parse_text(text, token = 'arxiv.org/pdf', return_prefix='https://arxiv.org/abs/'):
    # converts type from https://arxiv.org/pdf/2005.14165.pdf to https://arxiv.org/abs/2005.14165
    # TODO more than one instance
    if token in text: 
        paper_id = text.split('.pdf')[0].split('/')[-1]
        abs_url = return_prefix + paper_id

        abs_html = requests.get(url = abs_url).text

        soup = BeautifulSoup(abs_html, "html.parser")

        title = soup.find("meta", property="og:title")['content']
        desc = soup.find("meta", property="og:description")['content']
        desc = desc.split('.')[0]
        return title + '\n' + desc

if __name__=='__main__':
    app.run(debug=True)