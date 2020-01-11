# coding: UTF-8
import json
import re
import urllib2
import ssl
import urlparse
import time

##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class DWDUnwetter_14101_14101(hsl20_3.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_3.BaseModule.__init__(self, homeserver_context, "hsl20_3_dwd")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_3.LOGGING_NONE,())
        self.PIN_I_NTRIGGER=1
        self.PIN_I_SCITYID=2
        self.PIN_I_SCITY=3
        self.PIN_O_SHEADLINE=1
        self.PIN_O_SDESCR=2
        self.PIN_O_SINSTR=3
        self.PIN_O_FSTART=4
        self.PIN_O_FSTOP=5
        self.PIN_O_FLEVEL=6
        self.PIN_O_BACTIVE=7
        self.PIN_O_BERROR=8
        self.PIN_O_SJSON=9
        self.FRAMEWORK._run_in_context_thread(self.on_init)

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##

    m_sCityId = ""
    m_bValidData = False

    def getData(self):
        #https://www.dwd.de/DWD/warnungen/warnapp/json/warnings.json
        url_parsed = urlparse.urlparse("https://www.dwd.de/DWD/warnungen/warnapp/json/warnings.json")
        # Use Framework to resolve the host ip adress. 
        host_ip = self.FRAMEWORK.resolve_dns(url_parsed.hostname)
        # Append port if provided.
        netloc = host_ip
        if(url_parsed.port!=None):
            netloc+=':%s' % url_parsed.port
        # Build URL with the host replaced by the resolved ip address.
        url_resolved = urlparse.urlunparse((url_parsed[0], netloc) + url_parsed[2:])
        # Build a SSL Context to disable certificate verification.
        ctx = ssl._create_unverified_context()
        
        try:
            # Build a http request and overwrite host header with the original hostname.
            request = urllib2.Request(url_resolved, headers={'Host':url_parsed.hostname})
            # Open the URL and read the response.
            response = urllib2.urlopen(request, context=ctx)
            response_data = response.read()
        except Exception as e:
            self._set_output_value(self.PIN_O_BERROR, True)
            self.DEBUG.self.DEBUG.add_message("Error connecting to www.dwd.de: " + str(e))
        return response_data

    def getCityJson(self, sJson, sCityId):
        sPattern = '.*"' + sCityId + '":(\[.*?\])'
        reMatch = re.match(sPattern, sJson)
        if (reMatch):
            sCityJson = reMatch.group(1)
            return sCityJson
        else:
            return None

    # gets the element nIdx of the list grJson
    def getMaxWarnLvl(self, grWarningsLst):
        nMaxLvl = 0
        nIdxMaxLvl = -1
        
        for i in range(0, len(grWarningsLst)):
            nLevel = self.getVal(grWarningsLst[i], "level")
            
            if (nLevel>nMaxLvl) and (nLevel<=10) and (nLevel > 0):
                nMaxLvl = nLevel
                nIdxMaxLvl = i
        
        return {"level":nMaxLvl, "idx":nIdxMaxLvl}

    def getVal(self, sJson, sKey):
        val = ""
        if sKey in sJson:
            val = sJson[sKey]

        return val
    
    def getCityId(self, sCityName):
        sCityId = "0"
        sJson = self.getData()
        sPattern = '.*"([0-9]+?)":.*?' + sCityName
        reMatch = re.match(sPattern, sJson)
        if (reMatch):
            sCityId = reMatch.group(1)

        return sCityId

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()

    def on_input_value(self, index, value):
        data = ""
        cityJson = "---"
        m_sCityId = self._get_input_value(self.PIN_I_SCITYID)
        
        if ((m_sCityId == "") or 
            (self._get_input_value(self.PIN_I_SCITY) == "")):
            self._set_output_value(self.PIN_O_BERROR, True)
            self.DEBUG.self.DEBUG.add_message("Could not retrieve City Id")
            return

        # retrieve city id if not done before
        if (m_sCityId == ""):
            m_sCityId = self.getCityId(self._get_input_value(self.PIN_I_SCITY))

        # get json date if triggered
        if (index == self.PIN_I_NTRIGGER) and (value == True):
            data = self.getData()
            cityJson = self.getCityJson(data, self._get_input_value( self.PIN_I_SCITYID))

        # retrieve city data 
        if (cityJson != None):
            m_bValidData = True
            
            self._set_output_value(self.PIN_O_SJSON, cityJson)

            grWarningsLst = json.loads("[]")

            try:
                grWarningsLst = json.loads(cityJson)
            except Exception as e:
                self._set_output_value(self.PIN_O_BERROR, True)
                self.DEBUG.set_value("Error", str(e))
                return

            grRet = self.getMaxWarnLvl(grWarningsLst)
            nIdx = grRet["idx"]

            sHeadline = self.getVal(grWarningsLst[nIdx], "headline")
            sDesrc = self.getVal(grWarningsLst[nIdx], "description")
            sInstr = self.getVal(grWarningsLst[nIdx], "instruction")
            nStart = self.getVal(grWarningsLst[nIdx], "start")
            nEnd = self.getVal(grWarningsLst[nIdx], "end")

            self._set_output_value(self.PIN_O_SHEADLINE, sHeadline.encode("ascii", "xmlcharrefreplace"))
            self._set_output_value(self.PIN_O_SDESCR, sDesrc.encode("ascii", "xmlcharrefreplace"))
            self._set_output_value(self.PIN_O_SINSTR, sInstr.encode("ascii", "xmlcharrefreplace"))
            self._set_output_value(self.PIN_O_FSTART, nStart)
            self._set_output_value(self.PIN_O_FSTOP, nEnd)
            self._set_output_value(self.PIN_O_FLEVEL, grRet["level"])
            self._set_output_value(self.PIN_O_BERROR, False)

            # determine if warn window is active
            # time is provided as us but function demands s
            currentTime = time.localtime()
            if ((time.localtime(nEnd / 1000) > currentTime) and
                (currentTime > time.localtime(nStart / 1000))):
                self._set_output_value(self.PIN_O_BACTIVE, True)
            else:
                self._set_output_value(self.PIN_O_BACTIVE, False)

        # reset data if json does not contain city data
        else:
            if (m_bValidData == True):
                m_bValidData = False
                self._set_output_value(self.PIN_O_SHEADLINE, "")
                self._set_output_value(self.PIN_O_SDESCR, "")
                self._set_output_value(self.PIN_O_SINSTR, "")
                self._set_output_value(self.PIN_O_FSTART, 0)
                self._set_output_value(self.PIN_O_FSTOP, 0)
                self._set_output_value(self.PIN_O_FLEVEL, 0)
                self._set_output_value(self.PIN_O_BACTIVE, False)
                self._set_output_value(self.PIN_O_BERROR, False)
