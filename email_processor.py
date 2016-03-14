import email
import email.header
import imaplib
import re
import smtplib
import threading
import uuid
import sys
import traceback

from app import db_session
from models.snippet import Snippet

class Message:
    def __init__(self, uid, rawMessageData):
        self.message = email.message_from_string(rawMessageData)
        self.uid = uid
        self.rawMessageData = rawMessageData

    def subject(self):
        return unicode(email.header.decode_header(self.message["Subject"])[0][0])

    def sender(self):
        return email.utils.parseaddr(self.message["From"])

    def senderEmail(self):
        return self.sender()[1]

    def recipient(self):
        return email.utils.parseaddr(self.message["To"])

    def recipientEmail(self):
        return self.recipient()[1]

    def senderPrettyName(self):
        return self.sender()[0]

    def isReply(self):
        return 'In-Reply-To' in self.message

    """
    Returns None if not found.
    """
    def bodyText(self):
        textSections = filter(lambda x: x.get_content_type() == 'text/plain', self.message.walk())
        return textSections[0].get_payload() if len(textSections) > 0 else None

    """
    Returns None if not found.
    """
    def bodyHtml(self):
        htmlSections = filter(lambda x: x.get_content_type() == 'text/html', self.message.walk())
        return htmlSections[0].get_payload() if len(htmlSections) > 0 else None

    """
    Returns None if not found.
    """
    def bodyHtmlOrText(self):
        result = self.bodyHtml()
        if not result:
            result = self.bodyText()
        return result

class IMAPGetMessagesException(Exception):
    pass

class IMAPSwitchMailboxExcepion(Exception):
    pass

class IMAPMailboxCreateException(Exception):
    pass

class IMAPMoveMessageException(Exception):
    pass

class IMAPDeleteMessageException(Exception):
    pass

class IMAPConnection:
    """
    The connection must already be logged in.
    """
    def __init__(self, imapConnection):
        self.imapConnection = imapConnection
        self.currentMailbox = None

    def __del__(self):
        self.imapConnection.close()
        self.imapConnection.logout()

    def openMailbox(self, mailbox=None):
        if self.currentMailbox:
            self.imapConnection.close()
            self.currentMailbox = None
        if mailbox:
            status, numMessages = self.imapConnection.select(mailbox)
            self.currentMailbox = mailbox
        else:
            status, numMessages = self.imapConnection.select() # Get INBOX
            self.currentMailbox = "INBOX"
        if status != 'OK':
            raise IMAPSwitchMailboxException("could not switch to mailbox %s" % self.currentMailbox)
            self.currentMailbox = None

    def createMailboxIfNotExists(self, mailbox):
        previousMailbox = self.currentMailbox
        if self.currentMailbox:
            self.imapConnection.close()
            self.currentMailbox = None
        status, numMessages = self.imapConnection.select(mailbox)
        if status != 'OK':
            # mailbox does not exist
            createStatus, createMsg = self.imapConnection.create(mailbox)
            if createStatus != 'OK':
                raise IMAPMailboxCreateException("Failed to create mailbox: %s" % mailbox)


    def __getMessage(self, msgUID):
        fetchStatus, rawMessageData = self.imapConnection.uid("FETCH", msgUID, '(RFC822)')
        if fetchStatus != 'OK':
            return None
        else:
            return Message(msgUID, rawMessageData[0][1])

    def getAllMessagesInCurrentMailbox(self):
        status, data = self.imapConnection.uid('SEARCH', None, 'ALL')
        if status != 'OK':
            raise IMAPGetMessagesException("could not get messages in mailbox %s - error %s" % (self.currentMailbox, data))
        messages = map(lambda x: self.__getMessage(x) , data[0].split())
        return [m for m in messages if m is not None]

    def copyMessageToMailbox(self, msgUID, destinationMailbox):
        status, data = self.imapConnection.uid('COPY', msgUID, destinationMailbox)
        if status != 'OK':
            raise IMAPMoveMessageException("could not move message with uid: %s to mailbox %s - error %s" % (msgUID, destinationMailbox, data))

    def deleteMessageFromCurrentMailbox(self, msgUID):
        status, data = self.imapConnection.uid('STORE', msgUID , '+FLAGS', '(\Deleted)')
        if status != 'OK':
            raise IMAPDeleteMessageException("could not delete message with uid: %s from mailbox %s - error %s" % (msgUID, self.currentMailbox, data))

class SMTPConnection:
    def __init__(self, server, userName, password):
        self.smtpConnection = smtplib.SMTP_SSL(server)
        self.smtpConnection.login(userName, password)

    def __del__(self):
        self.smtpConnection.quit()

    def sendMessage(self, sender, receivers, msgString):
        self.smtpConnection.sendmail(sender, receivers, msgString)

class EmailProcessor:
    def __init__(self, config):
        self.config = config

    @staticmethod
    def processMessages(messages, imapConnection):
        for msg in messages:
            try:
                storageMailbox = msg.senderEmail()
                imapConnection.createMailboxIfNotExists(storageMailbox)
                imapConnection.openMailbox()
                imapConnection.copyMessageToMailbox(msg.uid, storageMailbox)
                imapConnection.deleteMessageFromCurrentMailbox(msg.uid)
                # TODO: should extract creation time
                snippet = Snippet(
                    user_id=msg.senderEmail(),
                    recipient=msg.recipientEmail(),
                    text=msg.bodyText(),
                    html=msg.bodyHtml()
                )
                db_session.add(snippet)
            except:
                print "Abandoning processing of message subject: %s sender: %s" % (msg.subject(), msg.senderEmail())
                traceback.print_exc()
        db_session.commit()

    def processInbox(self):
        try:
            userName = self.config['IMAP_CONFIG']['username']
            password = self.config['IMAP_CONFIG']['password']
            conn = imaplib.IMAP4_SSL(self.config['IMAP_CONFIG']['imap_host'])
            conn.login(userName, password)
            imapConnection = IMAPConnection(conn)
            imapConnection.openMailbox()
            inboxMessages = imapConnection.getAllMessagesInCurrentMailbox()
            EmailProcessor.processMessages(inboxMessages, imapConnection)
        finally:
            threading.Timer(30.0, self.processInbox).start()

    def start(self):
        threading.Timer(1, self.processInbox).start()
