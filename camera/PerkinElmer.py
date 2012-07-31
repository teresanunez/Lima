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

import PyTango
import sys

from Lima import Core
from Lima import PerkinElmer as PerkinElmerModule
from LimaCCDs import CallableReadEnum,CallableWriteEnum
#==================================================================
#   PerkinElmer Class Description:
#
#
#==================================================================


class PerkinElmer(PyTango.Device_4Impl):

#--------- Add you global variables here --------------------------
    Core.DEB_CLASS(Core.DebModApplication, 'LimaCCDs')

#------------------------------------------------------------------
#    Device constructor
#------------------------------------------------------------------
    def __init__(self,cl, name):
        PyTango.Device_4Impl.__init__(self,cl,name)
        self.init_device()

        self.__CorrectionMode = {'NO' : _PerkinElmerIterface.No,
                                 'OFFSET ONLY' : _PerkinElmerIterface.OffsetOnly,
                                 'OFFSET AND GAIN' : _PerkinElmerIterface.OffsetAndGain}
	
	self.__KeepFirstImage = {'YES' : True,
				 'NO' : False}
	
        self.__Attribute2FunctionBase = {
            }
#------------------------------------------------------------------
#    Device destructor
#------------------------------------------------------------------
    def delete_device(self):
        pass


#------------------------------------------------------------------
#    Device initialization
#------------------------------------------------------------------
    def init_device(self):
        self.set_state(PyTango.DevState.ON)
        self.get_device_properties(self.get_device_class())

#==================================================================
#
#    PerkinElmer read/write attribute methods
#
#==================================================================

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
                    function2Call = getattr(_PerkinElmerIterface,functionName)
                    callable_obj = CallableReadEnum(d,function2Call)
                else:
                    functionName = 'set' + attr_name
                    function2Call = getattr(_PerkinElmerIterface,functionName)
                    callable_obj = CallableWriteEnum('_'.join(split_name),
                                                     d,function2Call)
                self.__dict__[name] = callable_obj
                return callable_obj
        raise AttributeError('PerkinElmer has no attribute %s' % name)

    def read_gain(self,attr) :
	gain = _PerkinElmerIterface.getGain()
	attr.set_value(gain)

    def write_gain(self,attr) :
	data = []
	attr.get_write_value(data)
	_PerkinElmerIterface.setGain(*data)
	
#==================================================================
#
#    PerkinElmer command methods
#
#==================================================================
            
#------------------------------------------------------------------
#    getAttrStringValueList command:
#
#    Description: return a list of authorized values if any
#    argout: DevVarStringArray   
#------------------------------------------------------------------
    @Core.DEB_MEMBER_FUNCT
    def getAttrStringValueList(self, attr_name):
        valueList = []
        dict_name = '_' + self.__class__.__name__ + '__' + ''.join([x.title() for x in attr_name.split('_')])
        d = getattr(self,dict_name,None)
        if d:
            valueList = d.keys()
        return valueList


    @Core.DEB_MEMBER_FUNCT
    def startAcqOffsetImage(self,nbImageNtime) :
        nbImage = int(nbImageNtime[0])
        expTime = nbImageNtime[1]
        _PerkinElmerIterface.startAcqOffsetImage(nbImage,expTime)

    @Core.DEB_MEMBER_FUNCT
    def startAcqGainImage(self,nbImageNtime) :
        nbImage = int(nbImageNtime[0])
        expTime = nbImageNtime[1]
        _PerkinElmerIterface.startAcqGainImage(nbImage,expTime)
#==================================================================
#
#    PerkinElmerClass class definition
#
#==================================================================
class PerkinElmerClass(PyTango.DeviceClass):

    #    Class Properties
    class_property_list = {
        }


    #    Device Properties
    device_property_list = {
        }


    #    Command definitions
    cmd_list = {
        'getAttrStringValueList':
        [[PyTango.DevString, "Attribute name"],
         [PyTango.DevVarStringArray, "Authorized String value list"]],
        'startAcqOffsetImage':
        [[PyTango.DevVarDoubleArray, "nb frames,exposure time"],
         [PyTango.DevVoid]],
        'startAcqGainImage':
        [[PyTango.DevVarDoubleArray, "nb frames,exposure time"],
         [PyTango.DevVoid]],
        }


    #    Attribute definitions
    attr_list = {
        'correction_mode':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE]],
	'gain':
	[[PyTango.DevLong,
	  PyTango.SCALAR,
	  PyTango.READ_WRITE]],
	'keep_first_image':
	[[PyTango.DevString,
	  PyTango.SCALAR,
	  PyTango.READ_WRITE]],
        }


#------------------------------------------------------------------
#    PerkinElmerClass Constructor
#------------------------------------------------------------------
    def __init__(self, name):
        PyTango.DeviceClass.__init__(self, name)
        self.set_type(name)

#----------------------------------------------------------------------------
# Plugins
#----------------------------------------------------------------------------
_PerkinElmerIterface = None

def get_control(**keys) :
    global _PerkinElmerIterface
    if _PerkinElmerIterface is None:
        _PerkinElmerIterface = PerkinElmerModule.Interface()
    return Core.CtControl(_PerkinElmerIterface)


def get_tango_specific_class_n_device() :
    return PerkinElmerClass,PerkinElmer
