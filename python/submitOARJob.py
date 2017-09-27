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

from workflow_lib import mxnice


def run(beamline=None, dataCollectionId=None, ednaDpLaunchPath=None,
        launchPath=None, procType=None, numberOfImages=None, proposal=None,
        nodes=1, core=4, queue=None, **kwargs):

    nodes = int(nodes)
    core = int(core)

    # To be removed when all launchers use launchPath instead of ednaDpLaunchPath
    if launchPath is None:
        launchPath = ednaDpLaunchPath


    name = "{procType}, {proposal}, {beamline}, {numberOfImages}, id={dataCollectionId}".format(procType=procType,
                                                          beamline=beamline,
                                                          numberOfImages=numberOfImages,
                                                          dataCollectionId=dataCollectionId,
                                                          proposal=proposal)
    commandLine = "export AutoPROCWorkFlowUser=True; {0}".format(launchPath)
    workingDirectory = os.path.dirname(launchPath)
    oarCommand, oarJobId = mxnice.submitJobToOar(commandLine, workingDirectory, queue=queue, nodes=nodes, core=core, walltime="2:00:00", name=name)

    return {"oarCommand": oarCommand,
            "oarJobId": oarJobId,
            "commandLine": commandLine,
            "workingDirectory": workingDirectory}


