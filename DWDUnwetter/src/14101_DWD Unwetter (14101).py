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
        self.PIN_O_FLEVEL=2
        self.PIN_O_SDESCR=3
        self.PIN_O_SINSTR=4
        self.PIN_O_FSTART=5
        self.PIN_O_FSTOP=6
        self.PIN_O_SALLWRNSTR=7
        self.PIN_O_SLV1STR=8
        self.PIN_O_SLV2STR=9
        self.PIN_O_SLV3STR=10
        self.PIN_O_SLV4STR=11
        self.PIN_O_SPREWRNSTR=12
        self.PIN_O_SHEATWRNSTR=13
        self.PIN_O_SUVWRNSTR=14
        self.PIN_O_BACTIVE=15
        self.PIN_O_BERROR=16
        self.PIN_O_SJSON=17
        self.FRAMEWORK._run_in_context_thread(self.on_init)

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##

    m_sCityId = ""
    m_bValidData = False
    m_bWarnActive = False

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
        response_data = ""
        
        try:
            # Build a http request and overwrite host header with the original hostname.
            request = urllib2.Request(url_resolved, headers={'Host':url_parsed.hostname})
            # Open the URL and read the response.
            response = urllib2.urlopen(request, context=ctx)
            response_data = response.read()
        except Exception as e:
            self._set_output_value(self.PIN_O_BERROR, True)
            self.DEBUG.add_message("Error connecting to www.dwd.de: " + str(e))
        return response_data

    def getCityJson(self, sJson, sCityId):
        prog = re.compile('"' + sCityId + '":\\[(.*?)\\]')
        reMatches = prog.finditer(sJson)
        res = "["
        i = 0

        for x in reMatches:
            res = res + x.group(1) + ","
            i = i + 1

        if (i == 0):
            return "[]"

        res = res[0:len(res)-1]
        res = res + "]"
        return res

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
    
    def getAllWarnings(self, grWarningsLst):
        sMsg = ""
        for i in range(0, len(grWarningsLst)):
            sMsg += self.getVal(grWarningsLst[i], "event")
            if (i < len(grWarningsLst) - 1):
                sMsg += ", "

        return sMsg
    
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
        self.m_sCityId = self._get_input_value(self.PIN_I_SCITYID)

        # retrieve city id if not done before
        if (self.m_sCityId == ""):
            self.m_sCityId = self.getCityId(self._get_input_value(self.PIN_I_SCITY))

        if (self.m_sCityId == "0"):
            self._set_output_value(self.PIN_O_BERROR, True)
            self.DEBUG.add_message("Could not retrieve City Id")
            return

        # get json date if triggered
        if (index == self.PIN_I_NTRIGGER) and (value == True):
            data = self.getData()
            cityJson = self.getCityJson(data, self._get_input_value( self.PIN_I_SCITYID))

        # retrieve city data 
        if (cityJson != None):
            self.m_bValidData = True
            
            self._set_output_value(self.PIN_O_SJSON, cityJson)

            grWarningsLst = json.loads("[]")

            try:
                grWarningsLst = json.loads(cityJson)
            except Exception as e:
                self._set_output_value(self.PIN_O_BERROR, True)
                self.DEBUG.set_value("Error", str(e))
                return

            grRet = self.getMaxWarnLvl(grWarningsLst)
            nIdx = grRet["idx"] #{"level":nMaxLvl, "idx":nIdxMaxLvl}

            sHeadline = self.getVal(grWarningsLst[nIdx], "headline")
            sDesrc = self.getVal(grWarningsLst[nIdx], "description")
            sInstr = self.getVal(grWarningsLst[nIdx], "instruction")
            nStart = self.getVal(grWarningsLst[nIdx], "start")
            nEnd = self.getVal(grWarningsLst[nIdx], "end")
            sAllWarnings = self.getAllWarnings(grWarningsLst)

            self._set_output_value(self.PIN_O_SHEADLINE, sHeadline.encode("ascii", "xmlcharrefreplace"))
            self._set_output_value(self.PIN_O_SDESCR, sDesrc.encode("ascii", "xmlcharrefreplace"))
            self._set_output_value(self.PIN_O_SINSTR, sInstr.encode("ascii", "xmlcharrefreplace"))
            self._set_output_value(self.PIN_O_FSTART, nStart / 1000)
            self._set_output_value(self.PIN_O_FSTOP, nEnd / 1000)
            self._set_output_value(self.PIN_O_FLEVEL, grRet["level"])
            self._set_output_value(self.PIN_O_BERROR, False)
            self._set_output_value(self.PIN_O_SALLWRNSTR, sAllWarnings.encode("ascii", "xmlcharrefreplace"))

            self._set_output_value(self.PIN_O_SHEATWRNSTR, "")
            self._set_output_value(self.PIN_O_SLV1STR, "")
            self._set_output_value(self.PIN_O_SLV2STR, "")
            self._set_output_value(self.PIN_O_SLV3STR, "")
            self._set_output_value(self.PIN_O_SLV4STR, "")
            self._set_output_value(self.PIN_O_SPREWRNSTR, "")
            self._set_output_value(self.PIN_O_SUVWRNSTR, "")

            if(int(grRet["level"]) == 1):
                self._set_output_value(self.PIN_O_SPREWRNSTR, sAllWarnings.encode("ascii", "xmlcharrefreplace"))
            elif(int(grRet["level"]) == 2):
                self._set_output_value(self.PIN_O_SLV1STR, sAllWarnings.encode("ascii", "xmlcharrefreplace"))
            elif(int(grRet["level"]) == 3):
                self._set_output_value(self.PIN_O_SLV2STR, sAllWarnings.encode("ascii", "xmlcharrefreplace"))
            elif(int(grRet["level"]) == 4):
                self._set_output_value(self.PIN_O_SLV3STR, sAllWarnings.encode("ascii", "xmlcharrefreplace"))
            elif(int(grRet["level"]) == 5):
                self._set_output_value(self.PIN_O_SLV4STR, sAllWarnings.encode("ascii", "xmlcharrefreplace"))
            elif(int(grRet["level"]) == 10):
                self._set_output_value(self.PIN_O_SHEATWRNSTR, sAllWarnings.encode("ascii", "xmlcharrefreplace"))
            elif(int(grRet["level"]) == 20):
                self._set_output_value(self.PIN_O_SUVWRNSTR, sAllWarnings.encode("ascii", "xmlcharrefreplace"))

            # determine if warn window is active
            # time is provided as us but function demands s
            # "start":1578765600 000,"end":1578823200 000
            currentTime = time.localtime()
            if ((time.localtime(nEnd / 1000) > currentTime) and
                (currentTime > time.localtime(nStart / 1000))):
                # sbc
                if (self.m_bWarnActive == False):
                    self._set_output_value(self.PIN_O_BACTIVE, True)
                    self.m_bWarnActive = True
            else:
                # sbc
                if (self.m_bWarnActive == True):
                    self._set_output_value(self.PIN_O_BACTIVE, False)
                    self.m_bWarnActive = False

        # reset data if json does not contain city data
        else:
            self.DEBUG.add_message("No data found in json file for requested region.")
            
            if (self.m_bValidData == True):
                self.m_bValidData = False
                self._set_output_value(self.PIN_O_SHEADLINE, "")
                self._set_output_value(self.PIN_O_SDESCR, "")
                self._set_output_value(self.PIN_O_SINSTR, "")
                self._set_output_value(self.PIN_O_FSTART, 0)
                self._set_output_value(self.PIN_O_FSTOP, 0)
                self._set_output_value(self.PIN_O_FLEVEL, 0)
                self._set_output_value(self.PIN_O_BACTIVE, False)
                self._set_output_value(self.PIN_O_BERROR, False)
                self._set_output_value(self.PIN_O_SHEATWRNSTR, "")
                self._set_output_value(self.PIN_O_SLV1STR, "")
                self._set_output_value(self.PIN_O_SLV2STR, "")
                self._set_output_value(self.PIN_O_SLV3STR, "")
                self._set_output_value(self.PIN_O_SLV4STR, "")
                self._set_output_value(self.PIN_O_SPREWRNSTR, "")
                self._set_output_value(self.PIN_O_SUVWRNSTR, "")
                self._set_output_value(self.PIN_O_SALLWRNSTR, "")
