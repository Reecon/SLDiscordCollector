#---------------------------
#   Import Libraries
#---------------------------
import os
import codecs
import sys
import json

import clr
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

#---------------------------
#   [Required] Script Information
#---------------------------
ScriptName = "DiscordCollector"
Website = "reecon820@gmail.com"
Description = "Allows a Twitch chat command to post to discord"
Creator = "Reecon820"
Version = "0.0.0.1"

#---------------------------
#   Settings Handling
#---------------------------
class DcSettings:
    def __init__(self, settingsfile=None):
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
                self.__dict__ = json.load(f, encoding="utf-8")
        except:
            self.Cooldown = 0
            self.Permission = "everyone"
            self.Info = ""
            self.Command = "!suggest"

    def Reload(self, jsondata):
        self.__dict__ = json.loads(jsondata, encoding="utf-8")

    def Save(self, settingsfile):
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="w+") as f:
                json.dump(self.__dict__, f, encoding="utf-8")
            with codecs.open(settingsfile.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
                f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8')))
        except:
            Parent.Log(ScriptName, "Failed to save settings to file.")


#---------------------------
#   Define Global Variables
#---------------------------
dcSettingsFile = ""
dcScriptSettings = DcSettings()

#---------------------------
#   [Required] Initialize Data (Only called on load)
#---------------------------
def Init():
  
    #   Create Settings Directory
    directory = os.path.join(os.path.dirname(__file__), "Settings")
    if not os.path.exists(directory):
        os.makedirs(directory)

    #   Load settings
    global dcSettingsFile
    dcSettingsFile = os.path.join(os.path.dirname(__file__), "Settings\settings.json")
    global dcScriptSettings
    dcScriptSettings = DcSettings(dcSettingsFile)
    
    updateUi()

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):
    #   only handle messages from chat
    if data.IsChatMessage() and data.IsFromTwitch() and not data.IsWhisper() and not Parent.IsOnCooldown(ScriptName, dcScriptSettings.Command) and Parent.HasPermission(data.User, dcScriptSettings.Permission, dcScriptSettings.Info):
        
        isCommand = data.GetParam(0).lower() == dcScriptSettings.Command
        if isCommand and data.GetParam(1):
            message = " ".join(data.Message.split(" ")[1:])
            Parent.SendDiscordMessage("{0} suggests {1}".format(data.UserName, message))
            Parent.AddCooldown(ScriptName, dcScriptSettings.Command, dcScriptSettings.Cooldown)  # Put the command on cooldown

#---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
#---------------------------
def Tick():
    return

#---------------------------
#   [Optional] Parse method (Allows you to create your own custom $parameters) 
#---------------------------
def Parse(parseString, username, message):
    return parseString

#---------------------------
#   [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI)
#---------------------------
def ReloadSettings(jsonData):
    # Execute json reloading here
    dcScriptSettings.Reload(jsonData)
    dcScriptSettings.Save(dcSettingsFile)
    updateUi()
    return

#---------------------------
#   [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff)
#---------------------------
def Unload():
    return

#---------------------------
#   [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
#---------------------------
def ScriptToggled(state):
    return

def updateUi():
    ui = {}
    UiFilePath = os.path.join(os.path.dirname(__file__), "UI_Config.json")
    try:
        with codecs.open(UiFilePath, encoding="utf-8-sig", mode="r") as f:
            ui = json.load(f, encoding="utf-8")
    except Exception as err:
        Parent.Log(ScriptName, "{0}".format(err))

    # update ui with loaded settings
    ui['Cooldown']['value'] = dcScriptSettings.Cooldown
    ui['Permission']['value'] = dcScriptSettings.Permission
    ui['Info']['value'] = dcScriptSettings.Info
    ui['Command']['value'] = dcScriptSettings.Command

    try:
        with codecs.open(UiFilePath, encoding="utf-8-sig", mode="w+") as f:
            json.dump(ui, f, encoding="utf-8", indent=4, sort_keys=True)
    except Exception as err:
        Parent.Log(ScriptName, "{0}".format(err))
