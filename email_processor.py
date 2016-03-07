import email
import imaplib
import re
import smtplib
import threading
import uuid

from app import app

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

    def senderPrettyName(self):
        return self.sender()[0]

    def isReply(self):
        return 'In-Reply-To' in self.message

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
    def __init__(self, server, creds):
        self.smtpConnection = smtplib.SMTP_SSL("smtp.gmail.com")
        self.smtpConnection.login(creds.email, creds.password)

    def __del__(self):
        self.smtpConnection.quit()

    def sendMessage(self, sender, receivers, msgString):
        self.smtpConnection.sendmail(sender, receivers, msgString)

class EmailProcessor():
    def __init__(self, config):
        self.config = config

    @staticmethod
    def isSnippetTest(message):
        return not message.isReply() and message.subject().find("SnippetTest") != -1

    @staticmethod
    def isCommandMessage(message):
        return isSnippetTest(message)

    """
    Process any special command messages and return the filtered list.  These include:
      Subject contains "SnippetTest" and is not a reply - send me a test snippet prompt
    """
    @staticmethod
    def processCommandMessages(messages, imapConnection, smtpConnection):
        commandMessages = filter(lambda m: isCommandMessage(m), messages)
        print "Found %d command messages" % len(commandMessages)
        for cmdMsg in commandMessages:
            if isSnippetTest(cmdMsg):
                testSnippetUUID = uuid.uuid4()
                print "Creating test snippet prompt with test uuid: %s and delivering to %s" % (str(testSnippetUUID), cmdMsg.senderEmail())
                receivers = [cmdMsg.senderEmail()]
                sender = "snippets@twitter.com"
                testSnippetEmail = email.mime.text.MIMEText("Hi %s! You have requested a test snippet prompt, and here it is" % (cmdMsg.senderPrettyName()))
                testSnippetEmail['Subject'] = "Test Snippet Prompt UUID: %s" % str(testSnippetUUID)
                testSnippetEmail['From'] = sender
                testSnippetEmail['To'] = ",".join(receivers)
                smtpConnection.sendMessage(sender, receivers, testSnippetEmail.as_string())
                imapConnection.createMailboxIfNotExists(cmdMsg.senderEmail())
                imapConnection.openMailbox() # open INBOX
                imapConnection.copyMessageToMailbox(cmdMsg.uid, cmdMsg.senderEmail())
                imapConnection.deleteMessageFromCurrentMailbox(cmdMsg.uid)
        return filter(lambda m: not isCommandMessage(m), messages)

    @staticmethod
    def processNonCommandMessages(nonCommandMessages, imapConnection, smtpConnection):
        for msg in nonCommandMessages:
            print "Message subject: %s sender: %s" % (msg.subject(), msg.senderEmail())

    def processInbox(self):
      print "Processing inbox"
      conn = imaplib.IMAP4_SSL(self.config['EMAIL']['imap_host'])
      conn.login(self.config['EMAIL']['username'], self.config['EMAIL']['password'])
      imapConnection = IMAPConnection(conn)
      imapConnection.openMailbox()
      inboxMessages = imapConnection.getAllMessagesInCurrentMailbox()
      print "Fetched %d messages" % (len(inboxMessages))
      # f = open("/Users/kgalloway/emailsample.txt", "wb")
      # f.write(inboxMessages[0].rawMessageData)
      smtpConnection = SMTPConnection(self.config['EMAIL']['smtp_host'], creds)
      nonCommandMessages = processCommandMessages(inboxMessages, imapConnection, smtpConnection)
      print "Fetched %d non-command messages" % (len(nonCommandMessages))
      processNonCommandMessages(nonCommandMessages, imapConnection, smtpConnection)
      threading.Timer(30.0, processInbox).start()

    def start(self):
      threading.Timer(1, self.processInbox).start()

if __name__ == "__main__":
  EmailProcessor(app.config).start()
