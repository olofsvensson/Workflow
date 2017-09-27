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

__authors__ = ["Olof Svensson"]
__license__ = "MIT"
__date__ = "27/09/2017"


import os
import time
import pprint
import tempfile

from workflow_lib import path
from workflow_lib import ispyb
from workflow_lib import edna_mxv1
from workflow_lib import workflow_logging

def run(beamline, dataCollectionId, **kwargs):

    firstAndLastImagesOk = "false"
    firstImageTimeOut = False
    lastImageTimeOut = False

    dateString = time.strftime("%Y%m%d", time.localtime(time.time()))
    timeString = time.strftime("%H%M%S", time.localtime(time.time()))
    pluginBaseDir = os.path.join("/tmp", beamline, dateString)
    if not os.path.exists(pluginBaseDir):
        try:
            os.makedirs(pluginBaseDir, 0755)
        except:
            pass

    workflowWorkingDir = tempfile.mkdtemp(prefix="{0}_waitForFirstAndLastImage_".format(timeString),
                                            dir=pluginBaseDir)

    ispybDataCollection = ispyb.findDataCollection(beamline, dataCollectionId)
    directory = ispybDataCollection.imageDirectory
    fileTemplate = ispybDataCollection.fileTemplate
    imageNoStart = ispybDataCollection.startImageNumber
    imageNoEnd = imageNoStart + ispybDataCollection.numberOfImages - 1
    overlap = ispybDataCollection.overlap
    if fileTemplate.endswith(".h5"):
        pathToStartImage = os.path.join(directory,
                                        path.eigerTemplateToImage(fileTemplate, imageNoStart, overlap))
        pathToEndImage = os.path.join(directory,
                                        path.eigerTemplateToImage(fileTemplate, imageNoEnd, overlap))
    else:
        pathToStartImage = os.path.join(directory, ispybDataCollection.fileTemplate % imageNoStart)
        pathToEndImage = os.path.join(directory, ispybDataCollection.fileTemplate % imageNoEnd)

    if beamline in ["id23eh2", "id30a1", "id30a2"]:
        minFileSize = 2.0e6
    elif beamline in ["id30a3"]:
        minFileSize = 1.0e4
    else:
        minFileSize = 6.0e6

    firstImageTimeOut = edna_mxv1.waitForFile(beamline, pathToStartImage, workflowWorkingDir,
                                              fileSize=minFileSize, timeOut=3600)

    if not firstImageTimeOut:
        if pathToStartImage == pathToEndImage:
            lastImageTimeOut = False
            firstAndLastImagesOk = "true"
        else:
            lastImageTimeOut = edna_mxv1.waitForFile(beamline, pathToEndImage, workflowWorkingDir,
                                                     fileSize=minFileSize, timeOut=3600)
            if not lastImageTimeOut:
                firstAndLastImagesOk = "true"


    return {
        "pathToStartImage": pathToStartImage,
        "pathToEndImage": pathToEndImage,
        "firstImageTimeOut": firstImageTimeOut,
        "lastImageTimeOut": lastImageTimeOut,
        "firstAndLastImagesOk": firstAndLastImagesOk,
        "minFileSize": minFileSize,
        }


if __name__ == '__main__':
    workflowParameters = {}
    beamline = "id30a2"
#    dataCollectionId = 1774250
#    workflow_working_dir = tempfile.mkdtemp(prefix="test_waitForFirstAndLastImage_")
#    dictResult = run(beamline, workflowParameters, dataCollectionId, workflow_working_dir)
#    pprint.pprint(dictResult)
    dataCollectionId = 1766980
#    dataCollectionId = 1961981
    dictResult = run(beamline, dataCollectionId)
    pprint.pprint(dictResult)
