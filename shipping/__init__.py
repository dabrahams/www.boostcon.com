from AbstractShipping import *
from UPSTools import *
from FedExTools import *

__version__ = '1.0 March 30, 2004'
__changelog__ = """
1.0 - Created file
"""

__doc__ = """
Abstracts shipping tools for a variety of providers and tasks.

Current Providers:
	
	UPS
		Login information to UPS must be supplied as a dictionary with
		the following keys:
			accesskey		The client's UPS XML Access key
			userid			The client's UPS User ID
			password		The client's UPS Password
		
		Links:
		
		Rates & Service Selection XML Docs
			http://www.ups.com/gec/techdocs/pdf/dtk_RateXML_V1.zip
			
	FedEx
		Login information to FedEx must be supplied as a dictionary with
		the following keys:
			account_number	The client's FedEx account number, found on shipping labels
			meter_number	Number received from FedExSubscriptionRequest()
		
		Links:
		
		Ship Manager Documentation (This module uses Ship Manager Direct via XML)
			http://www.fedex.com/us/solutions/shipapi/docs.html?link=4
		Shipping Solutions FAQ
			http://www.fedex.com/us/solutions/shipapi/faq.html
			
	
	
Current Actions:
	
	SimpleRate
		The class will query the online tool for shipping rates, and then
		return the response for the most basic shipping option (as specified
		for each particular provider.)

		Some options do not translate directly between all providers.
	
		Initialize with:
			login				A login, in whatever format required
								for the provider.
			from_zip_code		The shipper's Zip Code
			from_state			FedEx requires the Shipper's state
			from_country		FedEx requires the Shipper's country (US default)
			to_zip_code			The customer's Zip Code
			to_country 			The customer's country (either full name
								or shipper Country Code)
	
		.addPackage(packages)
			Adds new package(s) to the list of packages to be sent as
			part of this shipment.
				packages		A single package weight, or a list/tuple
								of package weights. See individual provider's
								class for details.
		
		.getResponse()
			Returns a tuple containing the cost, Service Name, and
			Service Code of the most basic form of shipping that
			provider offers.
"""

def create(provider, action, login, **kwargs):
	
	import shipping
	
	if hasattr(shipping, provider + action):
		return apply(getattr(shipping, provider + action), (login,), kwargs)
	else:
		raise NameError, 'No class named %s%s' % (provider, action)
