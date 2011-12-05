import smtplib, email.mime.text, imaplib, email, time, sys, random, getpass, math


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

		return output


	def __del__(self):
		self.send_server.close()
		self.recv_server.close()



class useful(object):
	def __init__(self):
		self.file2Open = 'data.txt'

	def genRandID(self, fromInt, toInt = -1):
		if toInt == -1:
			toInt = fromInt
		tmp = ""
		for i in range(random.randint(fromInt,toInt)):
			tmp += str(random.randint(0,9))
		return int(tmp)

	def append2File(self, text):
		oldContent = ""
		try:
			fd = open(self.file2Open, 'r')
			oldContent = fd.read()
			fd.close()
		except IOError:
			pass
		fd = open(self.file2Open, 'w')
		if oldContent == "":
			fd.write(text)
		else:
			fd.write(oldContent + "\n\n" + text)
		fd.close()



class looper(object):
	def __init__(self):
		self.u = useful()
		self.m = mailer('kpjkpjkpjkpjkpjkpj@googlemail.com', getpass.getpass())

		self.runInterval = 3 # in seconds

		self.subject = 'WAM - Write and Mail'
		self.content = '\n'.join([
															'Hey,',
															'schoen, dass du mitspielst!',
															'Gib deinen Satz einfach ein.',
															'Pass dabei aber auf, dass du kein "-" nutzt',
															'und dieses Zeichen deinen Satz vom Rest der Mail trennt.',
															'',
															'Viel Spasz wuenscht kpj',
										])

		self.subscriber = ["pythoner@gmx.de"] # TO EDIT
		self.num2Send = int(math.ceil(float(len(self.subscriber))/3))
		self.gotThisMail = []
		self.gotLastMail = []

		self.ID = self.u.genRandID(5,10)
		self.currentSubject = '%s (%i)' % (self.subject, self.ID)

		self.story = ''


	def getRecipient(self):
		for x in range(self.num2Send):
			recipient = random.choice(self.subscriber)
			while recipient in self.gotLastMail and recipient in self.gotThisMail:
				if len(self.gotLastMail) == len(self.subscriber):
					print "Only one email-address ?!"
					break
				recipient = random.choice(self.subscriber)
			self.gotThisMail.append(recipient)
		self.gotLastMail = self.gotThisMail[:] # Really create new list
		self.gotThisMail = []
		return self.gotLastMail


	def getStory(self, mail):
		return mail.split('-')[0]

	
	def sendMails(self):
		for recipient in self.getRecipient():
			print "Sending mail to %s" % recipient
			self.m.sendMail(self.currentSubject, self.content, recipient)


	def start(self):
		self.sendMails()
		while True:
			mails = []
			while True:
				print "Receiving mails (%s)" % repr(self.currentSubject)
				mails = self.m.getMail(self.currentSubject)
				print "Received 1 mail" if len(mails) == 1 else "Received %i mails"%len(mails)
				if mails:
					break
				time.sleep(self.runInterval)

			self.ID += 1
			self.currentSubject = '%s (%i)' % (self.subject, self.ID)
			self.story += self.getStory(mails[0])

			self.sendMails()


	def __del__(self):
		print self.u.append2File(self.story)

looper().start()
