﻿"""
Class for generating required cmake files
"""

import shutil, subprocess, os
from pylib.logwrapper import LogWrapper
from pylib.cmake.cmake_process import CMakeProcess
from pylib.depend.depsettings import DependSettings
from os.path import abspath, dirname, join

# Wrapper class for cmake
class CMakeGen(object):

    # Class Constructor
    def __init__(self, Setts):
        self.log = LogWrapper.getlogger()
        self.Setts = Setts

        # Directory properties
        self.PackagesDir = abspath(join(self.Setts.DepsDirectory, "packages"))
        self.PatchedDir = abspath(join(self.Setts.DepsDirectory, "patched"))
        self.SrcDir = abspath(join(self.Setts.DepsDirectory, "..", "src"))

    # Get the generator based on platform
    def getgenerator(self):
        ret = None
        if self.Setts.platform == "Windows":
            ret = "Visual Studio 12 2013"
            # There are currently issues with the newer libs included with VS2015 for libsox
            # http://stackoverflow.com/questions/31150635/build-error-in-visual-studio-in-perlio-h-and-iobuf
            #cmakeproc.Generator = "Visual Studio 14 2015"
        elif self.Setts.platform == "Linux":
            log.error("Not yet implemented")
            sys.exit(1)
        else:
            log.error("Unsupported Platform")
            sys.exit(1)
        return ret

    # Start the CMake Generation
    def Start(self):
        if self.Setts.CMakeGenerator == None: self.Setts.CMakeGenerator = self.getgenerator()
        self.CMake_Zlib()
        self.CMake_LibSox()

    def CMake_Zlib(self):
        # Run cmake for zlib, this is needed for libpng
        cmakeproc = CMakeProcess()
        cmakeproc.WorkingDir = join(self.Setts.DepsDirectory, "cmake", "zlib")
        cmakeproc.SrcDir = join(self.Setts.DepsDirectory, "patched", "zlib")
        cmakeproc.Generator = self.Setts.CMakeGenerator
        cmakeproc.SetupOutputDir()
        cmakeproc.Start()

    def CMake_LibSox(self):
        # Run cmake for libsox
        cmakeproc = CMakeProcess()
        cmakeproc.WorkingDir = join(self.Setts.DepsDirectory, "cmake", "sox")
        cmakeproc.SrcDir = join(self.Setts.DepsDirectory, "patched", "sox")
        cmakeproc.Generator = self.Setts.CMakeGenerator
        cmakeproc.SetupOutputDir()

        # Copy over needed files for cmake
        sox_cmakefile = join(self.SrcDir, "sox-" + self.Setts.SoxVersion, "cmake", "libsox", "soxconfig.h.cmake")
        shutil.copy(sox_cmakefile, cmakeproc.WorkingDir)

        cmakeproc.Start()