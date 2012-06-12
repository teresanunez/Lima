############################################################################
# This file is part of LImA, a Library for Image Acquisition
#
# Copyright (C) : 2009-2011
# European Synchrotron Radiation Facility
# BP 220, Grenoble 38043
# FRANCE
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
############################################################################
#=============================================================================
#
# file :        Frelon.py
#
# description : Python source for the Frelon and its commands.
#                The class is derived from Device. It represents the
#                CORBA servant object which will be accessed from the
#                network. All commands which can be executed on the
#                Pilatus are implemented in this file.
#
# project :     TANGO Device Server
#
# copyleft :    European Synchrotron Radiation Facility
#               BP 220, Grenoble 38043
#               FRANCE
#
#=============================================================================
#         (c) - Bliss - ESRF
#=============================================================================
#
import time
import PyTango
from Lima import Core
from Lima import Frelon as FrelonAcq
from LimaCCDs import CallableReadEnum,CallableWriteEnum


class Frelon(PyTango.Device_4Impl):

    Core.DEB_CLASS(Core.DebModApplication, 'LimaCCDs')


#------------------------------------------------------------------
#    Device constructor
#------------------------------------------------------------------
    def __init__(self,*args) :
        PyTango.Device_4Impl.__init__(self,*args)

        self.__ImageMode = {'FRAME TRANSFER': FrelonAcq.FTM,
                            'FULL FRAME': FrelonAcq.FFM}

        self.__RoiMode = {'NONE' : FrelonAcq.None,
                          'SLOW' : FrelonAcq.Slow,
                          'FAST' : FrelonAcq.Fast,
                          'KINETIC' : FrelonAcq.Kinetic}

        self.__InputChannel = {'1'       : 0x1,
                               '2'       : 0x2,
                               '3'       : 0x4,
                               '4'       : 0x8,
                               '1-2'     : 0x3,
                               '3-4'     : 0xc,
                               '1-3'     : 0x5,
                               '2-4'     : 0xA,
                               '1-2-3-4' : 0xf} 

        self.__E2vCorrection = {'ON' : True,
                                'OFF' : False}

        self.__Spb2Config = {'PRECISION' : 0,
                             'SPEED' : 1}

        self.__Attribute2FunctionBase = {'image_mode' : 'FrameTransferMode',
                                         'input_channel' : 'InputChan',
                                         'e2v_correction' : 'E2VCorrectionActive',
                                         'spb2_config' : 'SPB2Config'}

        self.init_device()

#------------------------------------------------------------------
#    Device destructor
#------------------------------------------------------------------
    def delete_device(self):
        pass

#------------------------------------------------------------------
#    Device initialization
#------------------------------------------------------------------
    @Core.DEB_MEMBER_FUNCT
    def init_device(self):
        self.set_state(PyTango.DevState.ON)
        self.get_device_properties(self.get_device_class())
	self.ResetLinkWaitTime = 5	

    @Core.DEB_MEMBER_FUNCT
    def getAttrStringValueList(self, attr_name):
        valueList=[]
        dict_name = '_' + self.__class__.__name__ + '__' + ''.join([x.title() for x in attr_name.split('_')])
        d = getattr(self,dict_name,None)
        if d:
            valueList = d.keys()

        return valueList

    def __getattr__(self,name) :
        if name.startswith('read_') or name.startswith('write_') :
            split_name = name.split('_')[1:]
            attr_name = ''.join([x.title() for x in split_name])
            dict_name = '_' + self.__class__.__name__ + '__' + attr_name
            d = getattr(self,dict_name,None)
            attr_name = self.__Attribute2FunctionBase.get('_'.join(split_name),attr_name)
            if d:
                if name.startswith('read_') :
                    functionName = 'get' + attr_name
                    function2Call = getattr(_FrelonAcq,functionName)
                    callable_obj = CallableReadEnum(d,function2Call)
                else:
                    functionName = 'set' + attr_name
                    function2Call = getattr(_FrelonAcq,functionName)
                    callable_obj = CallableWriteEnum('_'.join(split_name),
                                                     d,function2Call)
                self.__dict__[name] = callable_obj
                return callable_obj
        raise AttributeError('Frelon has no attribute %s' % name)

    @Core.DEB_MEMBER_FUNCT
    def execSerialCommand(self, command_string) :
        return _FrelonAcq.execFrelonSerialCmd(command_string)

    @Core.DEB_MEMBER_FUNCT
    def resetLink(self) :
        _FrelonAcq.getEspiaDev().resetLink()
	time.sleep(self.ResetLinkWaitTime)

    ## @brief read the espia board id
    #
    def read_espia_dev_nb(self,attr) :
        espia_dev_nb = 0
        if self.espia_dev_nb:
            espia_dev_nb = self.espia_dev_nb
        attr.set_value(espia_dev_nb)

    def read_roi_bin_offset(self,attr) :
        attr.set_value(-1)
        #TODO

    def write_roi_bin_offset(self,attr) :
        data = []
        attr.get_write_value(data)
        #TODO


class FrelonClass(PyTango.DeviceClass):

    class_property_list = {}

    device_property_list = {
        'espia_dev_nb':
        [PyTango.DevShort,
         "Espia board device number",[]],
        }

    cmd_list = {
        'getAttrStringValueList':
        [[PyTango.DevString, "Attribute name"],
         [PyTango.DevVarStringArray, "Authorized String value list"]],
        'execSerialCommand':
        [[PyTango.DevString,"command"],
         [PyTango.DevString,"return command"]],
        'resetLink':
        [[PyTango.DevVoid,""],
         [PyTango.DevVoid,""]],
        }

    attr_list = {
        'espia_dev_nb':
        [[PyTango.DevShort,
          PyTango.SCALAR,
          PyTango.READ]],
        'image_mode' :
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE]],
        'input_channel' :
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE]],
        'roi_mode' :
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE]],
        'roi_bin_offset' :
        [[PyTango.DevLong,
          PyTango.SCALAR,
          PyTango.READ_WRITE]],
        'e2v_correction' :
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE]],
        'spb2_config' :
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE]],
        }

    def __init__(self,name) :
        PyTango.DeviceClass.__init__(self,name)
        self.set_type(name)

#----------------------------------------------------------------------------
# Plugins
#----------------------------------------------------------------------------
_FrelonAcq = None

def get_control(espia_dev_nb = 0,**keys) :
    global _FrelonAcq
    if _FrelonAcq is None:
	_FrelonAcq = FrelonAcq.FrelonAcq(int(espia_dev_nb))
    return _FrelonAcq.getGlobalControl() 

def get_tango_specific_class_n_device():
    return FrelonClass,Frelon
