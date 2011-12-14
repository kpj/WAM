###############################################
#                                             #
#  Send SIGUSR1 to update the subscribe-list  #
#  example: killall -USR1 python           #
#                                             #
###############################################

import smtplib, imaplib, getpass, logging, signal
import email, email.mime.text, email.Iterators,  email.header
import time, sys, random, math, re

# Enable logging
level = logging.INFO
log = logging.getLogger(sys.argv[0])
log.setLevel(level)

ch = logging.StreamHandler()
ch.setLevel(level)

formatter = logging.Formatter("%(asctime)s - %(message)s")
ch.setFormatter(formatter)

log.addHandler(ch)

class signalHandler(object):
	def __init__(self, sig, func):
		self.func = func
		signal.signal(sig, self.handler)


	def handler(self, signum, frame):
		log.info("Executed function...")
		self.func()
			


class getData(object):
	def __init__(self):
		self.fileWithMails = 'mails.txt'

		self.fd = open(self.fileWithMails, 'a+')


	def genMailList(self):
		lines = self.fd.read()
		mailList = lines.split('\n')
		for i in range(len(mailList)):
			try:
				mailList.remove('')
			except ValueError:
				pass
		return mailList



class mailer(object):
	def __init__(self, address, passwd):
		self.__address = address
		self.__passwd = passwd

		self.send_server = smtplib.SMTP('smtp.gmail.com', 587)
		self.send_server.ehlo()
		self.send_server.starttls()
		self.send_server.ehlo()
		self.send_server.login(self.__address, self.__passwd)

		self.recv_server = imaplib.IMAP4_SSL("imap.googlemail.com")
		self.recv_server.login(self.__address, self.__passwd)
		self.recv_server.select()


	def sendMail(self, subject, content, target):
		msg = email.mime.text.MIMEText(content, 'plain', 'utf-8')
		msg['Subject'] = subject
		msg['From'] = self.__address
		msg['To'] = target

		self.send_server.sendmail(self.__address, target, msg.as_string())

		
	def getMail(self, subject, delete = True):
		self.recv_server.select()
		typ, data = self.recv_server.search(None, 'SUBJECT', '"%s"' % (subject))

		output = []
		for num in data[0].split():
			# m.get_body(email.message_from_string(m.g(1)[0][1]))
			typ, data = self.recv_server.fetch(num, '(RFC822)')
			mail = email.message_from_string(data[0][1])
			content = self.get_body(mail)
			output.append(content)

			if delete:
				self.recv_server.store(num, '+FLAGS', r'(\Deleted)')

		return output


	def getHeader(self, num):
		h = self.recv_server.fetch(num, '(BODY[HEADER])')
		header_text = h[1][0][1]
		parser = email.parser.HeaderParser()
		head = parser.parsestr(header)
		return head


	def get_charset(self, message, default="ascii"):
		if message.get_content_charset():
			return message.get_content_charset()
		if message.get_charset():
			return message.get_charset()
		return default

	
	def get_body(self, message):
		if message.is_multipart():
			text_parts = [part for part in email.Iterators.typed_subpart_iterator(message, 'text', 'plain')]

			body = []
			for part in text_parts:
				charset = self.get_charset(part, self.get_charset(message))
				body.append(unicode(part.get_payload(decode=True), charset, "replace"))

			return u"\n".join(body).strip()
		else:
			body = unicode(message.get_payload(decode=True), self.get_charset(message), "replace")
			return body.strip()


	def __del__(self):
		self.send_server.close()
		self.recv_server.close()



class useful(object):
	def __init__(self):
		pass

	def genRandID(self, fromInt, toInt = -1):
		if toInt == -1:
			toInt = fromInt
		tmp = ""
		for i in range(random.randint(fromInt,toInt)):
			tmp += str(random.randint(0,9))
		return int(tmp)



class story(object):
	def __init__(self, identity):
		self.openFile = 'story.txt'
		self.story = []
		
		self.fd = open(self.openFile, 'a+')
		self.story = [line.replace('\n','').decode('utf-8') for line in self.fd.readlines()]
		
		self.identity = identity


	def setID(self, ID):
		self.identity = ID


	def append(self, text):
		text = text.replace('\n', '')
		self.story.append(text)
		text = text.encode('utf-8')
		print >> self.fd, text
		self.fd.flush()


	def printStory(self):
		print '\n'.join(self.story)


	def lastPhrase(self):
		try:
			return self.story[-1]
		except IndexError:
			return 'Kein letzter Satz.'


	def __del__(self):
		self.printStory()
		self.fd.close()



class looper(object):
	def __init__(self):
		self.ownMail = 'kpjkpjkpjkpjkpjkpj@googlemail.com'

		self.u = useful()
		self.m = mailer('kpjkpjkpjkpjkpjkpj+WAM@googlemail.com', getpass.getpass())
		self.g = getData()

		self.runInterval = 2 # in seconds

		self.subject = 'WAM - Write and Mail'
		self.content = '\n'.join([
				'Hey,',
				'schoen, dass du mitspielst!',
				'Antworte einfach und schreibe entweder ueber,',
				'oder unter diesem Abschnitt.',
				'(Am Besten mit ein paar Leerzeilen ;))',
				'Der vorhergehende Satz war:',
				'',
				'%s',
				'',
				'Viel Spasz wuenscht kpj',
		])

		self.genSubscribers()
		self.s = signalHandler(signal.SIGUSR1, self.genSubscribers)

		self.gotThisMail = []
		self.gotLastMail = []

		self.story = story(self.u.genRandID(5,10))
		self.currentSubject = '%s (%i)' % (self.subject, self.story.identity)


	def genSubscribers(self):
		self.subscriber = self.g.genMailList()
		self.num2Send = int(math.ceil(float(len(self.subscriber))/3))


	def getRecipient(self):
		for x in range(self.num2Send):
			recipient = random.choice(self.subscriber)
			while recipient in self.gotLastMail or recipient in self.gotThisMail:
				if len(self.gotLastMail) == len(self.subscriber):
					log.debug("Only one email-address ?!")
					break
				recipient = random.choice(self.subscriber)
			self.gotThisMail.append(recipient)
		self.gotLastMail = self.gotThisMail[:] # Really create new list
		self.gotThisMail = []
		return self.gotLastMail


	def getStory(self, mail):
		m = mail.split('\n')
		comment_pattern = '>'

    # Just always delete my own address:
		for i in range(len(m)):
			if self.ownMail in m[i]:
				m.remove(m[i])
				break

		pos = -1
		hadComment = False
		for p in m:
			pos += 1
			if comment_pattern in p:
				hadComment = True
				break
		if hadComment:
			m.pop(pos-1)

		toDel = []
		for i in range(len(m)):
			if comment_pattern in m[i]:
				toDel.append(m[i])
		for i in toDel:
			m.remove(i)

		for i in range(len(m)):
			try:
				m.remove('')
			except ValueError:
				pass

		m.remove('\r')

		mail = '\n'.join(m)

		return mail

	
	def sendMails(self):
		for recipient in self.getRecipient():
			log.info("Sending mail to %s" % recipient)
			self.m.sendMail(self.currentSubject,
					self.content % ( 
							self.story.lastPhrase()),
							recipient)


	def start(self):
		self.sendMails()
		while True:
			mails = []
			while True:
				log.debug("Receiving mails (%s)" % repr(self.currentSubject))
				mails = self.m.getMail(self.currentSubject)
				if mails:
					log.info("Received 1 mail" if len(mails) == 1 else "Received %i mails"%len(mails))
					break
				else:
					log.debug("Received 0 mails")
				time.sleep(self.runInterval)

			self.story.setID(self.u.genRandID(5,10))
			self.currentSubject = '%s (%i)' % (self.subject, self.story.identity)

			content = ''.join(self.getStory(mails[0]))
			self.story.append(content)

			self.sendMails()


	def __del__(self):
		pass

looper().start()
#getData().genMailList()
#m=mailer('kpjkpjkpjkpjkpjkpj+WAM@googlemail.com', getpass.getpass())
#l = looper()
# vim: autoindent:
