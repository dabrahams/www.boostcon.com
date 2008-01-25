import AbstractShipping
import httplib
from dom import tag as _, xml_document
from xml.dom import minidom

__version__ = '1.0 February 7, 2005'
__changelog__ = """
1.0 - File released
"""

__doc__ = """
Classes for sending requests to and parsing responses from FedEx OnLine Tools.
"""

# "Constants"
APIURL = 'http://www.fedex.com/fsmapi'
XSIURL = 'http://www.w3.org/2001/XMLSchema-instance'
RATE_NNSLOC = 'FDXRateRequest.xsd' # NNSLOC is "xsi:noNamespaceSchemaLocation"
SUBSCRIBE_NNSLOC = 'FDXSubscriptionRequest.xsd' # NNSLOC is "xsi:noNamespaceSchemaLocation"
#DOMAIN = 'gatewaybeta.fedex.com' # Before the customer is approved for production by FedEx, we use gatewaybeta.
DOMAIN = 'gateway.fedex.com'
URL_RATE_CHECK = '/GatewayDC'

SERVICES = {
    'PRIORITYOVERNIGHT'                 :   'FedEx Priority Overnight',
    'STANDARDOVERNIGHT'                 :   'FedEx Standard Overnight',
    'FIRSTOVERNIGHT'                    :   'FedEx First Overnight',
    'FEDEX2DAY'                         :   'FedEx 2 Day',
    'FEDEXEXPRESSSAVER'                 :   'FedEx Express Saver',
    'INTERNATIONALPRIORITY'             :   'FedEx International Priority', 
    'INTERNATIONALECONOMY'              :   'FedEx International Economy',
    'INTERNATIONALFIRST'                :   'FedEx International First',
    'FEDEX1DAYFREIGHT'                  :   'FedEx 1 Day Freight',
    'FEDEX2DAYFREIGHT'                  :   'FedEx 2 Day Freight',
    'FEDEX3DAYFREIGHT'                  :   'FedEx 3 Day Freight',
    'FEDEXGROUND'                       :   'FedEx Ground',
    'GROUNDHOMEDELIVERY'                :   'FedEx Ground Home Delivery',
    'INTERNATIONALPRIORITYFREIGHT'      :   'FedEx International Priority Freight',
    'INTERNATIONALECONOMYFREIGHT'       :   'FedEx International Economy Freight',
    'EUROPEFIRSTINTERNATIONALPRIORITY'  :   'FedEx Europe First International Priority',
}

COUNTRIES = {
    'Albania': 'AL',
    'Algeria': 'DZ',
    'American Samoa': 'AS',
    'Andorra': 'AD',
    'Angola': 'AO',
    'Anguilla': 'AI',
    'Antigua': 'AG',
    'Argentina': 'AR',
    'Armenia': 'AM',
    'Aruba': 'AW',
    'Australia': 'AU',
    'Austria': 'AT',
    'Azerbaijan': 'AZ',
    'Bahamas': 'BS',
    'Bahrain': 'BH',
    'Bangladesh': 'BD',
    'Barbados': 'BB',
    'Belarus': 'BY',
    'Belgium': 'BE',
    'Belize': 'BZ',
    'Benin': 'BJ',
    'Bermuda': 'BM',
    'Bhutan': 'BT',
    'Bolivia': 'BO',
    'Botswana': 'BW',
    'Brazil': 'BR',
    'British Virgin Is.': 'VG',
    'Brunei': 'BN',
    'Bulgaria': 'BG',
    'Burkino Faso': 'BF',
    'Burma': 'MM',
    'Burundi': 'BI',
    'Cambodia': 'KH',
    'Cameroon': 'CM',
    'Canada': 'CA',
    'Cape Verde': 'CV',
    'Cayman Islands': 'KY',
    'Central African': 'CF',
    'Chad': 'TD',
    'Chile': 'CL',
    'China': 'CN',
    'Colombia': 'CO',
    'Congo': 'CG',
    'Congo, The Republic of': 'CD',
    'Cook Islands': 'CK',
    'Costa Rica': 'CR',
    'Cote D\'Ivoire': 'CI',
    'Croatia': 'HR',
    'Cyprus': 'CY',
    'Czech Republic': 'CZ',
    'Denmark': 'DK',
    'Djibouti': 'DJ',
    'Dominica': 'DM',
    'Dominican Republic': 'DO',
    'Ecuador': 'EC',
    'Egypt': 'EG',
    'El Salvador': 'SV',
    'Equatorial Guinea': 'GQ',
    'Eritrea': 'ER',
    'Estonia': 'EE',
    'Ethiopia': 'ET',
    'Faeroe Islands': 'FO',
    'Fiji': 'FJ',
    'Finland': 'FI',
    'France': 'FR',
    'French Guiana': 'GF',
    'French Polynesia': 'PF',
    'Gabon': 'GA',
    'Gambia': 'GM',
    'Georgia, Republic of': 'GE',
    'Germany': 'DE',
    'Ghana': 'GH',
    'Gibraltar': 'GI',
    'Greece': 'GR',
    'Greenland': 'GL',
    'Grenada': 'GD',
    'Guadeloupe': 'GP',
    'Guam': 'GU',
    'Guatemala': 'GT',
    'Guinea': 'GN',
    'Guinea-Bissau': 'GW',
    'Guyana': 'GY',
    'Haiti': 'HT',
    'Honduras': 'HN',
    'Hong Kong': 'HK',
    'Hungary': 'HU',
    'Iceland': 'IS',
    'India': 'IN',
    'Indonesia': 'ID',
    'Ireland': 'IE',
    'Israel': 'IL',
    'Italy': 'IT',
    'Ivory Coast': 'CI',
    'Jamaica': 'JM',
    'Japan': 'JP',
    'Jordan': 'JO',
    'Kazakhstan': 'KZ',
    'Kenya': 'KE',
    'Kuwait': 'KW',
    'Kyrgyzstan': 'KG',
    'Latvia': 'LV',
    'Lebanon': 'LB',
    'Lesotho': 'LS',
    'Liechtenstein': 'LI',
    'Lithuania': 'LT',
    'Luxembourg': 'LU',
    'Macau': 'MO',
    'Macedonia': 'MK',
    'Madagascar': 'MG',
    'Malawi': 'MW',
    'Malaysia': 'MY',
    'Maldives': 'MV',
    'Mali': 'ML',
    'Malta': 'MT',
    'Marshall Islands': 'MH',
    'Martinique': 'MQ',
    'Mauritania': 'MR',
    'Mauritius': 'MU',
    'Mexico': 'MX',
    'Micronesia': 'FM',
    'Moldova': 'MD',
    'Monaco': 'MC',
    'Mongolia': 'MN',
    'Montserrat': 'MS',
    'Morocco': 'MA',
    'Mozambique': 'MZ',
    'Myanmar': 'MM',
    'Namibia': 'NA',
    'Nepal': 'NP',
    'Netherlands Antilles': 'AN',
    'Netherlands': 'NL',
    'New Caledonia': 'NC',
    'New Zealand': 'NZ',
    'Nicaragua': 'NI',
    'Niger': 'NE',
    'Nigeria': 'NG',
    'Norway': 'NO',
    'Oman': 'OM',
    'Pakistan': 'PK',
    'Palau': 'PW',
    'Panama': 'PA',
    'Papua New Guinea': 'PG',
    'Paraguay': 'PY',
    'Peru': 'PE',
    'Philippines': 'PH',
    'Poland': 'PL',
    'Portugal': 'PT',
    'Puerto Rico': 'US',
    'Qatar': 'QA',
    'Reunion Island': 'RE',
    'Romania': 'RO',
    'Russia': 'RU',
    'Rwanda': 'RW',
    'Saipan': 'MP',
    'San Marino': 'SM',
    'Saudi Arabia': 'SA',
    'Senegal': 'SN',
    'Seychelles': 'SC',
    'Sierra Leone': 'SL',
    'Singapore': 'SG',
    'Slovak Republic': 'SK',
    'Slovenia': 'SI',
    'South Africa': 'ZA',
    'South Korea': 'KR',
    'Spain': 'ES',
    'Sri Lanka': 'LK',
    'St. Kitts & Nevis': 'KN',
    'St. Lucia': 'LC',
    'St. Vincent': 'VC',
    'Suriname': 'SR',
    'Swaziland': 'SZ',
    'Sweden': 'SE',
    'Switzerland': 'CH',
    'Syria': 'SY',
    'Taiwan': 'TW',
    'Tanzania': 'TZ',
    'Thailand': 'TH',
    'Togo': 'TG',
    'Trinidad & Tobago': 'TT',
    'Tunisia': 'TN',
    'Turkey': 'TR',
    'Turkmenistan, Republic of': 'TM',
    'Turks & Caicos Is.': 'TC',
    'U.A.E.': 'AE',
    'U.S. Virgin Islands': 'VI',
    'U.S.A.': 'US',
    'Uganda': 'UG',
    'Ukraine': 'UA',
    'United Kingdom': 'GB',
    'Uruguay': 'UY',
    'Uzbekistan': 'UZ',
    'Vanuatu': 'VU',
    'Vatican City': 'VA',
    'Venezuela': 'VE',
    'Vietnam': 'VN',
    'Wallis & Futuna Islands': 'WF',
    'Yemen': 'YE',
    'Zambia': 'ZM',
    'Zimbabwe': 'ZW',
}

STATES = [
    'AL',
    'AK',
    'AZ',
    'AR',
    'CA',
    'CO',
    'CT',
    'DE',
    'FL',
    'GA',
    'HI',
    'ID',
    'IL',
    'IN',
    'IA',
    'KS',
    'KY',
    'LA',
    'ME',
    'MD',
    'MA',
    'MI',
    'MN',
    'MS',
    'MO',
    'MT',
    'NE',
    'NV',
    'NH',
    'NJ',
    'NM',
    'NY',
    'NC',
    'ND',
    'OH',
    'OK',
    'OR',
    'PA',
    'RI',
    'SC',
    'SD',
    'TN',
    'TX',
    'UT',
    'VT',
    'VA',
    'WA',
    'WV',
    'WI',
    'WY',
]

PACKAGING = {
    'FEDEXENVELOPE'                     :   'FEDEXENVELOPE' ,
    'FEDEXPAK'                          :   'FEDEXPAK'      ,
    'FEDEXBOX'                          :   'FEDEXBOX'      ,
    'FEDEXTUBE'                         :   'FEDEXTUBE'     ,
    'FEDEX10KGBOX'                      :   'FEDEX10KGBOX'  ,
    'FEDEX25KGBOX'                      :   'FEDEX25KGBOX'  ,
    'YOURPACKAGING'                     :   'YOURPACKAGING' ,
    'DEFAULT'                           :   'YOURPACKAGING' ,
}                     


class FedExTools:
    """This is a base class used to access various FedEx Online Tools.
    It builds the Request Header required to use FedEx Tools and handles
    sending the request to the FedEx server.
    
    To perform tasks with FedExTools, create a subclass that builds
    the requestxml property (a minidom.Document object) for the
    task.
    
    For specifics, see the FedEx OnLine Guides."""
    
    def __init__(self, login, carrier='FDXE'):
        """Initializes the object with the Transaction ID, AccountNumber, and MeterNumber
        required to access FedEx services."""

        self.DEBUG = 0

        # Build Access Request
        # i.e.,
        # <RequestHeader>
        #   <AccountNumber>ACCOUNTNUMBER</AccountNumber>
        #   <MeterNumber>METERNUMBER</MeterNumber>
        #   <CarrierCode>CODE</CarrierCode>
        #   <Service>SHIPPRIORITYSERVICE</Service>
        #   <Packaging>PACKTYPE</Packaging>
        # </RequestHeader>
        self.request_header = _.RequestHeader[
                _.AccountNumber[ login.get('account_number','') ]
              , _.MeterNumber[ login.get('meter_number','') ]
              , _.CarrierCode[ carrier ]  # Using FedEx Express.  FedEx ground
                                         # would be FDXG
            ]
        
        self.responsexml = minidom.Document()
        

    def getResponse(self):
        """Processes the request by sending it to the FedEx server. Stores
        a minidom.Document object containing the result of the query in
        the object's responsexml property."""
        req_xml = self.requestxml.toxml()
            
        # Connect to FedEx server via SSL
        hcon = httplib.HTTPSConnection(DOMAIN)
        hcon.putrequest('POST', URL_RATE_CHECK)
        hcon.putheader("Content-Length", len(req_xml))
        hcon.endheaders()
        hcon.send(req_xml)
        hres = hcon.getresponse()
        
        self.response = hres.read()
        self.responsexml = minidom.parseString(self.response)

        if self.DEBUG:
            print "-------------------------------------------------------------------"
            print "FedEx Response!"
            print "-------------------------------------------------------------------"
            print self.responsexml.documentElement.toprettyxml()
            print "-------------------------------------------------------------------"
        
        self.checkForError()

    def checkForError(self,):
        # Check for a failed result
        if self.responsexml.getElementsByTagName('Error'):
            err_code = self.responsexml.getElementsByTagName('Error')[0]\
                        .getElementsByTagName('Code')[0].firstChild.nodeValue
            err_desc = self.responsexml.getElementsByTagName('Error')[0]\
                        .getElementsByTagName('Message')[0].firstChild.nodeValue
            raise AbstractShipping.OnlineToolError, '%s (%s)' % (err_desc, err_code)


class FedExSubscriptionRequest(FedExTools):
    """In order to get rate requests from FedEx you must send a 'subscription request'.
        It need only be done twice (once to be allowed onto the test server, once
        to be allowed on the production server). Basically, you send them your existing
        Account Number and matching address information and they reply with a Meter Number
        that is required from then on in all your FedExTools requests.
            account, person, company, phone, address1, address2, city, state, zipcode, country
        """
    def __init__ (self, **kwargs):
        for key,value in kwargs.items():
            setattr(self,key,value and str(value) or '')
        self.Validate()
        self.DEBUG = 0
    
    def Validate (self,):
        if not self.account:
            raise "Account Number is required. E.g. 123456789"
        elif not self.person and not self.company:
            raise "Either the Person Name or the Company Name must be present"
        elif not self.phone:
            raise "Phone is required. E.g. 5405559900"
        elif not self.address1:
            raise "Address1 is required"
        elif not self.city:
            raise "City is required"
        elif not self.state:
            raise "State/Province is required"
        elif not self.zipcode:
            raise "Postal Code is required"
        elif not self.country:
            raise "Country is required"

    def BuildXml(self,):
        ''' Builds the XML object to be sent to Fedex. Stored in self.requestxml'''
        self.requestxml = minidom.Document()
        self.requestxml.appendChild(self.requestxml.createElement('FDXSubscriptionRequest'))
        self.requestxml.documentElement.setAttribute("xmlns:api",APIURL)
        self.requestxml.documentElement.setAttribute("xmlns:xsi",XSIURL)
        self.requestxml.documentElement.setAttribute("xsi:noNamespaceSchemaLocation",SUBSCRIBE_NNSLOC)

        element = minidom.Document()
        element.appendChild(element.createElement('RequestHeader'))
        element.documentElement.appendChild(
            element.createElement('AccountNumber')).appendChild(
            element.createTextNode(self.account))

        self.requestxml.documentElement.appendChild(element.documentElement)
        
        element.appendChild(element.createElement('Contact'))
        if self.person:
            element.documentElement.appendChild(
                element.createElement('PersonName')).appendChild(
                element.createTextNode(self.person))
        else:
            element.documentElement.appendChild(
                element.createElement('CompanyName')).appendChild(
                element.createTextNode(self.company))

        element.documentElement.appendChild(
            element.createElement('PhoneNumber')).appendChild(
            element.createTextNode(self.phone))
        
        self.requestxml.documentElement.appendChild(element.documentElement)

        element.appendChild(element.createElement('Address'))
        element.documentElement.appendChild(
            element.createElement('Line1')).appendChild(
            element.createTextNode(self.address1))
        
        if self.address2:
            element.documentElement.appendChild(
                element.createElement('Line2')).appendChild(
                element.createTextNode(self.address2))
            
        element.documentElement.appendChild(
            element.createElement('City')).appendChild(
            element.createTextNode(self.city))
        element.documentElement.appendChild(
            element.createElement('StateOrProvinceCode')).appendChild(
            element.createTextNode(self.state))
        element.documentElement.appendChild(
            element.createElement('PostalCode')).appendChild(
            element.createTextNode(self.zipcode))
        element.documentElement.appendChild(
            element.createElement('CountryCode')).appendChild(
            element.createTextNode(self.country))
        
        self.requestxml.documentElement.appendChild(element.documentElement)

        if self.DEBUG:
            print self.requestxml.toprettyxml()
            print self.requestxml.documentElement.toprettyxml()



class FedExSimpleRate(FedExTools, AbstractShipping.SimpleRate):
    """Subclass of FedExTools that queries FedEx for a list of shipping rates
    based on source, destination, and total weight of packages.
    
    For specifics, see the FedEx OnLine Tools Rates & Service Selection
    XML Tool Developer's Guide."""
    
    def __init__(self, login, **kwargs):
        """Initializes the FedExSimpleRateCheck object with the
        Transaction ID/AccountNumber/MeterNumber combo as well 
        as information on the source and destination of the package.
                
        A list of FedEx country codes can be found in the appendix of the
        FedEx Ship Manager API XML Transaction Guide."""

        # Initialize Access Request     
        FedExTools.__init__(self, login)

        # Total price for shipments
        self.total_cost = 0
        self.service = kwargs.get('service','FEDEXGROUND')
        
        # Package Information, such as weight and packingtype, e.g. [(1.4,"FEDEXBOX"),...]
        self.package_info = []

        # If we got the full country name, convert it to a country code
        kwargs['to_country'] = COUNTRIES.get(kwargs.get('to_country', None),
                                             kwargs.get('to_country', None))

        # Build Request
        # <FDXRateRequest xmlns:...>
        request = _.FDXRateRequest( **{
                'xmlns:api':APIURL
              , 'xmlns:xsi':XSIURL
              ,'xsi:noNamespaceSchemaLocation':RATE_NNSLOC
            })[
                  self.request_header
                , _.Service[ self.service ]
                  # FedEx Ground Home Delivery Packaging must be YOURPACKAGING only.
                , _.Packaging[ kwargs.get('packaging','YOURPACKAGING') ]
                , _.WeightUnits[ kwargs.get('weight_units','LBS') ]
                  # Value will be overridden in getResponse()
                , _.Weight[ '' ]
                , _.OriginAddress[
                      _.StateOrProvinceCode[ kwargs.get('from_state','') ]
                    , _.PostalCode[ kwargs.get('from_zip_code','') ]
                    , _.CountryCode[ kwargs.get('from_country','US') ]
                 ]
                , _.DestinationAddress[
                      _.StateOrProvinceCode[ kwargs.get('to_state','') ]
                    , _.PostalCode[ kwargs.get('to_zip_code','') ]
                    , _.CountryCode[ kwargs.get('to_country','US') ]
                 ]
               , _.Payment
               , _.PackageCount[ 1 ]
             ]

        self.requestxml = xml_document(request)

        
    def addPackage(self, packages=[]):
        """Adds a package to the request. The request must contain at least
        one package
        
        Packages may be a single value representing the weight of the new package,
        a tuple/list of weights, or a tuple/list of (weight,packaging) tuples/lists.
        e.g. 
            packages=2.3
            
            packages=(2.3,6.0,7.5)
            
            packages=((2.3,'FEDEXBOX'),(6.0,'FEDEXTUBE'),7.5)
        Note: FedEx requires a weight-value of one decimal point, e.g. 7.0, 7.5, etc.
        Values sent to this function will be converted to that format automatically.
        """     
        if isinstance(packages, tuple) or isinstance(packages, list):
            for p in packages:
                if isinstance(p,(tuple,list)) and len(p) == 2:
                    weight = "%.1f" % p[0]
                    packaging = PACKAGING[p[1]]
                else:
                    weight = "%.1f" % p
                    packaging = PACKAGING['DEFAULT']
                self.package_info.append((weight,packaging),)
        else:
            weight = "%.1f" % packages
            packaging = PACKAGING['DEFAULT']
            self.package_info.append((weight,packaging),)

    def getResponse(self, returnAllResults=None):
        """Queries the FedEx server for shipping information, and then returns
        the "best" shipping method (as specified in the SERVICES variable)
        as a dictionary containing:
            service_name    The FedEx Service Name (i.e., 'FedEx Ground')
            service_code    The FedEx Service Code (i.e., '03')
            price           The cost of shipping."""
        
        # Package dictionary finds package count grouped by weight/type. i.e.
        #   self.package_info = [(1,'FEDEXBOX'), (1,'FEDEXBOX'), (1.5,'FEDEXBOX')]
        # becomes
        #   package_dict = {(1,'FEDEXBOX'):2, (1.5,'FEDEXBOX'):1}
        package_dict = {}
        for pkg in self.package_info:
            if package_dict.get(pkg):
                package_dict[pkg] += 1
            else:
                package_dict[pkg] = 1
        
        self.total_cost = 0
        if self.DEBUG: print "-------------------------------------------------"
        for ((weight,packaging),count,) in package_dict.items():
            # FYI: FedEx rounds floats to decimal values.
            self.requestxml.documentElement.getElementsByTagName('Weight')[0].firstChild.nodeValue = weight
            self.requestxml.documentElement.getElementsByTagName('Packaging')[0].firstChild.nodeValue = packaging
            self.requestxml.documentElement.getElementsByTagName('PackageCount')[0].firstChild.nodeValue = count
            FedExTools.getResponse(self)
            self.checkForError()
            this_cost = float(self.responsexml.documentElement.getElementsByTagName('NetCharge')[0].firstChild.nodeValue)
            # Preferred clients get a discount from FedEx. In our case we do not pass
            # the preferred cost to client, we return standard cost.
            this_discount = float(self.responsexml.documentElement.getElementsByTagName('EffectiveNetDiscount')[0].firstChild.nodeValue)
            self.total_cost += this_cost + this_discount
            if self.DEBUG: print "Weight: %s, Count: %s, Charge: $%s, Overall: $%s" % (weight, count, this_cost, self.total_cost)
        if self.DEBUG: print "-------------------------------------------------"
        return {
            'price'         :   self.total_cost,
            'service_code'  :   self.service,
            'service_name'  :   SERVICES[self.service],
        }

from datetime import timedelta, datetime, date
import timezone
import time

def next_business_day( t, ship_delay = (1,1,1,1,3,2,1) ):
    # Get a time that we can offset without running afoul of leap seconds
    safe_t = t.replace(hour=0)
    days_to_skip = ship_delay[t.weekday()]
    return (safe_t + timedelta(days_to_skip)).date()

class FedExAvailableRates(FedExTools, AbstractShipping.SimpleRate):
    """Subclass of FedExTools that queries FedEx for a list of shipping rates
    based on source, destination, and total weight of packages.
    
    For specifics, see the FedEx OnLine Tools Rates & Service Selection
    XML Tool Developer's Guide."""
    
    def __init__(self, login, **kwargs):
        """Initializes self with the
        Transaction ID/AccountNumber/MeterNumber combo as well 
        as information on the source and destination of the package.
                
        A list of FedEx country codes can be found in the appendix of the
        FedEx Ship Manager API XML Transaction Guide."""

        # Initialize Access Request     
        FedExTools.__init__(self, login, kwargs['carrier'])

        # Package Information, such as weight and packingtype, e.g. [(1.4,"FEDEXBOX"),...]
        self.package_info = []

        # If we got the full country name, convert it to a country code
        kwargs['to_country'] = COUNTRIES.get(kwargs.get('to_country', None),
                                             kwargs.get('to_country', None))
        # Build Request
        # <FDXRateRequest xmlns:...>
        request = _.FDXRateAvailableServicesRequest( **{
                'xmlns:api':APIURL
              , 'xmlns:xsi':XSIURL
              ,'xsi:noNamespaceSchemaLocation':'FDXRateAvailableServicesRequest.xsd'
            })[
                  self.request_header
                , _.ShipDate[ next_business_day(datetime.now(timezone.Eastern)) ]
                , _.DropoffType[ 'REQUESTCOURIER' ]
                , _.WeightUnits[ kwargs.get('weight_units','LBS') ]
                , _.Weight[ kwargs.get('weight','') ]
                  # FedEx Ground Home Delivery Packaging must be YOURPACKAGING only.
                , _.Packaging[ kwargs.get('packaging','YOURPACKAGING') ]
                  # Value will be overridden in getResponse()
                , _.OriginAddress[
                      _.StateOrProvinceCode[ kwargs.get('from_state','') ]
                    , _.PostalCode[ kwargs.get('from_zip_code','') ]
                    , _.CountryCode[ kwargs.get('from_country','US') ]
                 ]
                , _.DestinationAddress[
                      _.StateOrProvinceCode[ kwargs.get('to_state','') ]
                    , _.PostalCode[ kwargs.get('to_zip_code','') ]
                    , _.CountryCode[ kwargs.get('to_country','US') ]
                 ]
               , _.PackageCount[ 1 ]
               , _.Payment
             ]

        self.requestxml = xml_document(request)

        
    def addPackage(self, packages=[]):
        """Adds a package to the request. The request must contain at least
        one package
        
        Packages may be a single value representing the weight of the new package,
        a tuple/list of weights, or a tuple/list of (weight,packaging) tuples/lists.
        e.g. 
            packages=2.3
            
            packages=(2.3,6.0,7.5)
            
            packages=((2.3,'FEDEXBOX'),(6.0,'FEDEXTUBE'),7.5)
        Note: FedEx requires a weight-value of one decimal point, e.g. 7.0, 7.5, etc.
        Values sent to this function will be converted to that format automatically.
        """     
        if isinstance(packages, tuple) or isinstance(packages, list):
            for p in packages:
                if isinstance(p,(tuple,list)) and len(p) == 2:
                    weight = "%.1f" % p[0]
                    packaging = PACKAGING[p[1]]
                else:
                    weight = "%.1f" % p
                    packaging = PACKAGING['DEFAULT']
                self.package_info.append((weight,packaging),)
        else:
            weight = "%.1f" % packages
            packaging = PACKAGING['DEFAULT']
            self.package_info.append((weight,packaging),)

    def getResponse(self, returnAllResults=None):

        FedExTools.getResponse(self)

        result = []

        for i in self.responsexml.documentElement.getElementsByTagName('Entry'):
            service = i.getElementsByTagName('Service')[0].firstChild.nodeValue
            charge = i.getElementsByTagName('NetCharge')[0].firstChild.nodeValue
            transit_time = i.getElementsByTagName('TimeInTransit')

            if not transit_time:
                delivery_date = i.getElementsByTagName('DeliveryDate')
                if delivery_date:
                    delivery_date = delivery_date[0].firstChild.nodeValue
                    delivery_date = date(*time.strptime(delivery_date, '%Y-%m-%d')[0:3])
                    transit_time = (delivery_date - date.today()).days
                else:
                    transit_time = None
            else:
                transit_time = int(transit_time[0].firstChild.nodeValue)

            result.append((SERVICES[service],charge,transit_time))
        return result

        return self.responsexml.toprettyxml()
        """Queries the FedEx server for shipping information, and then returns
        the "best" shipping method (as specified in the SERVICES variable)
        as a dictionary containing:
            service_name    The FedEx Service Name (i.e., 'FedEx Ground')
            service_code    The FedEx Service Code (i.e., '03')
            price           The cost of shipping."""
        
        # Package dictionary finds package count grouped by weight/type. i.e.
        #   self.package_info = [(1,'FEDEXBOX'), (1,'FEDEXBOX'), (1.5,'FEDEXBOX')]
        # becomes
        #   package_dict = {(1,'FEDEXBOX'):2, (1.5,'FEDEXBOX'):1}
        package_dict = {}
        for pkg in self.package_info:
            if package_dict.get(pkg):
                package_dict[pkg] += 1
            else:
                package_dict[pkg] = 1
        
        self.total_cost = 0
        if self.DEBUG: print "-------------------------------------------------"
        for ((weight,packaging),count,) in package_dict.items():
            # FYI: FedEx rounds floats to decimal values.
            self.requestxml.documentElement.getElementsByTagName('Weight')[0].firstChild.nodeValue = weight
            self.requestxml.documentElement.getElementsByTagName('Packaging')[0].firstChild.nodeValue = packaging
            self.requestxml.documentElement.getElementsByTagName('PackageCount')[0].firstChild.nodeValue = count
            FedExTools.getResponse(self)
            self.checkForError()
            this_cost = float(self.responsexml.documentElement.getElementsByTagName('NetCharge')[0].firstChild.nodeValue)
            # Preferred clients get a discount from FedEx. In our case we do not pass
            # the preferred cost to client, we return standard cost.
            this_discount = float(self.responsexml.documentElement.getElementsByTagName('EffectiveNetDiscount')[0].firstChild.nodeValue)
            self.total_cost += this_cost + this_discount
            if self.DEBUG: print "Weight: %s, Count: %s, Charge: $%s, Overall: $%s" % (weight, count, this_cost, self.total_cost)
        if self.DEBUG: print "-------------------------------------------------"
        return {
            'price'         :   self.total_cost,
            'service_code'  :   self.service,
            'service_name'  :   SERVICES[self.service],
        }

    
