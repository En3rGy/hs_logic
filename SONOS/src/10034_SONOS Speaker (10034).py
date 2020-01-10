# coding: UTF-8
import httplib

##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class SONOSSpeaker_10034_10034(hsl20_3.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_3.BaseModule.__init__(self, homeserver_context, "hsl20_3_SonosSpeaker")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_3.LOGGING_NONE,())
        self.PIN_I_SSPEAKERIP=1
        self.PIN_I_NSPEAKERPORT=2
        self.PIN_I_NVOLUME=3
        self.PIN_I_BPLAY=4
        self.PIN_I_BPAUSE=5
        self.PIN_I_BPREVIOUS=6
        self.PIN_I_BNEXT=7
        self.PIN_I_SPLAYLIST=8
        self.PIN_I_SRADIO=9
        self.PIN_I_SJOINRINCON=10
        self.PIN_O_SOUT=1
        self.FRAMEWORK._run_in_context_thread(self.on_init)

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##

    def httpPut(self, api_url, api_port, api_path, api_action, payload):
        httpClient = None
        try:
            headers = {"CONNECTION": "close", "HOST": str(api_url + ":" + str(api_port)), "CONTENT-LENGTH": str(len(payload)), "Content-type": 'text/xml; charset="utf-8"', "SOAPACTION": api_action}
            httpClient = httplib.HTTPConnection(api_url, int(api_port), timeout=5)
            httpClient.request("POST", api_path, payload, headers)
            response = httpClient.getresponse()
            status = response.status
            self.DEBUG.set_value('data', response.read())
            self.DEBUG.set_value('status', status)
            if str(status) != '200':
                return False
            else:
                return True
        except Exception as e:
            print(e)
            #data = {'status':500,'auth':'failed'}
            return False
        finally:
            if httpClient:
                httpClient.close()

    def setMute(self, api_url, api_port, bSetMute):
        api_action = '"urn:schemas-upnp-org:service:RenderingControl:1#SetMute"'
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetMute xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><Channel>Master</Channel><DesiredMute>' + str(int(bSetMute)) + '</DesiredMute></u:SetMute></s:Body></s:Envelope>'
        return self.httpPut(api_url, api_port, "/MediaRenderer/AVTransport/Control HTTP/1.1", api_action, data)

    def clearQueue(self, api_url, api_port):
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#RemoveAllTracksFromQueue"'
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:RemoveAllTracksFromQueue xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID></u:RemoveAllTracksFromQueue></s:Body></s:Envelope>'
        return self.httpPut(api_url, api_port, "/MediaRenderer/AVTransport/Control HTTP/1.1", api_action, data)

    def selectFstTrack(self, api_url, api_port):
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#Seek"'
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:Seek xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Unit>TRACK_NR</Unit><Target>1</Target></u:Seek></s:Body></s:Envelope>'
        return self.httpPut(api_url, api_port, "/MediaRenderer/AVTransport/Control HTTP/1.1", api_action, data)

    def setPlaylistActive(self, api_url, api_port):
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI"'
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><CurrentURI>x-rincon-queue:RINCON_949F3E6D215901400#0</CurrentURI><CurrentURIMetaData></CurrentURIMetaData></u:SetAVTransportURI></s:Body></s:Envelope>'
        return self.httpPut(api_url, api_port, "/MediaRenderer/AVTransport/Control HTTP/1.1", api_action, data)

    # Playlist Children
    def setPlaylist(self, api_url, api_port, data):
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#AddURIToQueue"'
        strList = str.split(data, "*")

        if len(strList) != 2:
            return False

        #data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:AddURIToQueue xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><EnqueuedURI>x-rincon-playlist:RINCON_949F3E71146601400#A:GENRE/Children&apos;s</EnqueuedURI><EnqueuedURIMetaData>&lt;DIDL-Lite xmlns:dc=&quot;http://purl.org/dc/elements/1.1/&quot; xmlns:upnp=&quot;urn:schemas-upnp-org:metadata-1-0/upnp/&quot; xmlns:r=&quot;urn:schemas-rinconnetworks-com:metadata-1-0/&quot; xmlns=&quot;urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/&quot;&gt;&lt;item id=&quot;A:GENRE/Children&amp;apos;s&quot; parentID=&quot;A:GENRE&quot; restricted=&quot;true&quot;&gt;&lt;dc:title&gt;Children&amp;apos;s&lt;/dc:title&gt;&lt;upnp:class&gt;object.container.genre.musicGenre.sonos-favorite&lt;/upnp:class&gt;&lt;desc id=&quot;cdudn&quot; nameSpace=&quot;urn:schemas-rinconnetworks-com:metadata-1-0/&quot;&gt;RINCON_AssociatedZPUDN&lt;/desc&gt;&lt;/item&gt;&lt;/DIDL-Lite&gt;</EnqueuedURIMetaData><DesiredFirstTrackNumberEnqueued>1</DesiredFirstTrackNumberEnqueued><EnqueueAsNext>1</EnqueueAsNext></u:AddURIToQueue></s:Body></s:Envelope>'
        data2 = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:AddURIToQueue xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><EnqueuedURI>' + strList[0] + '</EnqueuedURI><EnqueuedURIMetaData>' + strList[1] + '</EnqueuedURIMetaData><DesiredFirstTrackNumberEnqueued>1</DesiredFirstTrackNumberEnqueued><EnqueueAsNext>1</EnqueueAsNext></u:AddURIToQueue></s:Body></s:Envelope>'

        return self.httpPut(api_url, api_port, "/MediaRenderer/AVTransport/Control HTTP/1.1", api_action, data2)

    def setPlayModeShuffleNoRepeat(self, api_url, api_port):
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#SetPlayMode"'
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetPlayMode xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><NewPlayMode>SHUFFLE_NOREPEAT</NewPlayMode></u:SetPlayMode></s:Body></s:Envelope>'
        return self.httpPut(api_url, api_port, "/MediaRenderer/AVTransport/Control HTTP/1.1", api_action, data)

    def play(self, api_url, api_port):
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#Play"'
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:Play xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Speed>1</Speed></u:Play></s:Body></s:Envelope>'
        return self.httpPut(api_url, api_port, "/MediaRenderer/AVTransport/Control HTTP/1.1", api_action, data)

    def playNext(self, api_url, api_port):
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#Next"'
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:Next xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID></u:Next></s:Body></s:Envelope>'
        return self.httpPut(api_url, api_port, "/MediaRenderer/AVTransport/Control HTTP/1.1", api_action, data)

    def playPrevious(self, api_url, api_port):
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#Previous"'
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:Previous xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID></u:Previous></s:Body></s:Envelope>'
        return self.httpPut(self, api_url, api_port, "/MediaRenderer/AVTransport/Control HTTP/1.1", api_action, data)

    def pause(self, api_url, api_port):
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#Pause"'
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:Pause xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID></u:Pause></s:Body></s:Envelope>'
        return self.httpPut(api_url, api_port, "/MediaRenderer/AVTransport/Control HTTP/1.1", api_action, data)

    def setVolume(self, api_url, api_port, nVolume):
        api_action = '"urn:schemas-upnp-org:service:RenderingControl:1#SetVolume"'
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetVolume xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><Channel>Master</Channel><DesiredVolume>' + str(nVolume) + '</DesiredVolume></u:SetVolume></s:Body></s:Envelope>'
        return self.httpPut(api_url, api_port, "/MediaRenderer/RenderingControl/Control HTTP/1.1", api_action, data)

    def playRadio(self, api_url, api_port, data):
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI"'
        strList = str.split(data, "*")

        if len(strList) != 2:
            return False

        data2 = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><CurrentURI>' + strList[0] + '</CurrentURI><CurrentURIMetaData>' + strList[1] + '</CurrentURIMetaData></u:SetAVTransportURI></s:Body></s:Envelope>'

        ret = self.httpPut(api_url, api_port, "/MediaRenderer/AVTransport/Control HTTP/1.1", api_action, data2)

        if ret == True:
            return self.play(api_url, api_port)

    def playPlaylist(self, api_url, api_port, data):
        ret = self.clearQueue(api_url, api_port)
        if ret == False:
            return False

        ret = self.setPlaylist(api_url, api_port, data)
        if ret == False:
            return False

        ret = self.setPlaylistActive(api_url, api_port)
        if ret == False:
            return False

        ret = self.setPlayModeShuffleNoRepeat(api_url, api_port)
        if ret == False:
            return False

        ret = self.selectFstTrack(api_url, api_port)
        if ret == False:
            return False

        return self.play(api_url, api_port)

    def joinRincon(self, api_url, api_port, rincon):
        # SOAPACTION: "urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI"
        #<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><CurrentURI>x-rincon:RINCON_949F3E6D215901400</CurrentURI><CurrentURIMetaData></CurrentURIMetaData></u:SetAVTransportURI></s:Body></s:Envelope>
        api_action = '"urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI"'
        data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><CurrentURI>x-rincon:RINCON_' + rincon + '</CurrentURI><CurrentURIMetaData></CurrentURIMetaData></u:SetAVTransportURI></s:Body></s:Envelope>'
        return self.httpPut(api_url, api_port, "/MediaRenderer/AVTransport/Control HTTP/1.1", api_action, data)

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()

    def on_input_value(self, index, value):

        sIp   = self._get_input_value(self.PIN_I_SSPEAKERIP)
        nPort = self._get_input_value(self.PIN_I_NSPEAKERPORT)
        res   = False

        if (sIp == "") or (nPort == 0):
            self._set_output_value(self.PIN_O_SOUT, "IP or Port not set.")
            return 

        if (index == self.PIN_I_BNEXT) and (bool(value)):
            res = self.playNext(sIp, nPort)

        elif (index == self.PIN_I_BPAUSE) and (bool(value)):
            res = self.pause(sIp, nPort)

        elif (index == self.PIN_I_BPLAY) and (bool(value)):
            res = self.play(sIp, nPort)

        elif (index == self.PIN_I_BPREVIOUS) and (bool(value)):
            res = self.playPrevious(sIp, nPort)

        elif (index == self.PIN_I_SPLAYLIST) and (bool(value)):
            res = self.playPlaylist(sIp, nPort, self._get_input_value(self.PIN_I_SPLAYLIST))

        elif (index == self.PIN_I_SRADIO) and (bool(value)):
            res = self.playRadio(sIp, nPort, self._get_input_value(self.PIN_I_SRADIO))

        elif (index == self.PIN_I_NVOLUME):
            res = self.setVolume(sIp, nPort, value)

        elif (index == self.PIN_I_SJOINRINCON):
            res = self.joinRincon(sIp, nPort, self._get_input_value(self.PIN_I_SJOINRINCON))

        self.DEBUG.set_value("Result", res) 
