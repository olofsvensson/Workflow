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
Workflow library module for connecting to ISPyB
"""

__authors__ = ["Olof Svensson"]
__license__ = "MIT"
__date__ = "27/09/2017"


__author__ = "Olof Svensson"
__contact__ = "svensson@esrf.eu"
__copyright__ = "ESRF, 2013"
__updated__ = "2016-02-17"

import os
import sys
import json
import time
import workflow_logging

# sys.path.insert(0, "/opt/pxsoft/EDNA/vMX/edna/libraries/suds-0.4")

from suds.client import Client
from suds.transport.https import HttpAuthenticated
from suds.sudsobject import asdict


def getTransport():
    transport = None
    logger = workflow_logging.getLogger()
    if not "ISPyB_user" in os.environ:
        logger.error("No ISPyB user name defined as environment variable!")
    elif not "ISPyB_pass" in os.environ:
        logger.error("No ISPyB password defined as environment variable!")
    else:
        ispybUserName = os.environ["ISPyB_user"]
        ispybPassword = os.environ["ISPyB_pass"]
        transport = HttpAuthenticated(username=ispybUserName, password=ispybPassword)
    return transport

def getWdslRoot(beamline):
    if beamline in ["id30a2"] or beamline.startswith("simulator"):
        wdslRoot = "http://ispyvalid.esrf.fr:8080/ispyb/ispyb-ws/ispybWS"
    else:
        wdslRoot = "http://ispyb.esrf.fr:8080/ispyb/ispyb-ws/ispybWS"
    return wdslRoot

def getToolsForShippingWebServiceWdsl(beamline):
    return os.path.join(getWdslRoot(beamline), "ToolsForShippingWebService?wsdl")

def getToolsForCollectionWebService(beamline):
    return os.path.join(getWdslRoot(beamline), "ToolsForCollectionWebService?wsdl")

def getToolsForShippingWebService(beamline):
    return os.path.join(getWdslRoot(beamline), "ToolsForShippingWebService?wsdl")

def getShippingWebServiceClient(beamline):
    logger = workflow_logging.getLogger()
    shippingWdsl = getToolsForShippingWebServiceWdsl(beamline)
    transport = getTransport()
    if transport is None:
        logger.error("No transport defined, ISPyB web service client cannot be instantiated.")
        shippingWSClient = None
    else:
        shippingWSClient = Client(shippingWdsl, transport=transport)
    return shippingWSClient

def getCollectionWebService(beamline):
    logger = workflow_logging.getLogger()
    collectionWdsl = getToolsForCollectionWebService(beamline)
    transport = getTransport()
    if transport is None:
        logger.error("No transport defined, ISPyB web service client cannot be instantiated.")
        collectionWSClient = None
    else:
        collectionWSClient = Client(collectionWdsl, transport=transport)
    return collectionWSClient

def getShippingWebService(beamline):
    logger = workflow_logging.getLogger()
    shippingWdsl = getToolsForShippingWebService(beamline)
    transport = getTransport()
    if transport is None:
        logger.error("No transport defined, ISPyB web service client cannot be instantiated.")
        collectionWSClient = None
    else:
        collectionWSClient = Client(shippingWdsl, transport=transport)
    return collectionWSClient

def findPersonByProposal(beamline, proposalCode, proposalNumber):
    person = None
    logger = workflow_logging.getLogger()
    # Exclude opidXX accounts
    if proposalCode != "opid":
        client = getShippingWebServiceClient(beamline)
        if client is None:
            logger.error("No web service client available, cannot contact findPersonByProposal web service.")
        elif proposalCode is None:
            logger.error("No proposal code given, cannot contact findPersonByProposal web service.")
        elif proposalNumber is None:
            logger.error("No proposal number given, cannot contact findPersonByProposal web service.")
        else:
            person = asdict(client.service.findPersonByProposal(proposalCode, proposalNumber))
    return person


def findDataCollection(beamline, dataCollectionId, client=None):
    dataCollectionWS3VO = None
    logger = workflow_logging.getLogger()
    if client is None:
        client = getCollectionWebService(beamline)
    if client is None:
        logger.error("No web service client available, cannot contact findDataCollectionFromFileLocationAndFileName web service.")
    elif dataCollectionId is None:
        logger.error("No dataCollectionId given, cannot contact storeOrUpdateDataCollection web service.")
    else:
        dataCollectionWS3VO = client.service.findDataCollection(dataCollectionId)
    return dataCollectionWS3VO

def findDataCollectionFromFileLocationAndFileName(beamline, fileLocation, fileName, client=None):
    dataCollectionWS3VO = None
    logger = workflow_logging.getLogger()
    if client is None:
        client = getCollectionWebService(beamline)
    if client is None:
        logger.error("No web service client available, cannot contact findDataCollectionFromFileLocationAndFileName web service.")
    elif fileLocation is None:
        logger.error("No fileLocation given, cannot contact storeOrUpdateDataCollection web service.")
    elif fileName is None:
        logger.error("No fileName given, cannot contact storeOrUpdateDataCollection web service.")
    else:
        dataCollectionWS3VO = client.service.findDataCollectionFromFileLocationAndFileName(fileLocation, fileName)
    return dataCollectionWS3VO



def storeOrUpdateDataCollection(beamline, dataCollectionWS3VO, client=None):
    dataCollectionId = None
    logger = workflow_logging.getLogger()
    if client is None:
        client = getCollectionWebService(beamline)
    if client is None:
        logger.error("No web service client available, cannot contact storeOrUpdateDataCollection web service.")
    elif dataCollectionWS3VO is None:
        logger.error("No dataCollection given, cannot contact storeOrUpdateDataCollection web service.")
    else:
        dataCollectionId = client.service.storeOrUpdateDataCollection(dataCollectionWS3VO)
    return dataCollectionId


def findDataCollectionGroup(beamline, dataCollectionId, client=None):
    dataCollectionGroupWS3VO = None
    logger = workflow_logging.getLogger()
    if client is None:
        client = getCollectionWebService(beamline)
    if client is None:
        logger.error("No web service client available, cannot contact findDataCollectionGroup web service.")
    elif dataCollectionId is None:
        logger.error("No dataCollectionId given, cannot contact findDataCollectionGroup web service.")
    else:
        dataCollectionGroupWS3VO = client.service.findDataCollectionGroup(dataCollectionId)
    return dataCollectionGroupWS3VO

def storeOrUpdateDataCollectionGroup(beamline, dataCollectionGroupWS3VO, client=None):
    logger = workflow_logging.getLogger()
    if client is None:
        client = getCollectionWebService(beamline)
    if client is None:
        logger.error("No web service client available, cannot contact storeOrUpdateDataCollectionGroup web service.")
    elif dataCollectionGroupWS3VO is None:
        logger.error("No dataCollectionGroup given, cannot contact storeOrUpdateDataCollectionGroup web service.")
    else:
        dataCollectionGrouoId = client.service.storeOrUpdateDataCollectionGroup(dataCollectionGroupWS3VO)
    return dataCollectionGrouoId


def updateDataCollectionComment(beamline, filePath, newComment):
    dataCollectionId = None
    logger = workflow_logging.getLogger()
    client = getCollectionWebService(beamline)
    if client is None:
        logger.error("No web service client available, cannot contact storeOrUpdateDataCollection web service.")
    fileLocation = os.path.dirname(filePath)
    fileName = os.path.basename(filePath)
    dataCollectionWS3VO = findDataCollectionFromFileLocationAndFileName(beamline, fileLocation, fileName, client=client)
    if (dataCollectionWS3VO is not None) and (newComment is not None):
        if hasattr(dataCollectionWS3VO, "comments") and (dataCollectionWS3VO.comments is not None):
            newComments = dataCollectionWS3VO.comments + " " + newComment
            if len(newComments) < 1024:
                dataCollectionWS3VO.comments = newComments
            else:
                logger.debug("New ISPyB comment too long! '{0}'".format(newComments))
        elif len(newComment) < 1024:
            dataCollectionWS3VO.comments = newComment
        else:
            logger.debug("New ISPyB comment too long! '{0}'".format(newComment))
        dataCollectionId = storeOrUpdateDataCollection(beamline, dataCollectionWS3VO, client=client)
    else:
        dataCollectionId = dataCollectionWS3VO.dataCollectionId
    return dataCollectionId

def updateDataCollectionGroupComment(beamline, filePath, newComment):
    dataCollectionGroupId = None
    logger = workflow_logging.getLogger()
    client = getCollectionWebService(beamline)
    if client is None:
        logger.error("No web service client available, cannot contact storeOrUpdateDataCollectionGroup web service.")
    fileLocation = os.path.dirname(filePath)
    fileName = os.path.basename(filePath)
    dataCollectionWS3VO = findDataCollectionFromFileLocationAndFileName(beamline, fileLocation, fileName, client=client)
    if (dataCollectionWS3VO is not None) and (newComment is not None):
        dataCollectionGroupId = dataCollectionWS3VO.dataCollectionGroupId
        dataCollectionGroupWS3VO = findDataCollectionGroup(beamline, dataCollectionGroupId, client=client)
        if dataCollectionGroupWS3VO is not None:
            if (dataCollectionGroupWS3VO.comments is not None) and len(dataCollectionGroupWS3VO.comments + " " + newComment) >= 1024:
                logger.debug("New ISPyB comment make data collection group comment too long! '{0}'".format(dataCollectionGroupWS3VO.comments + " " + newComment))
            elif len(newComment) >= 1024:
                logger.debug("New ISPyB comment make data collection group comment too long! '{0}'".format(newComment))
            else:
                dataCollectionGroupWS3VO.comments = newComment
                dataCollectionGroupId = storeOrUpdateDataCollectionGroup(beamline, dataCollectionGroupWS3VO, client=client)
                logger.info("ISPyB comment added: {0}".format(newComment))
    elif dataCollectionWS3VO is not None:
        dataCollectionGroupId = dataCollectionWS3VO.dataCollectionGroupId
    return dataCollectionGroupId

def storeWorkflowStep(beamline, workflowId, workflowStepType, status="Success", folderPath=None, imageResultFilePath=None,
                      htmlResultFilePath=None, resultFilePath=None, comments=None):
    workflowStepID = None
    logger = workflow_logging.getLogger()
    client = getCollectionWebService(beamline)
    if client is None:
        logger.error("No web service client available, cannot contact storeOrUpdateDataCollectionGroup web service.")
    else:
        workflowStep = json.dumps({
            "workflowId"                  : workflowId,
            "workflowStepType"            : workflowStepType,
            "status"                      : status,
            "folderPath"                  : folderPath,
            "imageResultFilePath"         : imageResultFilePath,
            "htmlResultFilePath"          : htmlResultFilePath,
            "resultFilePath"              : resultFilePath,
            "comments"                    : comments,
         })
        workflowStepID = client.service.storeWorkflowStep(workflowStep)
    return workflowStepID

def findProposal(beamline, code, number):
    client = getShippingWebService(beamline)
    proposal = client.service.findProposal(code + str(number))
    return proposal

def findProposalByCodeAndNumber(beamline, code, number):
    client = getShippingWebService(beamline)
    proposal = client.service.findProposalByCodeAndNumber(code, number)
    return proposal

def findPersonByProteinAcronym(beamline, code, number, acronym):
    person = None
    proposal = findProposal(beamline, code, number)
    if proposal is not None:
        proposalId = proposal.proposalId
        print(proposalId)
        client = getShippingWebService(beamline)
        person = client.service.findPersonByProteinAcronym(proposalId, acronym)
    return person

def updateDataCollectionSnapShots(beamline, dataCollectionId, listSnapShotPath):
    logger = workflow_logging.getLogger()
    client = getCollectionWebService(beamline)
    if client is None:
        logger.error("No web service client available, cannot contact storeOrUpdateDataCollection web service.")
    dataCollectionWS3VO = findDataCollection(beamline, dataCollectionId, client=client)
    if dataCollectionWS3VO is not None:
        index = 1
        for snapShotPath in listSnapShotPath:
            setattr(dataCollectionWS3VO, "xtalSnapshotFullPath{0}".format(index), snapShotPath)
            index += 1
            if index > 4:
                break
        dataCollectionId = storeOrUpdateDataCollection(beamline, dataCollectionWS3VO, client=client)
    return dataCollectionId
