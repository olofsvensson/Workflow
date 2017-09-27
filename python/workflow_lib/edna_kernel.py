# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

_authors__ = ["Olof Svensson"]
__license__ = "MIT"
__date__ = "27/09/2017"

"""
Workflow library module for running EDNA plugins
"""

import os
import sys
import time
import socket
import tempfile

from workflow_lib import path
from workflow_lib import workflow_logging

# sys.path.insert(0, "/opt/pxsoft/EDNA/vGIT/edna/kernel/src")
sys.path.insert(0, "/opt/pxsoft/EDNA/vMX/edna/kernel/src")

from EDVerbose import EDVerbose
from EDFactoryPluginStatic import EDFactoryPluginStatic

from XSDataCommon import XSDataString
from XSDataCommon import XSDataImage
from XSDataCommon import XSDataFile
from XSDataCommon import XSDataInteger
from XSDataCommon import XSDataVectorDouble

EDFactoryPluginStatic.loadModule("markupv1_10")
import markupv1_10

# Init simulation
def initSimulation(beamline):
    logger = workflow_logging.getLogger()
    if beamline.startswith("simulator") or beamline == "id30a2":
        logger.debug("Setting EDNA site to ESRF_ISPyBTest in order to use ISPyB validation server.")
        from EDUtilsPath import EDUtilsPath
        EDUtilsPath.setEdnaSite("ESRF_ISPyBTest")
        os.environ["EDNA_SITE"] = "ESRF_ISPyBTest"
#        EDVerbose.setVerboseDebugOn()
# EDNA base directory
def getEdnaBaseDirectory(directory):
    logger = workflow_logging.getLogger()
    strPluginBaseDir = path.createWorkflowWorkingDirectory(directory)
    logger.debug("EDNA base directory: %s" % strPluginBaseDir)
    os.chdir(strPluginBaseDir)
    return strPluginBaseDir


def executeEdnaPluginAsynchronous(strPluginName, xsDataInput, workflow_working_dir, timeout=None):
    logger = workflow_logging.getLogger()
    user = None
    try:
        user = path.extractBeamlineFromDirectory(workflow_working_dir)
    except:
        logger.debug("Cannot determine beamline from path {0}".format(workflow_working_dir))
    if user is None:
        user = os.environ["USER"]
    if workflow_working_dir is None:
        workflow_working_dir = path.createWorkflowWorkingDirectory()
    elif not os.path.exists(workflow_working_dir):
        if "RAW_DATA" in workflow_working_dir:
            workflow_working_dir = workflow_working_dir.replace("RAW_DATA", "PROCESSED_DATA")
            # Try to get beamline from path
            user = path.extractBeamlineFromDirectory(workflow_working_dir)
        os.makedirs(workflow_working_dir, 0755)
    logger.debug("Executing EDNA plugin %s" % strPluginName)
    logger.debug("EDNA_SITE %s" % os.environ["EDNA_SITE"])
    # strPluginBaseDir = workflow_working_dir
    strDate = time.strftime("%Y%m%d", time.localtime(time.time()))
    strTime = time.strftime("%H%M%S", time.localtime(time.time()))
    strPluginBaseDir = os.path.join("/tmp_14_days", user, strDate)
    if not os.path.exists(strPluginBaseDir):
        try:
            os.makedirs(strPluginBaseDir, 0755)
        except OSError as e:
            logger.warning("Error when trying to create directory: {0}".format(strPluginBaseDir))
            logger.warning("Error message: {0}".format(e))
            time.sleep(1)
            if not os.path.exists(strPluginBaseDir):
                raise BaseException("Cannot create directory: {0}".format(strPluginBaseDir))
    strEDNAWorkDir = tempfile.mkdtemp(prefix=strTime + "_" + strPluginName.replace("EDPlugin", "") + "_", dir=strPluginBaseDir)
    logger.debug("EDNA plugin working directory: %s" % strEDNAWorkDir)
    os.chmod(strEDNAWorkDir, 0755)
    ednaBaseName = os.path.basename(strEDNAWorkDir)
    ednaLogName = "{0}.log".format(ednaBaseName)
    ednaLogPath = os.path.join(workflow_working_dir, ednaLogName)
    EDVerbose.setLogFileName(ednaLogPath)
    EDVerbose.setVerboseOn()
    # Create link
    hostname = socket.gethostname()
    linkName = "{hostname}_{dir}".format(hostname=hostname, dir=os.path.basename(strEDNAWorkDir))
    os.symlink(strEDNAWorkDir, os.path.join(workflow_working_dir, linkName))
    # Load plugin
    edPlugin = EDFactoryPluginStatic.loadPlugin(strPluginName)
    edPlugin.setDataInput(xsDataInput)
    edPlugin.setBaseDirectory(strPluginBaseDir)
    edPlugin.setBaseName(ednaBaseName)
    if timeout is not None:
        edPlugin.setTimeOut(timeout)
        logger.debug("Timeout set to %f s" % timeout)
    logger.debug("Start of execution of EDNA plugin %s" % strPluginName)
    edPlugin.execute()
    return edPlugin, ednaLogPath


def synchronizeEdnaPlugin(edPlugin, bLogExecutiveSummary=False):
    logger = workflow_logging.getLogger()
    edPlugin.synchronize()
    logger.debug("EDNA plugin %s executed" % edPlugin.getPluginName())
    if bLogExecutiveSummary:
        for line in edPlugin.getListExecutiveSummaryLines():
            logger.info(line)
    xsDataResult = edPlugin.dataOutput
    logger.debug("XSDataResult type: %s" % type(xsDataResult))
    return xsDataResult


def executeEdnaPlugin(strPluginName, xsDataInput, workflow_working_dir, bLogExecutiveSummary=False):
    edPlugin, ednaLogPath = executeEdnaPluginAsynchronous(strPluginName, xsDataInput, workflow_working_dir)
    xsDataResult = synchronizeEdnaPlugin(edPlugin, bLogExecutiveSummary)
    return xsDataResult, ednaLogPath

