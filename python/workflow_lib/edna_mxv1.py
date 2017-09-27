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

"""
Workflow library module for running EDNA MX plugins
"""

__authors__ = ["Olof Svensson"]
__license__ = "MIT"
__date__ = "27/09/2017"

import os
import time
import tempfile
import subprocess

from workflow_lib import edna_kernel
from workflow_lib import workflow_logging

from edna_kernel import EDFactoryPluginStatic

from XSDataCommon import XSDataString
from XSDataCommon import XSDataImage
from XSDataCommon import XSDataFile
from XSDataCommon import XSDataInteger
from XSDataCommon import XSDataDouble
from XSDataCommon import XSDataFile
from XSDataCommon import XSDataTime
from XSDataCommon import XSDataAngularSpeed
from XSDataCommon import XSDataAngle
from XSDataCommon import XSDataLength
from XSDataCommon import XSDataFloat
from XSDataCommon import XSDataBoolean
from XSDataCommon import XSDataSize

EDFactoryPluginStatic.loadModule("XSDataPyarchThumbnailGeneratorv1_0")
from XSDataPyarchThumbnailGeneratorv1_0 import XSDataInputPyarchThumbnailGeneratorParallel

EDFactoryPluginStatic.loadModule("XSDataMXWaitFilev1_1")
from XSDataMXWaitFilev1_1 import XSDataInputMXWaitFile

def create_thumbnails_for_pyarch(list_image_creation, workflow_working_dir):
    logger = workflow_logging.getLogger()
    xsDataInputPyarchThumbnailGeneratorParallel = XSDataInputPyarchThumbnailGeneratorParallel()
    for image in list_image_creation:
        strPathImage = None
        if "imagePath" in image:
            strPathImage = image["imagePath"]
        elif image["isCreated"]:
            strPathImage = os.path.join(image["fileLocation"], image["fileName"])
        if strPathImage is not None:
            xsDataInputPyarchThumbnailGeneratorParallel.addDiffractionImage(XSDataFile(XSDataString(strPathImage)))
    if xsDataInputPyarchThumbnailGeneratorParallel.diffractionImage != []:
        xsDataInputPyarchThumbnailGeneratorParallel.waitForFileTimeOut = XSDataTime(2000.0)
#         logger.debug(xsDataInputPyarchThumbnailGeneratorParallel.marshal())
        xsDataResult, ednaLogPath = edna_kernel.executeEdnaPlugin("EDPluginControlPyarchThumbnailGeneratorParallelv1_0",
                                                     xsDataInputPyarchThumbnailGeneratorParallel,
                                                     workflow_working_dir,
                                                     )


def create_thumbnails_for_pyarch_asynchronous(beamline, list_image_creation, thumbnailWorkingDir=None):
    logger = workflow_logging.getLogger()
    directory = None
    list_image_names = []
    for image_creation in list_image_creation:
        if directory is None:
            directory = image_creation["fileLocation"]
        list_image_names.append(image_creation["fileName"])
    if list_image_names != []:
        environ_dict = os.environ
        if thumbnailWorkingDir is None:
            strDate = time.strftime("%Y%m%d", time.localtime(time.time()))
            strTime = time.strftime("%H%M%S", time.localtime(time.time()))
            strTmpBaseDir = os.path.join("/tmp", beamline, strDate)
            if not os.path.exists(strTmpBaseDir):
                os.makedirs(strTmpBaseDir, 0755)
            thumbnailWorkingDir = tempfile.mkdtemp(prefix="{0}_thumbnail_".format(strTime), dir=strTmpBaseDir)
        environ_dict["CREATE_THUMBNAIL_WORKING_DIR"] = thumbnailWorkingDir
        command = "/opt/pxsoft/bin/id29_create_thumbnail %s" % directory
        for image_name in list_image_names:
            command += " %s" % image_name
        logger.debug("Thumnail generation command: %s" % command)
        pipe1 = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, close_fds=True, env=environ_dict)

def waitForFile(beamline, filePath, workflow_working_dir, fileSize=None, timeOut=None):
    timedOut = True
    xsDataInputMXWaitFile = XSDataInputMXWaitFile()
    xsDataInputMXWaitFile.file = XSDataFile(XSDataString(filePath))
    if fileSize is not None:
        xsDataInputMXWaitFile.size = XSDataInteger(fileSize)
    if timeOut is not None:
        xsDataInputMXWaitFile.timeOut = XSDataTime(timeOut)
    xsDataResult, ednaLogPath = edna_kernel.executeEdnaPlugin("EDPluginMXWaitFilev1_1",
                                                              xsDataInputMXWaitFile,
                                                              workflow_working_dir)
    if xsDataResult is not None:
        if xsDataResult.timedOut.value:
            timedOut = True
        else:
            timedOut = False
    return timedOut
