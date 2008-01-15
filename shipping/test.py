from pprint import *
import sys
sys.path.append('..')
import shipping

def UPSShip(toZip="80501", fromZip="37932", toCountry="United States",packages=[6,2.3]):
	'''Examples:
	UPSShip('80501') # Some random place in Colorado
	UPSShip('00785','PR') # Some random place in Puerto Rico
	UPSShip('09096','United States',[7.5,10,2.3]) # Some random place in Hawaii (or... Alaska. I forget.)
	'''
	ship = shipping.create('UPS', 'SimpleRate',
							{
								'accesskey' : "BBFF633F986ECB79", # a 16-character string
								'userid'    : "david_abrahams",
								'password'  : "y0up33e55",
							},
							from_zip_code = fromZip,
							to_zip_code = toZip,
							to_country = toCountry,
							)
	ship.addPackage(packages) 
	shipInfo = None
	try:     
		shipInfo = ship.getResponse(returnAllResults = True) 
		print shipInfo
	except (shipping.NoResultsError, shipping.OnlineToolError), error_text:
		print ship.responsexml.toprettyxml()
		print error_text
		print
	return shipInfo

def FedExShip(toState="CO",toZip="80501",fromState="TN", fromZip="37932",
              toCountry="United States",packages=[6.0001,2.3],weight=10.0):
	ship = shipping.create('FedEx', 'AvailableRates',
							{
								'account_number'	:'361927826',# a 9 digit number
								'meter_number'		:'7340835',
							},
							from_state = fromState,
							from_zip_code = fromZip,
							to_state = toState,
							to_zip_code = toZip,
							to_country = toCountry,

							# The following args have defaults but they're left here for example
							# on how to change them, should the need arise.
							
							# service = 'GROUNDHOMEDELIVERY', 
							# service='FEDEXGROUND',
							# packaging = 'FEDEXBOX',
							# weight_units = 'LBS',
                           weight = weight
							)
	# addPackage can accept lists of weights for multiple packages or single floats
	ship.addPackage(packages) 
	shipInfo = None
	try:     
		print ship
		print
		print dir(ship)
		print
		shipInfo = ship.getResponse(returnAllResults = True) 
		print shipInfo
	except (shipping.NoResultsError, shipping.OnlineToolError), error_text:
		print ship.responsexml.toprettyxml()
		print error_text
		print
	return ship


def FedExSubscription(	account='', 
						person='', 
						company='', 
						phone='', 
						address1='', 
						address2='', 
						city='', 
						state='', 
						zipcode='', 
						country='',):
	'''
		In order to connect to FedEx you must send a request to its test server
		to receive a Meter number (required login piece for FedEx).
		Once you are done testing and FedEx has approved you (see dox), you run
		this request again to receive a new Meter number on their 
		production server.
	'''
	req = shipping.FedExSubscriptionRequest(
						account=account, 
						person=person,
						company=company,
						phone=phone,
						address1=address1,
						address2=address2,
						city=city,
						state=state,
						zipcode=zipcode,
						country=country,
						)
	req.BuildXml()
	req.getResponse()
	return (req.responsexml, req.response)


unsubscribed = False
if unsubscribed:
    pprint(FedExSubscription(
						account='361927826', 
						person='David Abrahams',
						company='Boost Consulting, Inc.',
						phone='6174184100',
						address1='45 Walnut St',
#						address2='attn:shipping',
						city='Somerville',
						state='MA',
						zipcode='02143',
						country='US',
						))

response = FedExShip(toZip='99517',
                     toState='AK',fromZip='02143',fromState='MA',packages=[0.3125],
                     weight=0.3125)
print 40*'='
print response.toprettyxml()

# pprint(UPSShip(toZip='99517',fromZip='02143',packages=[0.3125]))

    
