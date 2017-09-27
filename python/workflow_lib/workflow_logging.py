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
Workflow library module for workflow logging.
"""

__authors__ = ["Olof Svensson"]
__license__ = "MIT"
__date__ = "27/09/2017"

import logging, xmlrpclib, json

from workflow_lib import beamline_parameters

class STATICLOGGER:
    """
    Global dictionary for keeping a reference to initialisation flags
    and the paths to the three different log files.
    """
    # pylint: disable=W0232,R0903
    b_stream_init = False
    b_xmlrpc_init = False
    b_beamline_log = True
    workflow_log = None
    workflow_debug_log = None
    workflow_pyarch_log = None

class MxCUBEv1XmlRpcHandler(logging.Handler):
    """
    Handler for mxCuBE v1 (obsolete)
    """

    def __init__(self, mxcube_uri):
        logging.Handler.__init__(self)
        self.serverProxy = xmlrpclib.ServerProxy(mxcube_uri)

    def emit(self, record):
        msg = self.format(record)
        try:
            self.serverProxy.log_message(msg, record.levelno)
        except BaseException:
            # Ignore any errors sending log messages
            pass

class TokenTransport(xmlrpclib.Transport):

    def __init__(self, token, use_datetime=0):
        xmlrpclib.Transport.__init__(self, use_datetime=use_datetime)
        self.token = token

    def send_content(self, connection, request_body):
        connection.putheader("Content-Type", "text/xml")
        connection.putheader("Content-Length", str(len(request_body)))
        connection.putheader("Token", self.token)
        connection.endheaders()
        if request_body:
            connection.send(request_body)

class MxCUBEv2XmlRpcHandler(logging.Handler):
    """
    Handler for mxCuBE v2
    """

    def __init__(self, mxcube_uri, token=None):
        logging.Handler.__init__(self)
        if token is None:
            self.serverProxy = xmlrpclib.ServerProxy(mxcube_uri)
        else:
            self.serverProxy = xmlrpclib.ServerProxy(mxcube_uri, transport=TokenTransport(token))
        self.token = token

    def emit(self, record):
        msg = self.format(record)
        try:
            if record.levelno == logging.INFO:
                self.serverProxy.log_message(msg, "info")
            elif record.levelno == logging.WARN:
                self.serverProxy.log_message(msg, "warning")
            elif record.levelno == logging.ERROR:
                self.serverProxy.log_message(msg, "error")
        except BaseException:
            # Ignore any errors sending log messages
            pass


def getLogger(beamline=None, workflowParameters=None, noBeamlineLog=None, token=None):
    """
    Returns a customised handler depending on beamline etc.
    """
    # TODO: Remove old handlers when adding new ones
    # pylint: disable=R0912,R0915

    logger = logging.getLogger('workflow')
    logger.setLevel(logging.DEBUG)

    workflowLogFile = None
    workflowDebugLogFile = None
    workflowPyarchLogFile = None

    if workflowParameters is not None:

        if type(workflowParameters) == str:
            workflowParameters = json.loads(workflowParameters)

        if "logFile" in workflowParameters:
            workflowLogFile = workflowParameters["logFile"]

        if "debugLogFile" in workflowParameters:
            workflowDebugLogFile = workflowParameters["debugLogFile"]

        if "pyarchLogFile" in workflowParameters:
            workflowPyarchLogFile = workflowParameters["pyarchLogFile"]


    if not STATICLOGGER.b_stream_init:
        STATICLOGGER.b_stream_init = True
        stream_hdlr = logging.StreamHandler()
        stream_formatter = logging.Formatter('%(levelname)s %(message)s')
        stream_hdlr.setFormatter(stream_formatter)
        stream_hdlr.setLevel(logging.DEBUG)
        logger.addHandler(stream_hdlr)

    if workflowLogFile is not None:
        if workflowLogFile != STATICLOGGER.workflow_log:
            STATICLOGGER.workflow_log = workflowLogFile
            info_hdlr = logging.FileHandler(workflowLogFile)
            info_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            info_hdlr.setFormatter(info_formatter)
            info_hdlr.setLevel(logging.INFO)
            logger.addHandler(info_hdlr)

    if workflowDebugLogFile is not None:
        if workflowDebugLogFile != STATICLOGGER.workflow_debug_log:
            STATICLOGGER.workflow_debug_log = workflowDebugLogFile
            debug_hdlr = logging.FileHandler(workflowDebugLogFile)
            debug_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            debug_hdlr.setFormatter(debug_formatter)
            debug_hdlr.setLevel(logging.DEBUG)
            logger.addHandler(debug_hdlr)

    if workflowPyarchLogFile is not None:
        if workflowPyarchLogFile != STATICLOGGER.workflow_pyarch_log:
            STATICLOGGER.workflow_pyarch_log = workflowPyarchLogFile
            pyarch_hdlr = logging.FileHandler(workflowPyarchLogFile)
            pyarch_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            pyarch_hdlr.setFormatter(pyarch_formatter)
            pyarch_hdlr.setLevel(logging.INFO)
            logger.addHandler(pyarch_hdlr)

    if noBeamlineLog:
        STATICLOGGER.b_beamline_log = False

    if not STATICLOGGER.b_xmlrpc_init and STATICLOGGER.b_beamline_log:
        if beamline is not None:
            mxcube_hdlr = None
            mxcube_uri = beamline_parameters.DICT_PARAMETER[beamline]["mxCuBEv2URI"]
            if mxcube_uri is not None:
                mxcube_hdlr = MxCUBEv2XmlRpcHandler(mxcube_uri, token)
            if mxcube_hdlr is not None:
                mxcube_formatter = logging.Formatter('Workflow: %(message)s')
                mxcube_hdlr.setFormatter(mxcube_formatter)
                mxcube_hdlr.setLevel(logging.INFO)
                logger.addHandler(mxcube_hdlr)
                STATICLOGGER.b_xmlrpc_init = True

    return logger




def set_level(_logger, str_level):
    """
    Sets the debug level
    """
    if str_level == "DEBUG":
        _logger.set_level(logging.DEBUG)
    elif str_level == "INFO":
        _logger.set_level(logging.INFO)
    elif str_level == "WARN":
        _logger.set_level(logging.WARN)
    elif str_level == "ERROR":
        _logger.set_level(logging.ERROR)
    else:
        raise Exception("Unknow log level: %r" % str_level)
