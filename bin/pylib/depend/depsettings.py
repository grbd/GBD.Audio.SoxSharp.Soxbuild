﻿"""
Represents the Depend settings
"""

# Always try to import cElementTree since it's faster if it exists
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import platform
from os.path import join, abspath, exists
from pylib.logwrapper import LogWrapper
from pylib.depend.depsource import DepSource

# XML Settings for Download of Depends
class DependSettings(object):

    def __init__(self):
        """Dependency Settings"""
        super().__init__()
        self.log = LogWrapper.getlogger()

        # Path to the config file
        self.ConfigPath = None
        self.platform = None

        # XML Root Tag
        self.xmlroot = None

        # custom properties
        self.DepsDirectory = None
        self.ArchiveDirectory = None
        self.SoxVersion = None
        self.CMakeGenerator = None

        # List of Sources
        self.sources = []

    def read_element(self, tag):
        """Read XML Value Element"""
        nextval = next(self.xmlroot.iter(tag), None)
        if nextval == None : raise ValueError('Element not found: ' + tag)
        return nextval.text

    def loadxml(self):
        """Load XML"""
        # Load in the xml
        tree = ET.ElementTree(file=self.ConfigPath)
        self.xmlroot = tree.getroot()
        if self.xmlroot.tag != 'Settings':
            raise ValueError('Root Element is not Settings')

        # Custom Settings
        self.DepsDirectory = self.read_element('DepsDirectory')
        self.DepsDirectory = abspath(self.DepsDirectory)
        self.ArchiveDirectory = self.read_element('ArchiveDirectory')
        self.ArchiveDirectory = join(self.DepsDirectory, self.ArchiveDirectory)
        self.SoxVersion = self.read_element('SoxVersion')
        self.CMakeGenerator = self.read_element('CMakeGenerator')

        # Set the Archive directory for downloaded sources
        DepSource.ArchiveDir = self.ArchiveDirectory
        # Set the root Extract directory for extracting sources
        DepSource.RootExtractDir = self.DepsDirectory

        # Load in the list of download sources
        self.sources = DepSource.parsexml(self.xmlroot)
        return

    def getdeps(self):
        """Download and Extract Sources"""
        for source in self.sources:
            self.log.info("")
            self.log.info("#####################################################")

            # Skip anything already extracted
            extractdir = abspath(join(DepSource.RootExtractDir, source.destsubdir))
            if exists(extractdir):
                self.log.warn("Deps Subdir: " + source.destsubdir + " already exists, skipping")
                continue

            source.Extracted = False
            downloaded = source.download()
            if downloaded == False:
                self.log.error("Download Failed")
            else:
                source.Extracted = source.extract()

            # Remove the archive file
            source.remove_archivefile()

        # Re-jig the directories for those that need it
        for source in self.sources:
            if source.Extracted == True:
                source.movetoparent_multiple()
        return

    def get_configpath(self):
        log = LogWrapper.getlogger()
        """Determine which config filename / path to use"""
        self.platform = platform.system()
        settingsfile = ""
        if self.platform == "Windows":
           settingsfile = "Settings_win32.xml"
        elif self.platform == "Linux":
            settingsfile = "Settings_linux.xml"
        else:
            log.critical("Unsupported platform")
            self.ConfigPath = None
        self.log.info("Platform identified as: " + self.platform)
        self.log.info("Settings file: " + settingsfile)
        self.ConfigPath = abspath(settingsfile)
        return self.ConfigPath
