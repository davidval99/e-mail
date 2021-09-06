import sys
import os
from twisted.mail import smtp, maildir
from twisted.internet import protocol, reactor
from twisted.mail import relaymanager
from zope.interface import implementer
from email.header import Header
from twisted.names import client


mxCalc = relaymanager.MXCalculator()

@implementer(smtp.IMessage)
class MaildirMessageWriter(object):
    """
    MaildirMessageWriter uses the maildir.MaildirMailbox class provided by twisted.mail to write
    to the Inbox maildir in each user's directory.
    """
    def __init__(self, user):

        if not os.path.exists(userDir):
            os.mkdir(userDir)

        destDir = os.path.join(userDir,str(user.dest))
        if not os.path.exists(destDir):
            os.mkdir(destDir)

        inboxDir = os.path.join(destDir, 'Inbox')
        self.mailbox = maildir.MaildirMailbox(inboxDir)
        self.lines = []

    def lineReceived(self, line):
        if type(line) != str:
            line = line.decode("utf-8")
        self.lines.append(line)

    def eomReceived(self):
        # message is complete, store it
        self.lines.append('')
        messageData = '\n'.join(self.lines)
        return self.mailbox.appendMessage(bytes(messageData,'utf-8'))

    def connectionLost(self):
        # unexpected loss of connection; don't save
        del self.lines

@implementer(smtp.IMessageDelivery)
class LocalDelivery(object):

    def __init__ (self, userDir ,validDomains):
        self.validDomains = validDomains
        self.userDir = userDir

    def receivedHeader (self, helo, origin, recipients):

        client, clientIP= helo
        recipient = recipients[0]
        myself= 'localhost'
        value= """from %s [%s] by %s with SMTP for %s; %s""" % (
            client.decode("utf-8"), clientIP.decode("utf-8"), myself, recipient, smtp.rfc822date().decode("utf-8")
            )
        # email.Header.Header used for automatic wrapping of long lines
        return "Received: %s" % Header(value)

    def validateFrom (self, helo, originAddress):

        """
        Checks that from domain is right
        """
        self.client = helo
        return originAddress

    def validateTo(self, user):
        """
        Checks that to domain is right
        """
        if user.dest.domain.decode("utf-8") in self.validDomains:
            print("Domain: %s accepted" % user.dest.domain.decode("utf-8"))
            print("SMTP server is waiting for connections...")
            print()
            return lambda: MaildirMessageWriter(user)
        else:
            print("Domain: %s not supported" % user.dest.domain.decode("utf-8"))
            print("SMTP server is waiting for connections... \n")

            raise smtp.SMTPBadRcpt(user)

class SMTPFactory (protocol.ServerFactory):
    def __init__(self, userDir ,validDomains):
        print("Ok! ")
        print("SMTP server is waiting for connections...")
        print()
        self.validDomains = validDomains
        self.userDir = userDir

    def buildProtocol(self, addr):
        """
        Build protocol for email reception
        """
        delivery = LocalDelivery(self.userDir,self.validDomains)
        smtpProtocol = smtp.SMTP(delivery)
        smtpProtocol.factory = self
        return smtpProtocol

#python3 smtpserver.py -d <domains> -s <mail-storage> -p <port>
if __name__=='__main__':
    domains = sys.argv[2].split(',')
    userDir = sys.argv[4]
    port = int(sys.argv[6])
    reactor.listenTCP(port, SMTPFactory(userDir,domains))
    reactor.run()
