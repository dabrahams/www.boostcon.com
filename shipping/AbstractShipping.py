__version__ = '1.0 March 30, 2004'
__changelog__ = """
1.0 - Created file
"""

class OnlineToolError(Exception):
	"""Exception raised when an online shipping tool returns a failed result."""

class NoResultsError(Exception):
	"""Exception raised when an online shipping tool query returns no results."""

class SimpleRate:
	"""
	"""
	
	def addPackage(self, packages=[]):
		"""
		Abstract method: define this to add package(s) to the shipment.
		"""
		raise NotImplementedError
	
	def getResponse(self):
		"""
		Abstract method: define this to query the service and get a response.
		"""
		raise NotImplementedError