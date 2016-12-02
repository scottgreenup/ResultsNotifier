#!/usr/bin/env python3

import argparse
import datetime
import getpass
import mechanicalsoup
import smtplib
import sys
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
        "Your notices are out for {subject}! You got {marks} "
        "which is a {grade}."
    ).format(subject=subject, marks=marks, grade=grade)))

    conn.sendmail(msg['From'], msg['To'], msg.as_string())


parser = argparse.ArgumentParser(description='Get notified when results are posted')
parser.add_argument('--username', type=str, required=True)
#parser.add_argument('--password', type=str, required=True)
parser.add_argument('--subjects', type=str, required=True, nargs='+')
parser.add_argument('--email', type=str, required=True)
args = parser.parse_args()

domain = 'https://sydneystudent.sydney.edu.au/sitsvision/wrd/'
path = 'siw_lgn'

browser = mechanicalsoup.Browser()

login_page = browser.get(domain + path)
login_form = login_page.soup.body.form

login_form.select('#MUA_CODE.DUMMY.MENSYS')[0]['value'] = args.username

password = getpass.getpass(prompt='Unikey password:', stream=None)

login_form.select('#PASSWORD.DUMMY.MENSYS')[0]['value'] = password

try:
    page = browser.submit(login_form, login_page.url)
    path = page.soup.select('#siw_portal_url')[0]['value']
except:
    print('Password is incorrect.')
    sys.exit(1)

print('Password was accepted.')

page = browser.get(domain + path)
path = page.soup.select('#ASSTUPOR01')[0]['href']

page = browser.get(domain + path)
links = page.soup.select('a')

for link in links:
    text = str(link)
    if 'results notice' in text:
        path = link['href']
        break

page = browser.get(domain + path)
soup = page.soup

rows = soup.select("tr")
results = []

for row in rows:
    tds = row.select('td')

    if len(tds) == 0:
        continue

    text = tds[0].text

    if text == 'S1C' or text == 'S2C':
        results.append(row)


for result in results:

    texts = [t.text for t in result.select('td')]


    for subject in args.subjects:
        if texts[1] == subject:

            subject = texts[1]
            marks = (texts[3:] + ['00.0'])[0].strip()
            grade = (texts[4:] + ['NA'])[0].strip()

            print('{} | {} | {}'.format(subject, marks, grade))

            if marks != 'NA':
                send_email(args.email, subject, marks, grade)

