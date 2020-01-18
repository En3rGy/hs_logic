# coding: UTF-8
import json

##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class JSON_Parser_11087_11087(hsl20_3.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_3.BaseModule.__init__(self, homeserver_context, "hsl20_3_json")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_3.LOGGING_NONE,())
        self.PIN_I_SJSON=1
        self.PIN_I_SKEY=2
        self.PIN_I_SIDX=3
        self.PIN_O_SVALUE=1
        self.PIN_O_FVALUE=2
        self.FRAMEWORK._run_in_context_thread(self.on_init)

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##

    def getListElement(self, sJson, nIndex ):
        jsonFile = json.loads(sJson)

        if isinstance(jsonFile, list):
            if (nIndex<len(jsonFile)):
                return json.dumps(jsonFile[nIndex])

        return "{}"

    def getValue(self, sJson, sKey ):
        jsonFile = json.loads(sJson)
        ret = ""
        if sKey in jsonFile:
            val = jsonFile[sKey]

            if (isinstance( val, dict) 
                or isinstance( val, list)):
                ret = json.dumps(val)
            else:
                ret = val
        else:
            self.DEBUG.add_message("Error: Key not found.")

        if isinstance(ret, str):
            ret = ret.encode("ascii", "xmlcharrefreplace")

        return ret

    def on_init(self):
        self.DEBUG = self.FRAMEWORK.create_debug_section()

    def on_input_value(self, index, value):
        #self.DEBUG.set_value("Response code", status)
        #self.DEBUG.add_message("Error connecting to www.dwd.de: " + str(e))
        sJson = self._get_input_value(self.PIN_I_SJSON)
        sKey = self._get_input_value(self.PIN_I_SKEY)
        nIdx = self._get_input_value(self.PIN_I_SIDX)

        val = ""

        if( nIdx >= 0 ):
            val = self.getListElement(sJson, nIdx)
        else:
            val = self.getValue(sJson, sKey)

        # handle unicode representation
        if isinstance(val, str):
            val = val.replace( "u'", '"' )
            val = val.replace( "'", '"' )
            val = val.replace( ": False", ': false' )
            val = val.replace( ": True", ': true' )

        self._set_output_value(self.PIN_O_SVALUE, str(val))

        #converting a not-number-string to float causes an exception
        try:
            self._set_output_value(self.PIN_O_FVALUE, float(val))
        except Exception as e:
            self.DEBUG.add_message("Error converting '" + str(val) + "' to float: " + str(e))

