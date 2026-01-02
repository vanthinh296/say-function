# coding=UTF-8
# say function.py
# A simple NVDA add-on that notifies you when you press CTRL+c, CTRL+v, CTRL+x, CTRL+z, CTRL+y, CTRL+a.
# Author: Smart Thinh Production
# Copyright 2025

import globalPluginHandler
from ui import message
import addonHandler
import scriptHandler
import api
import inputCore
from scriptHandler import script
import tones
import os
import sys
import gui
import wx
import config
import globalVars

try:
    import winsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

addonHandler.initTranslation()

addonName = "sayFunction"
config.conf.spec[addonName] = {
    "playSounds": "boolean(default=False)"
}

class SayFunctionSettingsPanel(gui.SettingsPanel):
    title = _("Say Function")

    def makeSettings(self, settingsSizer):
        sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
        
        self.playSoundsCheckbox = sHelper.addItem(
            wx.CheckBox(self, label=_("Play different sound effects when performing keyboard shortcuts"))
        )
        self.playSoundsCheckbox.SetValue(config.conf[addonName]["playSounds"])
        
        if not SOUND_AVAILABLE and not PYGAME_AVAILABLE:
            soundInfo = sHelper.addItem(
                wx.StaticText(self, label=_("Note: Sound libraries not available. Only tone beeps will work."))
            )

    def onSave(self):
        config.conf[addonName]["playSounds"] = self.playSoundsCheckbox.GetValue()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

    def __init__(self):
        super(GlobalPlugin, self).__init__()
        if PYGAME_AVAILABLE:
            pygame.mixer.init()
        
        if not globalVars.appArgs.secure:
            gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(SayFunctionSettingsPanel)

    def terminate(self):
        if not globalVars.appArgs.secure:
            try:
                gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(SayFunctionSettingsPanel)
            except ValueError:
                pass
        super(GlobalPlugin, self).terminate()

    def play_sound(self, sound_type):
        if not config.conf[addonName]["playSounds"]:
            return
            
        try:
            if sound_type == "copy":
                tones.beep(1000, 100)
            elif sound_type == "paste":
                tones.beep(800, 100)
            elif sound_type == "cut":
                tones.beep(600, 100)
            elif sound_type == "undo":
                tones.beep(900, 80)
                tones.beep(700, 80)
            elif sound_type == "redo":
                tones.beep(700, 80)
                tones.beep(900, 80)
            elif sound_type == "select_all":
                tones.beep(500, 200)
            
            elif SOUND_AVAILABLE:
                frequencies = {
                    "copy": 1000,
                    "paste": 800, 
                    "cut": 600,
                    "undo": 900,
                    "redo": 700,
                    "select_all": 500
                }
                winsound.Beep(frequencies.get(sound_type, 1000), 100)
                
        except Exception as e:
            pass

    def process_input(self, gesture):
        """Process the input gesture and execute it if handled elsewhere"""
        scripts = []
        maps = [inputCore.manager.userGestureMap, inputCore.manager.localeGestureMap]
        
        for map in maps:
            for identifier in gesture.identifiers:
                scripts.extend(map.getScriptsForGesture(identifier))
        
        focus = api.getFocusObject()
        tree = focus.treeInterceptor
        
        if tree and tree.isReady:
            func = scriptHandler._getObjScript(tree, gesture, scripts)
            if func and (not tree.passThrough or getattr(func, "ignoreTreeInterceptorPassThrough", False)):
                func(tree)
                return True
        
        gesture.send()
        return False

    @script(
        description=_("Copy selected item"),
        gesture="kb:control+c"
    )
    def script_announceCopy(self, gesture):
        self.process_input(gesture)
        message(_("Copy"))
        self.play_sound("copy")

    @script(
        description=_("Pasted item"), 
        gesture="kb:control+v"
    )
    def script_announcePasted(self, gesture):
        self.process_input(gesture)
        message(_("Pasted"))
        self.play_sound("paste")

    @script(
        description=_("Cut selected item"),
        gesture="kb:control+x"
    )
    def script_announceCut(self, gesture):
        self.process_input(gesture)
        message(_("Cut"))
        self.play_sound("cut")

    @script(
        description=_("Undo operation"),
        gesture="kb:control+z"
    )
    def script_announceUndo(self, gesture):
        self.process_input(gesture)
        message(_("Undo"))
        self.play_sound("undo")

    @script(
        description=_("Redo operation"),
        gesture="kb:control+y"
    )
    def script_announceRedo(self, gesture):
        self.process_input(gesture)
        message(_("Redo"))
        self.play_sound("redo")

    @script(
        description=_("Select all"),
        gesture="kb:control+a"
    )
    def script_announceSelectAll(self, gesture):
        self.process_input(gesture)
        message(_("Select all"))
        self.play_sound("select_all")


if globalVars.appArgs.secure:
    GlobalPlugin = globalPluginHandler.GlobalPlugin