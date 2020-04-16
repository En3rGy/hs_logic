# coding: UTF-8
import re
import urllib2
import ssl
import urlparse
import socket
import struct
import hashlib
import threading
import json

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
        self.PIN_I_BWIFIGUESTON=6
        self.PIN_I_SMAC1=7
        self.PIN_I_SMAC2=8
        self.PIN_I_SMAC3=9
        self.PIN_I_SMAC4=10
        self.PIN_I_STELNO=11
        self.PIN_I_BDIAL=12
        self.PIN_I_NSOAPJSON=13
        self.PIN_I_NUPDATERATE=14
        self.PIN_O_SWIFI1SSID=1
        self.PIN_O_BRMWLAN1ONOFF=2
        self.PIN_O_SWIFI2SSID=3
        self.PIN_O_BRMWLAN2ONOFF=4
        self.PIN_O_SWIFI3SSID=5
        self.PIN_O_BRMWLAN3ONOFF=6
        self.PIN_O_SWIFIGUESTSSID=7
        self.PIN_O_BRMWLANGUESTONOFF=8
        self.PIN_O_SMAC1AVAIL=9
        self.PIN_O_SMAC2AVAIL=10
        self.PIN_O_SMAC3AVAIL=11
        self.PIN_O_SMAC4AVAIL=12
        self.PIN_O_SSOAPRPLY=13
        self.FRAMEWORK._run_in_context_thread(self.on_init)

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##


    m_url_parsed = ""
    m_sServiceDscr = ""
    m_sNonce = ""
    m_sRealm = ""
    m_sAuth = ""
    m_sUId = ""
    m_sPw = ""
    m_guestWifiIdx = 0

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
            self.DEBUG.set_value("14102 Error", "getServiceData: " + str(e))
            print ("getServiceData: " + str(e))


    def doRegex(self, p_sMatchStr, p_sStr):
        sMatch = re.findall(p_sMatchStr, p_sStr, flags=re.S)

        if len(sMatch) == 0:
            return ""

        return sMatch[0]


    def interface_addresses(self, family=socket.AF_INET):
        for fam, _, _, _, sockaddr in socket.getaddrinfo('', None, 0, 0, 0, socket.AI_NUMERICHOST):
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
        
        # hsl20_3.Framework.get_homeserver_private_ip
        sHsIp = self.FRAMEWORK.get_homeserver_private_ip()

        #for addr in self.interface_addresses():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        # time to life fro multicast msg
        ttl = struct.pack('b', 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        
        # specify interface to use for multicast msg
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(sHsIp))

        sock.settimeout(1)

        try: 
            sock.sendto(MCAST_MSG, (MCAST_GRP, MCAST_PORT))
        except socket.error as e:
            self.DEBUG.set_value("14102 Error", "discover: " + str(e))
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
            self.DEBUG.set_value("14102 Error", "getSecurityPort: " + str(e))
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
            self.DEBUG.set_value("14102 Error", "getData: " + str(e))
            print (str(e))
        return response_data


    def init_com(self):
        self.m_sUId = self._get_input_value(self.PIN_I_SUID)
        self.m_sPw = self._get_input_value(self.PIN_I_SPW)

        if self.m_url_parsed == "":
            self.m_url_parsed = self.discover()
            #print "Discovery: \t" + url_parsed.geturl()

            if(not self.m_url_parsed):
                self.DEBUG.add_message("14102 Could not discover Frtz!Box")
                #print "No data to continue. Quitting."
                return False

            self.m_sServiceDscr = self.getData(self.m_url_parsed.geturl())
            self.getGuestWifiIdx()

            self.m_url_parsed = urlparse.urlparse(self.m_url_parsed.scheme + "://" + self.m_url_parsed.netloc)
            self.DEBUG.add_message("14102 Fritz!Box URL: " + self.m_url_parsed.geturl())

            # work with device info
            serviceData = self.getServiceData(self.m_sServiceDscr, "urn:dslforum-org:service:DeviceInfo:1")

            # get security port
            data = self.setSoapAction(self.m_url_parsed, serviceData, "GetSecurityPort", {})

            if not 'NewSecurityPort' in data:
                self.DEBUG.add_message("14102 Could retrieve security port from Fritz!Box")
            else:
                sSPort = data['NewSecurityPort']
                url = 'https://' + self.m_url_parsed.hostname + ":" + sSPort
                self.m_url_parsed = urlparse.urlparse(url)
                self.DEBUG.add_message("14102 Fritz!Box URL: " + self.m_url_parsed.geturl())

        return True


    def getSoapHeader(self):
        sHeader = ""
        
        if (self.m_sAuth == ""):
            sHeader = ('<s:Header>\n\t<h:InitChallenge ' +
                       'xmlns:h="http://soap-authentication.org/digest/2001/10/" ' +
                       's:mustUnderstand="1">\n\t\t' + 
                       '<UserID>' + self.m_sUId + '</UserID>\n\t</h:InitChallenge >\n' +
                       '</s:Header>')

        else:
            sHeader = ('<s:Header>\n\t<h:ClientAuth ' +
                       'xmlns:h="http://soap-authentication.org/digest/2001/10/" ' +
                       's:mustUnderstand="1">' +
                       '\n\t\t<Nonce>' + self.m_sNonce + '</Nonce>' +
                       '\n\t\t<Auth>' + self.m_sAuth + '</Auth>' +
                       '\n\t\t<UserID>' + self.m_sUId + '</UserID>' +
                       '\n\t\t<Realm>' + self.m_sRealm + '</Realm>\n\t</h:ClientAuth>\n</s:Header>')

        return sHeader


    ## 
    ## @attr p_sFormerResp Response from a previous request
    def getSopaReq(self, p_url_parsed, p_grServiceData, p_sAction, p_AttrList):

        sUrl = (p_url_parsed.geturl() + p_grServiceData["controlURL"])
        url_parsed = urlparse.urlparse(sUrl)

        # Build a SSL Context to disable certificate verification.        
        htmlHdr={'Host': p_url_parsed.hostname,
                 'CONTENT-TYPE': 'text/xml; charset="utf-8"',
                 'SOAPACTION': '"' + p_grServiceData["serviceType"] + "#" + p_sAction + '"'}

        sSoapHdr = self.getSoapHeader()

        data= ('<?xml version="1.0" encoding="utf-8"?>\n' +
               '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" ' +
               's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\n'+
               sSoapHdr + '\n<s:Body>\n\t<u:' + p_sAction + ' xmlns:u="' + 
               p_grServiceData["serviceType"] + '">')

        for key in p_AttrList:
            data += ('\n\t\t<' + key + '>' + p_AttrList[key] + '</' + key + '>')

        data += ('\n\t</u:' + p_sAction + '>\n</s:Body>\n</s:Envelope>')

        return urllib2.Request(url_parsed.geturl(), data = data, headers = htmlHdr)


    def getAuthData(self, p_sData):
            self.m_sNonce = self.doRegex("<Nonce>(.*?)<\\/Nonce>", p_sData)
            self.m_sRealm = self.doRegex("<Realm>(.*?)<\\/Realm>", p_sData)

            secret = hashlib.md5(self.m_sUId + ":" + self.m_sRealm + ":" + self.m_sPw)
            response = hashlib.md5( secret.hexdigest() + ":" + self.m_sNonce)

            self.m_sAuth = response.hexdigest()
            print ("\n" + self.m_sAuth + "\n")

    def setSoapAction(self, url_parsed, p_grServiceData, p_sAction, p_AttrList, bSecure=False):
        # Build a SSL Context to disable certificate verification.
        ctx = ssl._create_unverified_context()
        response_data = ""

        for x in range(0, 2):
            request = self.getSopaReq(url_parsed, p_grServiceData, p_sAction, p_AttrList)

            try:
                response = urllib2.urlopen(request, context=ctx)
                response_data = response.read()
                print (response_data + "\n\n")

                self.getAuthData(response_data)

                sAuthStat = self.doRegex('<Status>(.*?)<\\/Status>', response_data)

                if ( sAuthStat != "Unauthenticated"):
                    break
    
            except urllib2.HTTPError as e:
                response_data = e.read()
                self.DEBUG.add_message("14102 setSoapAction: " + response_data)
    
            #except Exception as e:
            #    self.DEBUG.add_message("setSoapAction: " + str(e))
            #    print ("setWifiActive loop" + str(x) + ": " + str(e))

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


    def getGuestWifiIdx(self):
        wlanIF = re.findall("<serviceType>(urn:dslforum-org:service:WLANConfiguration:[0-9]<\\/serviceType>)", self.m_sServiceDscr, re.S)
        self.m_guestWifiIdx = len(wlanIF)
        self.DEBUG.set_value("14102 Guest WIFI Index", self.m_guestWifiIdx)


    def updateStatus(self):
        self.DEBUG.add_message("Status requested")
        
        nInterval = self._get_input_value(self.PIN_I_NUPDATERATE)
        if (nInterval > 0):
            if not self.init_com():
                return

            #work with wifi
            for nWifiIdx in range(1, (self.m_guestWifiIdx + 1)):
                serviceData = self.getServiceData(self.m_sServiceDscr, "urn:dslforum-org:service:WLANConfiguration:" + str(nWifiIdx))

                #get wifi status
                attrList = {} #{"NewEnable":"", "NewStatus":"", "NewSSID":""}
                data = self.setSoapAction(self.m_url_parsed, serviceData, "GetInfo", attrList)

                nOn = int(((data["NewStatus"] == "Up") and (data["NewEnable"] == '1')))

                if nWifiIdx == 1:
                    self._set_output_value(self.PIN_O_BRMWLAN1ONOFF, nOn)
                    self._set_output_value(self.PIN_O_SWIFI1SSID, data["NewSSID"])

                elif nWifiIdx == 2:
                    self._set_output_value(self.PIN_O_BRMWLAN2ONOFF, nOn)
                    self._set_output_value(self.PIN_O_SWIFI2SSID, data["NewSSID"])

                elif nWifiIdx == 3:
                    self._set_output_value(self.PIN_O_BRMWLAN3ONOFF, nOn)
                    self._set_output_value(self.PIN_O_SWIFI3SSID, data["NewSSID"])

                if nWifiIdx == self.m_guestWifiIdx:
                    self._set_output_value(self.PIN_O_BRMWLANGUESTONOFF, nOn)
                    self._set_output_value(self.PIN_O_SWIFIGUESTSSID, data["NewSSID"])
            ###End Wifi

            ###MAC attendence
            serviceData = self.getServiceData(self.m_sServiceDscr, "urn:dslforum-org:service:Hosts:1")
            for i in range(self.PIN_I_SMAC1, (self.PIN_I_SMAC4 + 1)):
                value = self._get_input_value(i)
                
                if value == "":
                    continue

                attrList = {"NewMACAddress" : value}
                data = self.setSoapAction(self.m_url_parsed, serviceData, "GetSpecificHostEntry", attrList)

                nRet = 0
                if (data):
                    nRet = int(data["NewActive"])

                if (i == self.PIN_I_SMAC1):
                    self._set_output_value(self.PIN_O_SMAC1AVAIL, nRet)
                elif (i == self.PIN_I_SMAC2):
                    self._set_output_value(self.PIN_O_SMAC2AVAIL, nRet)
                elif (i == self.PIN_I_SMAC3):
                    self._set_output_value(self.PIN_O_SMAC3AVAIL, nRet)
                elif (i == self.PIN_I_SMAC4):
                    self._set_output_value(self.PIN_O_SMAC4AVAIL, nRet)
            ### end mac discovery

            t = threading.Timer(nInterval, self.updateStatus).start()


    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()
        self.updateStatus()


    def on_input_value(self, index, value):
        ############################################
        self.m_sUId = self._get_input_value(self.PIN_I_SUID)
        self.m_sPw = self._get_input_value(self.PIN_I_SPW)
        nWifiIdx = 0
        nInterval = self._get_input_value(self.PIN_I_NUPDATERATE)
        ############################################
        
        #self.DEBUG.add_message("Set switch: " + str(self._get_input_value(self.PIN_I_BONOFF)))
        #self._set_output_value(self.PIN_O_BRMONOFF, grOn["data"])
        #self.DEBUG.set_value("Switch cmd", sUrl)

        if (index == self.PIN_I_SUID or index == self.PIN_I_SPW):
            return

        if not self.init_com():
            return

        if (index == self.PIN_I_NUPDATERATE):
            if (nInterval > 0):
                self.updateStatus()

        #work with wifi
        elif (index == self.PIN_I_BWIFI1ON or index == self.PIN_I_BWIFI2ON or index == self.PIN_I_BWIFI3ON or index == self.PIN_I_BWIFIGUESTON):

            bWifiOn = int(value)
            if (index == self.PIN_I_BWIFI1ON):
                nWifiIdx = 1
                
            elif (index == self.PIN_I_BWIFI2ON):
                nWifiIdx = 2
                
            elif (index == self.PIN_I_BWIFI3ON):
                nWifiIdx = 3
    
            elif (index ==self.PIN_I_BWIFIGUESTON):
                nWifiIdx = self.m_guestWifiIdx

            serviceData = self.getServiceData(self.m_sServiceDscr, "urn:dslforum-org:service:WLANConfiguration:" + str(nWifiIdx))

            # switch on wifi
            attrList = {"NewEnable" : str(bWifiOn)}
            self.DEBUG.add_message("14102 WIFI SOLL: idx " + str(nWifiIdx) + ", status " + str(bWifiOn))
            data = self.setSoapAction(self.m_url_parsed, serviceData, "SetEnable", attrList)

            #get wifi status
            attrList = {}
            data = self.setSoapAction(self.m_url_parsed, serviceData, "GetInfo", attrList)
            self.DEBUG.set_value("14102 SOAP Repl.", str(data))

            nOn = int(((data["NewStatus"] == "Up") and (data["NewEnable"] == '1')))


            if (nWifiIdx == self.m_guestWifiIdx):
                self._set_output_value(self.PIN_O_BRMWLANGUESTONOFF, nOn)
                self._set_output_value(self.PIN_O_SWIFIGUESTSSID, data["NewSSID"])
                self.DEBUG.add_message("RM Guest Wifi")

            if (nWifiIdx == 1):
                self._set_output_value(self.PIN_O_BRMWLAN1ONOFF, nOn)
                self._set_output_value(self.PIN_O_SWIFI1SSID, data["NewSSID"])
                self.DEBUG.add_message("RM Wifi 1")

            elif (nWifiIdx == 2):
                self._set_output_value(self.PIN_O_BRMWLAN2ONOFF, nOn)
                self._set_output_value(self.PIN_O_SWIFI2SSID, data["NewSSID"])
                self.DEBUG.add_message("RM Wifi 2")

            elif (nWifiIdx == 3):
                self._set_output_value(self.PIN_O_BRMWLAN3ONOFF, nOn)
                self._set_output_value(self.PIN_O_SWIFI3SSID, data["NewSSID"])
                self.DEBUG.add_message("RM Wifi 3")

        ###End Wifi

        elif (index == self.PIN_I_SMAC1 or index == self.PIN_I_SMAC2 or index == self.PIN_I_SMAC3 or index == self.PIN_I_SMAC4):
            serviceData = self.getServiceData(self.m_sServiceDscr, "urn:dslforum-org:service:Hosts:1")

            attrList = {"NewMACAddress" : value}
            data = self.setSoapAction(self.m_url_parsed, serviceData, "GetSpecificHostEntry", attrList)

            nRet = 0
            if (data):
                nRet = int(data["NewActive"])

            if (index == self.PIN_I_SMAC1):
                self._set_output_value(self.PIN_O_SMAC1AVAIL, nRet)
            elif (index == self.PIN_I_SMAC2):
                self._set_output_value(self.PIN_O_SMAC2AVAIL, nRet)
            elif (index == self.PIN_I_SMAC3):
                self._set_output_value(self.PIN_O_SMAC3AVAIL, nRet)
            elif (index == self.PIN_I_SMAC4):
                self._set_output_value(self.PIN_O_SMAC4AVAIL, nRet)
        ### end mac discovery

        elif (index == self.PIN_I_BDIAL):
            serviceData = self.getServiceData(self.m_sServiceDscr, "urn:dslforum-org:service:X_VoIP:1")

            if (value == 1): 
                attrList = {"NewX_AVM-DE_PhoneNumber" : self._get_input_value(self.PIN_I_STELNO)}
                data = self.setSoapAction(self.m_url_parsed, serviceData, "X_AVM-DE_DialNumber", attrList)
            
            elif (value == 0):
                attrList = {}
                data = self.setSoapAction(self.m_url_parsed, serviceData, "X_AVM-DE_DialHangup", attrList)
        ### end dial / call
        
        ### generic soap request
        elif (index == self.PIN_I_NSOAPJSON):
            # e.g.: '{"serviceType":"urn:dslforum-org:service:WLANConfiguration:1", "action_name":"SetEnable","argumentList":{"NewEnable":"1"}}'
            soapJson = self._get_input_value(self.PIN_I_NSOAPJSON)

            if soapJson:
                soapJson = soapJson.replace("&quot;", '"')
                res = json.loads(soapJson)
                serviceType = res["serviceType"]
                action_name = res["action_name"]
                argumentList = res ["argumentList"]

                serviceData = self.getServiceData(self.m_sServiceDscr, serviceType)
                data = self.setSoapAction(self.m_url_parsed, serviceData, action_name, argumentList)

                self._set_output_value(self.PIN_O_SSOAPRPLY, str(data))
