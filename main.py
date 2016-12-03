#!/usr/bin/env python3

import argparse
import datetime
import getpass
import mechanicalsoup
import smtplib
import sys
import time
import re

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to, subject, marks, grade):
    conn = smtplib.SMTP('smtp.mail.com', 587)
    conn.ehlo()
    conn.starttls()
    conn.ehlo()
    conn.login(
        'universityofsydneyresults@mail.com',
        'Utl#OteyoF*^UyUh%qm&u0JKx'
    )

    msg = MIMEMultipart()

    msg['Date'] = datetime.datetime.utcnow().strftime('%c +0000 (UTC)')
    msg['From'] = 'universityofsydneyresults@mail.com'
    msg['To'] = to
    msg['Subject'] = 'University Results Notice'
    msg.attach(MIMEText((
        "Your notices are out for {subject}!\n"
        "https://sydneystudent.sydney.edu.au/"
    ).format(subject=subject, marks=marks, grade=grade)))

    conn.sendmail(msg['From'], msg['To'], msg.as_string())


parser = argparse.ArgumentParser(description='Get notified when results are posted')
parser.add_argument('--username', type=str, required=True)
parser.add_argument('--subjects', type=str, required=True, nargs='+')
parser.add_argument('--email', type=str, required=True)
args = parser.parse_args()

domain = 'https://sydneystudent.sydney.edu.au/sitsvision/wrd/'

def get_results(username, password):
    path = 'siw_lgn'
    browser = mechanicalsoup.Browser()

    # Login to the page
    page = browser.get(domain + path)
    form = page.soup.body.form
    form.select('#MUA_CODE.DUMMY.MENSYS')[0]['value'] = username
    form.select('#PASSWORD.DUMMY.MENSYS')[0]['value'] = password
    try:
        page = browser.submit(form, page.url)
        path = page.soup.select('#siw_portal_url')[0]['value']
    except Exception as e:
        raise Exception('Password not accepted.')

    # Navigate to results, sydneystudent uses a weird hash system

    # Get to the assessments page
    page = browser.get(domain + path)
    path = page.soup.select('#ASSTUPOR01')[0]['href']
    page = browser.get(domain + path)

    # Find the link for the results notice page
    links = page.soup.select('a')
    for link in links:
        text = str(link)
        if 'results notice' in text:
            path = link['href']
            break
    page = browser.get(domain + path)

    # Find all rows relating to results
    rows = page.soup.select("tr")
    results = []
    for row in rows:
        tds = row.select('td')
        if len(tds) == 0:
            continue
        text = tds[0].text
        if text == 'S1C' or text == 'S2C':
            results.append(row)

    subjects = {}

    # Check the results requested, and send e-mail if they are out
    for result in results:
        texts = [t.text for t in result.select('td')]
        for subject in args.subjects:
            if texts[1] == subject:
                subjects[subject] = {
                    'subject': texts[1],
                    'marks': (texts[3:] + ['00.0'])[0].strip(),
                    'grade': (texts[4:] + ['NA'])[0].strip()
                }

    return subjects

def send_email_if_released(subjects, email):
    sent = False
    for k, v in subjects.items():
        if v['grade'] != 'NA':
            send_email(email, subject, marks, grade)
            print('sending {} to {}'.format(v['subject'], email))
            sent = True
    if not sent:
        print('.', end='')
        sys.stdout.flush()

password = getpass.getpass(prompt='Unikey password:', stream=None)

def main():
    while True:
        results = get_results(args.username, password)
        send_email_if_released(results, args.email)
        time.sleep(5 * 60)

main()
