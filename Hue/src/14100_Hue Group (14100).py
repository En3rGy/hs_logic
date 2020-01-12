# coding: UTF-8
import httplib
import json

##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class HueGroup_14100_14100(hsl20_3.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_3.BaseModule.__init__(self, homeserver_context, "hsl20_3_Hue")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_3.LOGGING_NONE,())
        self.PIN_I_SGROUPSTATJSON=1
        self.PIN_I_SLIGHTSSTATJSON=2
        self.PIN_I_BTRIGGER=3
        self.PIN_I_SHUEIP=4
        self.PIN_I_NHUEPORT=5
        self.PIN_I_SUSER=6
        self.PIN_I_NGROUP=7
        self.PIN_I_NLIGHT=8
        self.PIN_I_BONOFF=9
        self.PIN_I_NBRI=10
        self.PIN_I_NHUE=11
        self.PIN_I_NSAT=12
        self.PIN_I_SSCENE=13
        self.PIN_O_BSTATUSONOFF=1
        self.PIN_O_NBRI=2
        self.PIN_O_NHUE=3
        self.PIN_O_NSAT=4
        self.PIN_O_NREACHABLE=5
        self.PIN_O_NGRPJSON=6
        self.PIN_O_NLGHTSJSON=7
        self.FRAMEWORK._run_in_context_thread(self.on_init)

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##

    # get general web request
    def getData(self, api_url, api_port, api_user, api_cmd):
        api_path = '/api/' + api_user + '/' + api_cmd
        data = ""

        try:
            httpClient = httplib.HTTPConnection(api_url, int(api_port), timeout=5)
            httpClient.request("GET", api_path)
            response = httpClient.getresponse()
            status = response.status
            data = {'data' : response.read(), 'status' : status}
            self.DEBUG.set_value("Response code", status)
        except Exception as e:
            print(e)
            return
        finally:
            if httpClient:
                httpClient.close()

        return data

    # read light data from json
    def readLightsJson(self, jsonState, light):
        try:
            jsonState = json.loads(jsonState)

            if str(light) in jsonState:
                if 'state' in jsonState[str(light)]:
                    if 'reachable' in jsonState[str(light)]['action']:
                        bReachable = jsonState[str(light)]['state']['reachable']
                        self._set_output_value(self.PIN_O_NREACHABLE, bReachable)
        except:
            jsonState = []

        return json.dumps(jsonState)

    def readGroupsJson(self, jsonState, group):
        try:
            jsonState = json.loads(jsonState)
            
            if str(group) in jsonState:
                if 'action' in jsonState[str(group)]:
                    actionSub = jsonState[str(group)]["action"]
                    bOnOff = actionSub['on']
                    self._set_output_value(self.PIN_O_BSTATUSONOFF, bOnOff)

                    if 'bri' in actionSub:
                        nBri = int(actionSub['bri'] / 254.0 * 100)
                        self._set_output_value(self.PIN_O_NBRI, nBri)
                    if 'hue' in actionSub:
                        nHue = actionSub['hue']
                        self._set_output_value(self.PIN_O_NHUE, nHue)
                    if 'sat' in actionSub:
                        nSat = actionSub['sat']
                        self._set_output_value(self.PIN_O_NSAT, nSat)
        except:
            jsonState = []

        return json.dumps(jsonState)

    def httpPut(self, api_url, api_port, api_user, group, payload):
        httpClient = None
        try:
            api_path = '/api/' + api_user + '/groups/' + str(group) + '/action'
            headers = { "HOST": str(api_url + ":" + str(api_port)), "CONTENT-LENGTH": str(len(payload)), "Content-type": 'application/json' }
            #headers = { "Content-type": 'application/json' }            
            httpClient = httplib.HTTPConnection(api_url, int(api_port), timeout=5)
            httpClient.request("PUT", api_path, payload, headers) 
            response = httpClient.getresponse()
            status = response.status
            #data = {'data' : response.read(), 'status' : status}
            #print data
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            if httpClient:
                httpClient.close()
                
    def hueOnOff(self, api_url, api_port, api_user, group, bSetOn):
        payload = ""
        if bSetOn == True:
            payload = '{"on":true}'
        else:
            payload = '{"on":false}'
            
        ret = self.httpPut(api_url, api_port, api_user, group, payload)
        return ret
        
    def setScene(self, api_url, api_port, api_user, group, sScene):
        payload = '{"scene":"' + sScene + '"}'
        ret = self.httpPut(api_url, api_port, api_user, group, payload)
        return ret        
        
    def setBri(self, api_url, api_port, api_user, group, nBri):
        payload = '{"bri":' + str(nBri) + '}'
        ret = self.httpPut(api_url, api_port, api_user, group, payload)
        return ret
    
    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()
    
    def on_input_value(self, index, value):
        res = False

        # Process State
        sApi_url = str(self._get_input_value(self.PIN_I_SHUEIP))
        nApi_port = int(self._get_input_value(self.PIN_I_NHUEPORT))
        sApi_user = str(self._get_input_value(self.PIN_I_SUSER))
        group = int(self._get_input_value(self.PIN_I_NGROUP))
        light = int(self._get_input_value(self.PIN_I_NLIGHT))
        hueGroupState = {"data" : str(self._get_input_value(self.PIN_I_SGROUPSTATJSON)), "status" : 200}
        hueLightState = {"data" : str(self._get_input_value(self.PIN_I_SLIGHTSSTATJSON)), "status"  :200}
        nBri = int(self._get_input_value(self.PIN_I_NBRI) / 100.0 * 254)

        #### If trigger == 1, get data via web request
        if (self.PIN_I_BTRIGGER == index) and (bool(value)):
            hueGroupState = self.getData(sApi_url, nApi_port, sApi_user, "groups")
            hueLightState = self.getData(sApi_url, nApi_port, sApi_user, "lights")

            self.DEBUG.set_value("grp json", hueGroupState)
            self.DEBUG.set_value("lght json", hueLightState)

        if (hueGroupState["data"]):
            if (group > 0):
                self.readGroupsJson(hueGroupState["data"], group)
            self._set_output_value(self.PIN_O_NGRPJSON, hueGroupState["data"])

        if (hueLightState["data"]):
            if (light > 0):
                self.readLightsJson(hueLightState["data"], light)
            self._set_output_value(self.PIN_O_NLGHTSJSON, hueLightState["data"])

        #### Process set commands
        if (self._get_input_value(self.PIN_I_SUSER) == "") or (self._get_input_value(self.PIN_I_SHUEIP) == ""):
            return

        if self.PIN_I_BONOFF == index:
            res = self.hueOnOff(sApi_url, nApi_port, sApi_user, group, value)
            if (res):
                self._set_output_value(self.PIN_O_BSTATUSONOFF, value)

        if self.PIN_I_SSCENE == index:
            res = self.setScene(sApi_url, nApi_port, sApi_user, group, value)
            if (res):
                self._set_output_value(self.PIN_O_BSTATUSONOFF, True)

        if self.PIN_I_NBRI == index :
            res = self.setBri(sApi_url, nApi_port, sApi_user, group, nBri)
            if (res):
                self._set_output_value(self.PIN_O_NBRI, nBri)

