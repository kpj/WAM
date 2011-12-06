import smtplib, email.mime.text, imaplib, email, time, sys, random, getpass, math, logging

# Enable logging
level = logging.DEBUG
log = logging.getLogger(sys.argv[0])
log.setLevel(level)

ch = logging.StreamHandler()
ch.setLevel(level)

formatter = logging.Formatter("%(asctime)s - %(message)s")
ch.setFormatter(formatter)

log.addHandler(ch)

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


	def sendMail(self, subject, content, target):
		msg = email.mime.text.MIMEText(content)
		msg['Subject'] = subject
		msg['From'] = self.__address
		msg['To'] = target

		self.send_server.sendmail(self.__address, target, msg.as_string())

		
	def getMail(self, subject):
		self.recv_server.select()
		typ, data = self.recv_server.search(None, 'SUBJECT', '"%s"' % (subject))

		output = []
		for num in data[0].split():
			typ, data = self.recv_server.fetch(num, '(BODY.PEEK[TEXT])')
			for response_part in data:
				if isinstance(response_part, tuple):
					output.append(response_part[1])
			self.recv_server.store(num, '+FLAGS', r'(\Deleted)')

		return output


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
		self.story = [line.replace('\n','') for line in self.fd.readlines()]
		
		self.identity = identity


	def setID(self, ID):
		self.identity = ID


	def append(self, text):
		text = text.replace('\n', '')
		print >> self.fd, text
		self.story.append(text)
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
		self.u = useful()
		self.m = mailer('kpjkpjkpjkpjkpjkpj@googlemail.com', getpass.getpass())

		self.runInterval = 60 # in seconds
		self.seperator = ',.-/^\-.,'

		self.subject = 'WAM - Write and Mail'
		self.content = '\n'.join([
				'Hey,',
				'schoen, dass du mitspielst!',
				'Gib deinen Satz einfach zwischen den Zeichen ein:',
				'%s',
				'<-- Hier koennte Ihr Satz stehen. -->',
				'%s',
				'Der vorhergehende Satz war:',
				'',
				'%s',
				'Pass dabei aber auf, dass du kein "-" nutzt',
				'und dieses Zeichen deinen Satz vom Rest der Mail trennt.',
				'',
				'Viel Spasz wuenscht kpj',
		])

		self.subscriber = ["qaywsxedc291@web.de",
				"mr.flubbie@gmx.de",
				"abi1789@googlemail.com"]
		self.num2Send = int(math.ceil(float(len(self.subscriber))/3))
		self.gotThisMail = []
		self.gotLastMail = []

		self.story = story(self.u.genRandID(5,10))
		self.currentSubject = '%s (%i)' % (self.subject, self.story.identity)


	def getRecipient(self):
		for x in range(self.num2Send):
			print self.gotLastMail
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
		return mail.split(self.seperator)[1]

	
	def sendMails(self):
		for recipient in self.getRecipient():
			log.info("Sending mail to %s" % recipient)
			self.m.sendMail(self.currentSubject,
					self.content % (self.seperator, self.seperator, self.story.lastPhrase()),
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

			content = self.getStory(mails[0])
			self.story.append(content)

			self.sendMails()


	def __del__(self):
		pass

#looper().start()
l=looper()
# vim: autoindent:
