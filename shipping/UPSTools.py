import AbstractShipping
import httplib
from xml.dom import minidom

__version__ = '1.0 March 30, 2004'
__changelog__ = """
1.0 - Created file
"""

__doc__ = """
Classes for sending requests to and parsing responses from UPS OnLine Tools.
"""



# "Constants"
DOMAIN = 'ups.com'
URL_RATE_CHECK = '/ups.app/xml/Rate'
UPS_SERVICES = {'01' : 'UPS Next Day Air',
                '02' : 'UPS 2nd Day Air',
                '03' : 'UPS Ground',
                '07' : 'UPS Worldwide Express',
                '08' : 'UPS Worldwide Expedited',
                '11' : 'UPS Standard',
                '12' : 'UPS 3 Day Select',
                '13' : 'UPS Next Day Air Saver',
                '14' : 'UPS Next Day Air Early A.M.',
                '54' : 'UPS Worldwide Express Plus',
                '59' : 'UPS 2nd Day Air A.M.',
                '65' : 'UPS Express Saver' }
UPS_COUNTRIES = {'Canada' : 'CA',
                 'United States' : 'US',
                 'Puerto Rico' : 'PR',
                 }


class UPSTools:
    """This is a base class used to access various UPS Online Tools.
    It builds the Access Request required to use UPS Tools and handles
    sending the request to the UPS server.
    
    To perform tasks with UPSTools, create a subclass that builds
    the requestxml property (a minidom.Document object) for the
    task.
    
    For specifics, see the UPS OnLine Tools Rates & Service Selection
    XML Tool Developer's Guide."""
    
    def __init__(self, login):
        """Initializes the object with the Access Key, User ID, and Password
        required to access UPS services.""" 
        
                # Build Access Request
        # i.e.,
        # <AccessRequest>
        #   <LicenseAccessKey>ACCESSKEY</LicenseAccessKey>
        #   <UserId>USER ID</UserId>
        #   <Password>PASSWORD</Password>
        # </AccessRequest>
        self.accessxml = minidom.Document()
        self.accessxml.documentElement = self.accessxml.createElement('AccessRequest')
        self.accessxml.documentElement.appendChild(self.accessxml.createElement('AccessLicenseNumber')).appendChild(self.accessxml.createTextNode(login.get('accesskey','')))
        self.accessxml.documentElement.appendChild(self.accessxml.createElement('UserId')).appendChild(self.accessxml.createTextNode(login.get('userid','')))
        self.accessxml.documentElement.appendChild(self.accessxml.createElement('Password')).appendChild(self.accessxml.createTextNode(login.get('password','')))
        self.requestxml = minidom.Document()
        self.responsexml = minidom.Document()
        
    def getResponse(self):
        """Processes the request by sending it to the UPS server. Stores
        a minidom.Document object containing the result of the query in
        the object's responsexml property."""
        req_xml = '%s%s%s%s' % (self.accessxml.toxml(), self.accessxml.documentElement.toxml(), self.requestxml.toxml(), self.requestxml.documentElement.toxml())
            
        # Connect to UPS server via SSL
        hcon = httplib.HTTPSConnection(DOMAIN)
        hcon.putrequest('POST', URL_RATE_CHECK)
        hcon.putheader("Content-Length", len(req_xml))
        hcon.putheader("Accept-Language", "en")
        hcon.putheader("Connection", "Keep-Alive")
        hcon.putheader("Content-type", "application/x-www-form-urlencoded")
        hcon.endheaders()
        hcon.send(req_xml)
        hres = hcon.getresponse()

        self.responsexml = minidom.parseString(hres.read())
        
        # Check for a failed result
        if self.responsexml.getElementsByTagName('ResponseStatusCode')[0].firstChild.nodeValue == '0':
            err_code = self.responsexml.getElementsByTagName('ErrorCode')[0].firstChild.nodeValue
            err_desc = self.responsexml.getElementsByTagName('ErrorDescription')[0].firstChild.nodeValue
            raise AbstractShipping.OnlineToolError, '%s (%s)' % (err_desc, err_code)


class UPSSimpleRate(UPSTools, AbstractShipping.SimpleRate):
    """Subclass of UPSTools that queries UPS for a list of shipping rates
    based on source, destination, and total weight of packages.
    
    The class will check the response for the most basic shipping option.
    For the US, this is UPS Ground (03); for Canada, this is UPS Standard
    (11); and for everywhere else, this is UPS Worldwide Expedited (08).
    This behavior can be changed with the SERVICES variable below.
        
    For specifics, see the UPS OnLine Tools Rates & Service Selection
    XML Tool Developer's Guide."""
    
    SERVICES = {'US' : ('03','02'),
                'CA' : '11',
                'PR' : '02',
                None : '08'}
    
    def __init__(self, login, **kwargs):
        """Initializes the UPSSimpleRateCheck object with the Access Key/User ID/Password
        combo as well as information on the source and destination of the package.
                
        A list of UPS country codes can be found in the appendix of the
        UPS OnLine Tools Developer's Guide."""

        # Initialize Access Request     
        UPSTools.__init__(self, login)

        # If we got the full country name, convert it to a country code
        kwargs['to_country'] = UPS_COUNTRIES.get(kwargs.get('to_country', None), kwargs.get('to_country', None))

        # Determine which service we're looking for, based on country code
        self.ship_method = UPSSimpleRate.SERVICES.get(kwargs.get('to_country', 'US'), UPSSimpleRate.SERVICES[None])
            
        # Build Request
        # <RatingServiceSelectionRequest>
        self.requestxml.documentElement = self.requestxml.createElement('RatingServiceSelectionRequest')

        ## DWA Set shippingtype to "one-time pickup"
        node1 = self.requestxml.documentElement.appendChild(self.requestxml.createElement('PickupType'))
        node2 = node1.appendChild(self.requestxml.createElement('Code'))
        node2.appendChild(self.requestxml.createTextNode('01'))

        ## DWA Set customer classification to "occasional"
        node1 = self.requestxml.documentElement.appendChild(self.requestxml.createElement('CustomerClassification'))
        node2 = node1.appendChild(self.requestxml.createElement('Code'))
        node2.appendChild(self.requestxml.createTextNode('03'))

        
        #   <Request>
        #       <TransactionReference>
        #           <CustomerContext>Rating and Service</CustomerContext>
        #           <XpciVersion>1.0001</XpciVersion>
        #       </TransactionReference>
        #       <RequestAction>Rate</RequestAction>
        #       <RequestOption>shop</RequestOption>
        #   </Request>
        node1 = self.requestxml.documentElement.appendChild(self.requestxml.createElement('Request'))
        node2 = node1.appendChild(self.requestxml.createElement('TransactionReference'))
        node2.appendChild(self.requestxml.createElement('CustomerContext')).appendChild(self.requestxml.createTextNode('Rating and Service'))
        node2.appendChild(self.requestxml.createElement('XpciVersion')).appendChild(self.requestxml.createTextNode('1.0001'))
        node1.appendChild(self.requestxml.createElement('RequestAction')).appendChild(self.requestxml.createTextNode('Rate'))
        node1.appendChild(self.requestxml.createElement('RequestOption')).appendChild(self.requestxml.createTextNode('shop'))

        #   <Shipment>
        #       <Shipper>
        #           <Address>
        #               <PostalCode>FROM_ZIP_CODE</PostalCode>
        #           </Address>
        #       </Shipper>
        node1 = self.requestxml.documentElement.appendChild(self.requestxml.createElement('Shipment'))
        node2 = node1.appendChild(self.requestxml.createElement('Shipper')).appendChild(self.requestxml.createElement('Address'))
        node2.appendChild(self.requestxml.createElement('PostalCode')).appendChild(self.requestxml.createTextNode(kwargs.get('from_zip_code','')))
        
        #       <ShipTo>
        #           <Address>
        #               <PostalCode>TO_ZIP_CODE</PostalCode>
        #               <CountryCode>TO_COUNTRY</CountryCode>
        #           </Address>
        #       </ShipTo>
        node2 = node1.appendChild(self.requestxml.createElement('ShipTo')).appendChild(self.requestxml.createElement('Address'))
        node2.appendChild(self.requestxml.createElement('PostalCode')).appendChild(self.requestxml.createTextNode(kwargs.get('to_zip_code','')))
        node2.appendChild(self.requestxml.createElement('CountryCode')).appendChild(self.requestxml.createTextNode(kwargs.get('to_country','US')))
        
        
        # Mark the node where new Packages are to be added
        self.packageNode = node1
        
        #   </Shipment>
        #</RatingServiceSelectionRequest>

        
    def addPackage(self, packages=[]):
        """Adds a package to the request. The request must contain at least
        one package; otherwise, UPS will classify the request as invalid
        and an error will be returned.
        
        packages may be a single value representing the weight of the new package,
        or it may be a tuple or list of weights.
        
        PackagingType is always 02 (Package)."""        
        #   {   <Package>
        #           <PackagingType>
        #               <Code>02</Code>
        #           </PackagingType>
        #           <PackageWeight>
        #               <Weight>PACKAGE_WEIGHT</Weight>
        #           </PackageWeight>
        #       </Package>
        #   }
        if isinstance(packages, tuple) or isinstance(packages, list):
            for p in packages:
                node1 = self.packageNode.appendChild(self.requestxml.createElement('Package'))
                node1.appendChild(self.requestxml.createElement('PackagingType')).appendChild(self.requestxml.createElement('Code')).appendChild(self.requestxml.createTextNode('02'))
                node1.appendChild(self.requestxml.createElement('PackageWeight')).appendChild(self.requestxml.createElement('Weight')).appendChild(self.requestxml.createTextNode(str(p)))
        else:
            node1 = self.packageNode.appendChild(self.requestxml.createElement('Package'))
            node1.appendChild(self.requestxml.createElement('PackagingType')).appendChild(self.requestxml.createElement('Code')).appendChild(self.requestxml.createTextNode('02'))
            node1.appendChild(self.requestxml.createElement('PackageWeight')).appendChild(self.requestxml.createElement('Weight')).appendChild(self.requestxml.createTextNode(str(packages)))

    def getResponse(self, returnAllResults=None):
        """Queries the UPS server for shipping information, and then returns
        the "best" shipping method (as specified in the SERVICES variable)
        as a dictionary containing:
            service_name    The UPS Service Name (i.e., 'UPS Ground')
            service_code    The UPS Service Code (i.e., '03')
            price           The cost of shipping."""
        
        UPSTools.getResponse(self)
        responseOptions = {}
        code = '';charges=''
        availableOptions = []
        for n in self.responsexml.getElementsByTagName('RatedShipment'):
            
            # Get Service Code & Total Charges
            code = n.getElementsByTagName('Service')[0].getElementsByTagName('Code')[0].firstChild.nodeValue
            availableOptions.append(code)
            charges = n.getElementsByTagName('TotalCharges')[0].getElementsByTagName('MonetaryValue')[0].firstChild.nodeValue
            if returnAllResults or ((type(self.ship_method) == str and code == self.ship_method) or (type(self.ship_method) == tuple and code in self.ship_method)):
                responseOptions[code] = {'service_name': UPS_SERVICES[code],
                                         'service_code': code,
                                         'price': charges,
                                        }
        if returnAllResults:
            return responseOptions
        elif type(self.ship_method) == str:
            return responseOptions[self.ship_method]
        elif type(self.ship_method) == tuple:
            for method in self.ship_method:
                if method in responseOptions.keys():
                    return responseOptions[method]

        raise AbstractShipping.NoResultsError, 'UPS Service(s) "%s" not found in Rate Check response (%s).' % (str(self.ship_method), str(availableOptions))
