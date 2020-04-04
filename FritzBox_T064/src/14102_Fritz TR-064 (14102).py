# coding: UTF-8
import re
import urllib2
import ssl
import urlparse
import socket
import struct
import hashlib

##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class FritzTR_064_14102_14102(hsl20_3.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_3.BaseModule.__init__(self, homeserver_context, "hsl20_3_FritzBox")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_3.LOGGING_NONE,())
        self.PIN_I_SUID=1
        self.PIN_I_SPW=2
        self.PIN_I_BWIFI1ON=3
        self.PIN_I_BWIFI2ON=4
        self.PIN_I_BWIFI3ON=5
        self.PIN_I_BWIFI4ON=6
        self.PIN_O_SWIFI1SSID=1
        self.PIN_O_BRMWLAN1ONOFF=2
        self.PIN_O_SWIFI2SSID=3
        self.PIN_O_BRMWLAN2ONOFF=4
        self.PIN_O_SWIFI3SSID=5
        self.PIN_O_BRMWLAN3ONOFF=6
        self.PIN_O_SWIFI4SSID=7
        self.PIN_O_BRMWLAN4ONOFF=8
        self.FRAMEWORK._run_in_context_thread(self.on_init)

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##


    m_url_parsed = ""
    m_sServiceDscr = ""
    m_sNonce = ""
    m_sRealm = ""
    m_sAuth = ""

    def getServiceData(self, p_sStr, p_sServiceType):
        try:
            sServiceId = re.findall( '<serviceType>' + p_sServiceType + '<\\/serviceType>.*?<serviceId>(.*?)<\\/serviceId>', p_sStr, flags=re.S)[0]
            sControlURL = re.findall( '<serviceType>' + p_sServiceType + '<\\/serviceType>.*?<controlURL>(.*?)<\\/controlURL>', p_sStr, flags=re.S)[0]
            sEventSubURL = re.findall( '<serviceType>' + p_sServiceType + '<\\/serviceType>.*?<eventSubURL>(.*?)<\\/eventSubURL>', p_sStr, flags=re.S)[0]
            sSCPDURL = re.findall( '<serviceType>' + p_sServiceType + '<\\/serviceType>.*?<SCPDURL>(.*?)<\\/SCPDURL>', p_sStr, flags=re.S)[0]
            
            return { "serviceType": p_sServiceType,
                     "serviceId": sServiceId,
                     "controlURL": sControlURL,
                     "eventSubURL": sEventSubURL,
                     "SCPDURL": sSCPDURL}
        except Exception as e:
            self.DEBUG.set_value("Error", "getServiceData: " + str(e))
            print ("getServiceData: " + str(e))


    def doRegex(self, p_sMatchStr, p_sStr):
        sMatch = re.findall(p_sMatchStr, p_sStr, flags=re.S)

        if len(sMatch) == 0:
            return ""

        return sMatch[0]


    def interface_addresses(self, family=socket.AF_INET):
        for fam, _, _, _, sockaddr in socket.getaddrinfo('', None):
            if family == fam:
                yield sockaddr[0]


    # @return urlparse
    def discover(self):

        #SSDP request msg from application
        MCAST_MSG = ('M-SEARCH * HTTP/1.1\r\n' +
                     'HOST: 239.255.255.250:1900\r\n' +
                     'MAN: "ssdp:discover"\r\n' +
                     'MX: 5\r\n' +
                     'ST: urn:dslforum-org:device:InternetGatewayDevice:1\r\n' )

        MCAST_GRP = '239.255.255.250'
        MCAST_PORT = 1900

        for addr in self.interface_addresses():
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    
            # time to life fro multicast msg
            ttl = struct.pack('b', 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
            
            # specify interface to use for multicast msg
            sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(addr))
    
            sock.settimeout(1)
    
            try: 
                sock.sendto(MCAST_MSG, (MCAST_GRP, MCAST_PORT))
            except socket.error as e:
                self.DEBUG.set_value("Error", "discover: " + str(e))
                print (e)
                sock.close()
    
            while True:
                try:
                    data = sock.recv(1024)
                    
                    url_unparsed = self.doRegex('LOCATION: (.*)(?:\\n\\r|\\r\\n)SERVER:.*FRITZ!Box', data)
                    url_parsed = urlparse.urlparse(url_unparsed)
    
                    #(scheme='http', netloc='192.168.143.1:49000', path='/tr64desc.xml', params='', query='', fragment='')
                    if url_parsed.netloc:
                        sock.close()
                        return url_parsed
    
                except socket.timeout:
                    print ("Timeout")
                    break
    
            sock.close()


    def getSecurityPort(self, p_url_parsed):

        url = p_url_parsed.geturl() + "/upnp/control/deviceinfo"
        url_parsed = urlparse.urlparse(url)

        # Build a SSL Context to disable certificate verification.
        ctx = ssl._create_unverified_context()
        response_data = ""

        headers={'Host': url_parsed.hostname,
                 'CONTENT-TYPE': 'text/xml; charset="utf-8',
                 'SOAPACTION': "urn:dslforum-org:service:DeviceInfo:1#GetSecurityPort"}

        data= ('<?xml version="1.0"?>' +
               '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" ' +
               's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">' +
               '<s:Body><u:GetSecurityPort xmlns:u="urn:dslforum-' +
               'org:service:DeviceInfo:1"></u:GetSecurityPort>' +
               '</s:Body></s:Envelope>')

        try:
            # Build a http request and overwrite host header with the original hostname.
            request = urllib2.Request(url, data=data, headers=headers)

            # Open the URL and read the response.
            response = urllib2.urlopen(request, context=ctx)
            response_data = response.read()
        except Exception as e:
            self.DEBUG.set_value("Error", "getSecurityPort: " + str(e))
            print ("getSecurityPort: " + str(e))

        return self.doRegex('<NewSecurityPort>(.*?)<\\/NewSecurityPort>', response_data)


    def getData(self, p_sUrl):
        url_parsed = urlparse.urlparse(p_sUrl)

        # Build a SSL Context to disable certificate verification.
        ctx = ssl._create_unverified_context()
        response_data = ""

        try:
            # Build a http request and overwrite host header with the original hostname.
            request = urllib2.Request(p_sUrl, headers={'Host':url_parsed.hostname})
            # Open the URL and read the response.
            response = urllib2.urlopen(request, context=ctx)
            response_data = response.read()
        except Exception as e:
            self.DEBUG.set_value("Error", "getData: " + str(e))
            print (str(e))
        return response_data


    def calcAuthResp(self, p_sUid, p_sPw, p_sRealm, p_sNonce):
        secret = hashlib.md5(p_sUid + ":" + p_sRealm + ":" + p_sPw)
        response = hashlib.md5( secret.hexdigest() + ":" + p_sNonce)
        return response.hexdigest()


    def getSoapHeader(self, p_sData, p_sUId, p_sPw):
        sAuthStat = self.doRegex('<Status>(.*?)<\\/Status>', p_sData)
        sHeader = ""
        
        if (sAuthStat == ""):
            sHeader = ('<s:Header>\n\t<h:InitChallenge ' +
                       'xmlns:h="http://soap-authentication.org/digest/2001/10/" ' +
                       's:mustUnderstand="1">\n\t\t' + 
                       '<UserID>' + p_sUId + '</UserID>\n\t</h:InitChallenge >\n' +
                       '</s:Header>')

        elif  (sAuthStat == "Unauthenticated"):
            #Get Auth data
            self.m_sNonce = self.doRegex("<Nonce>(.*?)<\\/Nonce>", p_sData)
            self.m_sRealm = self.doRegex("<Realm>(.*?)<\\/Realm>", p_sData)
            self.m_sAuth = self.calcAuthResp(p_sUId, p_sPw, self.m_sRealm, self.m_sNonce)
            
            sHeader = ('<s:Header>\n\t<h:ClientAuth ' +
                       'xmlns:h="http://soap-authentication.org/digest/2001/10/" ' +
                       's:mustUnderstand="1">' +
                       '\n\t\t<Nonce>' + self.m_sNonce + '</Nonce>' +
                       '\n\t\t<Auth>' + self.m_sAuth + '</Auth>' +
                       '\n\t\t<UserID>' + p_sUId + '</UserID>' +
                       '\n\t\t<Realm>' + self.m_sRealm + '</Realm>\n\t</h:ClientAuth>\n</s:Header>')

        return sHeader


    ## 
    ## @attr p_sFormerResp Response from a previous request
    def getSopaReq(self, p_url_parsed, p_sUId, p_sPw, p_grServiceData, p_sAction, p_AttrList, p_sFormerResp):

        sUrl = (p_url_parsed.geturl() + p_grServiceData["controlURL"])
        url_parsed = urlparse.urlparse(sUrl)

        # Build a SSL Context to disable certificate verification.        
        htmlHdr={'Host': p_url_parsed.hostname,
                 'CONTENT-TYPE': 'text/xml; charset="utf-8"',
                 'SOAPACTION': '"' + p_grServiceData["serviceType"] + "#" + p_sAction + '"'}

        sSoapHdr = self.getSoapHeader(p_sFormerResp, p_sUId, p_sPw)

        data= ('<?xml version="1.0" encoding="utf-8"?>\n' +
               '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" ' +
               's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\n'+
               sSoapHdr + '\n<s:Body>\n\t<u:' + p_sAction + ' xmlns:u="' + 
               p_grServiceData["serviceType"] + '">')

        for key in p_AttrList:
            data += ('\n\t\t<' + key + '>' + p_AttrList[key] + '</' + key + '>')

        data += ('\n\t</u:' + p_sAction + '>\n</s:Body>\n</s:Envelope>')

        return urllib2.Request(url_parsed.geturl(), data = data, headers = htmlHdr)


    def setSoapAction(self, url_parsed, p_sUId, p_sPw, p_grServiceData, p_sAction, p_AttrList, bSecure=False):
        # Build a SSL Context to disable certificate verification.
        ctx = ssl._create_unverified_context()
        response_data = ""

        for x in range(0, 2):
            request = self.getSopaReq(url_parsed, p_sUId, p_sPw, p_grServiceData, p_sAction, p_AttrList, response_data)
            #print "\n" + request.get_full_url()
            #print request.header_items()
            #print "\n" + request.get_data() + "\n"

            try:
                response = urllib2.urlopen(request, context=ctx)
                response_data = response.read()
                #print response_data
                
                sAuthStat = self.doRegex('<Status>(.*?)<\\/Status>', response_data)

                if ( sAuthStat != "Unauthenticated"):
                    break
    
            except urllib2.HTTPError as e:
                response_data = e.read()
    
            except Exception as e:
                self.DEBUG.set_value("Error", "setSoapAction: " + str(e))
                print ("setWifiActive loop" + str(x) + ": " + str(e))

        dic = {}
        response_data = self.doRegex('<u:' + p_sAction + 'Response.*?>(?:\\n|)(.*?)(?:\\n|)<\\/u:' + p_sAction + 'Response>', response_data)
        #if response data is available; e.g. if a set command has been send, no return value is provided
        if response_data:
            response_data = re.findall('(<.*?<\\/.*?>)',response_data, flags=re.S)
            for i in range(0, len(response_data)):
                key = self.doRegex('<(.*?)>', response_data[i])
                val = self.doRegex('>(.*?)<', response_data[i])
                dic.update({key : val})
        return dic


    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()


    def on_input_value(self, index, value):
        
        #self.PIN_I_BWIFI1ON=4
        #self.PIN_I_BWIFI2ON=5
        
        ############################################
        sUId = self._get_input_value(self.PIN_I_SUID)
        sPw = self._get_input_value(self.PIN_I_SPW)
        nWifiIdx = 1
        
        bWifiOn = int(value)
        if (index == self.PIN_I_BWIFI1ON):
            nWifiIdx = 1
            
        elif (index== self.PIN_I_BWIFI2ON):
            nWifiIdx = 2
            
        elif (index== self.PIN_I_BWIFI3ON):
            nWifiIdx = 3

        elif (index== self.PIN_I_BWIFI4ON):
            nWifiIdx = 4
        ############################################
        
        #self.DEBUG.add_message("Set switch: " + str(self._get_input_value(self.PIN_I_BONOFF)))
        #self._set_output_value(self.PIN_O_BRMONOFF, grOn["data"])
        #self.DEBUG.set_value("Switch cmd", sUrl)

        if (index == self.PIN_I_SUID or index == self.PIN_I_SPW):
            return


        if self.m_url_parsed == "":
            self.m_url_parsed = self.discover()
            #print "Discovery: \t" + url_parsed.geturl()

            if(not self.m_url_parsed):
                self.DEBUG.add_message("Could not discover Frtz!Box")
                #print "No data to continue. Quitting."
                return

            self.m_sServiceDscr = self.getData(self.m_url_parsed.geturl())
    
            self.m_url_parsed = urlparse.urlparse(self.m_url_parsed.scheme + "://" + self.m_url_parsed.netloc)
            self.DEBUG.add_message("Fritz!Box URL " + self.m_url_parsed.geturl())

            # work with device info
            serviceData = self.getServiceData(self.m_sServiceDscr, "urn:dslforum-org:service:DeviceInfo:1")
    
            # get security port
            data = self.setSoapAction(self.m_url_parsed, sUId, sPw, serviceData, "GetSecurityPort", {})
            #print "\n---" 
            #print data 
            #print "---\n"
    
            if not 'NewSecurityPort' in data:
                self.DEBUG.add_message("Could retrieve security port from Fritz!Box")
            else:
                sSPort = data['NewSecurityPort']
                url = 'https://' + self.m_url_parsed.hostname + ":" + sSPort
                self.m_url_parsed = urlparse.urlparse(url)
                self.DEBUG.set_value("Fritz!Box URL", self.m_url_parsed.geturl())

        #work with wifi
        serviceData = self.getServiceData(self.m_sServiceDscr, "urn:dslforum-org:service:WLANConfiguration:" + str(nWifiIdx))

        # switch on wifi
        attrList = {"NewEnable" : str(bWifiOn)}
        self.DEBUG.set_value("Requested Wifi-Status", ("idx: " + str(nWifiIdx) + "; On: " + str(bWifiOn)))
        data = self.setSoapAction(self.m_url_parsed, sUId, sPw, serviceData, "SetEnable", attrList)
        #print "\n---"
        #print data
        #print "---\n"

        #get wifi status
        attrList = {} #{"NewEnable":"", "NewStatus":"", "NewSSID":""}
        data = self.setSoapAction(self.m_url_parsed, sUId, sPw, serviceData, "GetInfo", attrList)
        #print "\n---" 
        #print data 
        #print "---\n"
        #print "\n\nFinished."
        nOn = ((data["NewStatus"] == "Up") and (data["NewEnable"] == '1'))

        if nWifiIdx == 1:
            self._set_output_value(self.PIN_O_BRMWLAN1ONOFF, nOn)
            self._set_output_value(self.PIN_O_SWIFI1SSID, data["NewSSID"])
        
        elif nWifiIdx == 2:
            self._set_output_value(self.PIN_I_BWIFI2ON, nOn)
            self._set_output_value(self.PIN_O_BRMWLAN2ONOFF, data["NewSSID"])

