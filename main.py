from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from flask import Flask, request, abort, render_template
import re

import config

client = Client(config.account, config.token)
twilio_number = config.number

app = Flask(__name__)


def send_sms(to: str, body: str) -> None:
    client.messages.create(to=to, from_=twilio_number, body=body)


def is_valid_number(number: str) -> bool:
    try:
        response = client.lookups.phone_numbers(number).fetch(type="carrier")
        return True
    except TwilioRestException as e:
        if e.code == 20404:
            return False
        else:
            raise e


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        number = re.sub("\D", "", request.form['telephone'])
        if is_valid_number(number):
            pass
            # 1. add number to db
            send_sms("+" + number, "Thank you for signing up for EPL game notifications!")
            return render_template('registered.html')

    return render_template('index.html')


@app.route('/webhook', methods=['POST'])
def webhook():
    number = ""

    if request.method == 'POST':
        response = request.json
        if 'matches_count' in response and response['matches_count'] > 0:
            for match in response['results']:
                text_body = "{0} vs. {1} at {2}".format(match['home_team']['team_name'],
                                                        match['away_team']['team_name'],
                                                        match['start_datetime']['datetime'])

                send_sms(number, text_body)
        return '', 200

    else:
        abort(400)
