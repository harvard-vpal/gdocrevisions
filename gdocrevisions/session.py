class Session(object):
	"""
	Session class
	"""
	def __init__(self, revisions):
		# list of revisions
		self.revisions = revisions
		# session id
		self.session_id = self.revisions[0]
		# time of first revision
		self.start_time = self.revisions[0].time
		# time of last revision
		self.end_time = self.revisions[-1].time if len(self.revisions)>1 else self.start_time
		# user
		self.user_id  = self.revisions[0].user_id


