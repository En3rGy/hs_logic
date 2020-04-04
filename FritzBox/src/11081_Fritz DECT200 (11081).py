# coding: UTF-8
import re
import httplib
import urllib
import codecs
import md5

##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class FritzDECT200_11081_11081(hsl20_3.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_3.BaseModule.__init__(self, homeserver_context, "hsl20_3_FritzBox")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_3.LOGGING_NONE,())
        self.PIN_I_SXML=1
        self.PIN_I_SSID=2
        self.PIN_I_SIP=3
        self.PIN_I_SUSERPW=4
        self.PIN_I_SAIN=5
        self.PIN_I_BONOFF=6
        self.PIN_I_NSIDTIMEOUT=7
        self.PIN_I_NTRIGGER=8
        self.PIN_O_BRMONOFF=1
        self.PIN_O_NMW=2
        self.PIN_O_NZAEHLERWH=3
        self.PIN_O_NTEMP=4
        self.PIN_O_SSID=5
        self.PIN_O_SXML=6
        self.FRAMEWORK._run_in_context_thread(self.on_init)

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##

    def getSid(self, sUserPw, sIp):
        ## split username from password
        sPw = sUserPw[sUserPw.find('@') + 1:]
        sUser = sUserPw.split('@')[0]

        response = urllib.urlopen('http://' + sIp + '/login_sid.lua')
        sChallange = response.read()
        sChallange = re.findall('<Challenge>(.*?)</Challenge>', sChallange)[0]

        if len(sChallange) == 0:
            return ""

        sChallangeresp = codecs.utf_16_le_encode(unicode('%s-%s' %
                                                         (sChallange, sPw)))[0]
        sChallangeresp = (sChallange + "-" +
                          md5.new(sChallangeresp).hexdigest().lower())

        data = {"response": sChallangeresp, "username": sUser}
        response = urllib.urlopen('http://' + sIp + '/login_sid.lua',
                                  urllib.urlencode(data))
        sSid = response.read()
        sSid = re.findall('<SID>(.*?)</SID>', sSid)

        if len(sSid) == 0:
            return ""

        sSid = sSid[0]

        if sSid == '0000000000000000':
            return ""
        else:
            return sSid

    def setDect200(self, bOnOff, sIp, sAin, sSid):
        # Dect200 #1 on/off
        sCmd = 'setswitchoff'
        if bool(bOnOff) is True:
            sCmd = "setswitchon"

        sUrl = str('http://' + sIp +
                '/webservices/homeautoswitch.lua?ain=' + sAin +
                '&switchcmd=' + sCmd +
                '&sid=' + sSid)
        self.DEBUG.set_value("Switch cmd", sUrl)
        resp = urllib.urlopen(sUrl)
        self.DEBUG.set_value("Set switch result", resp.getcode())
        return {"code": resp.getcode(), "data": resp.read()}

    def getXml(self, sIp, sSid):
        resp = urllib.urlopen('http://' +
                              sIp +
                              '/webservices/homeautoswitch.lua?' +
                              'switchcmd=getdevicelistinfos' +
                              '&sid=' + sSid)
        self.DEBUG.set_value("Get XML result", resp.getcode())
        return {"code": resp.getcode(), "data": resp.read()}

    def getDect200Status(self, sXml, sAin):
        data = {}
        sState = re.findall('<device identifier="' + sAin +
                            '" id=.*?>.*?<state>(.*?)</state>', sXml)

        if len(sState) == 0:
            return {}
        else:
            sState = sState[0]

        if sState != "":
            data["state"] = int(sState)

        sPower = re.findall('<device identifier="' + sAin +
                            '" id=.*?>.*?<power>(.*?)</power>', sXml)
        if len(sPower) != 0:
            data["power"] = int(sPower[0])

        sEnergy = re.findall('<device identifier="' + sAin +
                             '" id=.*?>.*?<energy>(.*?)</energy>', sXml)
        if len(sEnergy) != 0:
            data["energy"] = int(sEnergy[0])

        sTemp = re.findall('<device identifier="' + sAin +
                           '" id=.*?>.*?<celsius>(.*?)</celsius>', sXml)

        if len(sTemp) != 0:
            nTemp = int(sTemp[0])
            sOffset = re.findall('<device identifier="' + sAin +
                                 '" id=.*?>.*?<offset>(.*?)</offset>', sXml)

            if len(sOffset) != 0:
                nTemp = nTemp + int(sOffset[0])

            data["temp"] = nTemp / 10.0

        return data

    def logout(self, sIp, sSid):
        httpClient = httplib.HTTPConnection('http://' + sIp, timeout=5)
        httpClient.request("GET", '/login_sid.lua?logout=true&sid=' + sSid)
        response = httpClient.getresponse()
        return response.status

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()
        self.DEBUG.set_value("XML", "-")

    def on_input_value(self, index, value):

        sSid = self._get_input_value(self.PIN_I_SSID)
        nLoop = 0

        # If SID did not work, retry with new SID
        while nLoop < 2:
            nLoop += 1

            # Get SID if not available
            if (((index == self.PIN_I_BONOFF) or
                 (index == self.PIN_I_NTRIGGER)) and
                 (not sSid)):

                sSid = self.getSid(self._get_input_value(self.PIN_I_SUSERPW),
                                   self._get_input_value(self.PIN_I_SIP))
                self.DEBUG.set_value("SID", sSid)

                if sSid == "":
                    self.DEBUG.add_message("Could not receive valid SID")
                else:
                    self._set_output_value(self.PIN_O_SSID, sSid)

            # If new XML available or trigger arrived,
            # get and process new status data
            if (index == self.PIN_I_SXML) or (index == self.PIN_I_NTRIGGER):
                grXml = ""

                if index == self.PIN_I_SXML:
                    grXml = {"code": 200, "data": value}

                if index == self.PIN_I_NTRIGGER:
                    grXml = self.getXml(self._get_input_value(self.PIN_I_SIP),
                                        sSid)
                    self.DEBUG.set_value("XML", grXml["data"])

                # Evaluate XML data
                ret = self.getDect200Status(grXml["data"],
                                            self._get_input_value(self.PIN_I_SAIN))

                if "state" in ret:
                    self._set_output_value(self.PIN_O_BRMONOFF, ret["state"])

                if "power" in ret:
                    self._set_output_value(self.PIN_O_NMW, ret["power"])

                if "energy" in ret:
                    self._set_output_value(self.PIN_O_NZAEHLERWH, ret["energy"])

                if "temp" in ret:
                    self._set_output_value(self.PIN_O_NTEMP, ret["temp"])

                if grXml["code"] == 200:
                    self._set_output_value(self.PIN_O_SXML, grXml["data"])
                    return
                else:
                    self.DEBUG.add_message("Error processing XML, code:" +
                                           str( grXml["code"]))
                    sSid = ""

            # Switch device on or of and report back new status
            if index == self.PIN_I_BONOFF:
                self.DEBUG.add_message("Set switch: " +
                                       str(self._get_input_value(self.PIN_I_BONOFF)))

                grOn = self.setDect200(self._get_input_value(self.PIN_I_BONOFF),
                                       self._get_input_value(self.PIN_I_SIP),
                                       self._get_input_value(self.PIN_I_SAIN),
                                       sSid)

                self._set_output_value(self.PIN_O_BRMONOFF, grOn["data"])

                if grOn["code"] == 200:
                    self.DEBUG.add_message("Switch set successfully.")
                    return
                else:
                    self.DEBUG.add_message("Error setting switch, code:" +
                                           str( grOn["code"]))

                    sSid = ""
