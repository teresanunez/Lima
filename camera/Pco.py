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
# file :        Pco.py
#
# description : Python source for the Pco and its commands.
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
import PyTango
from Lima import Core
from Lima import Pco as PcoAcq
from LimaCCDs import CallableReadEnum,CallableWriteEnum


class Pco(PyTango.Device_4Impl):

    Core.DEB_CLASS(Core.DebModApplication, 'LimaCCDs')


#------------------------------------------------------------------
#    Device constructor
#------------------------------------------------------------------
    def __init__(self,*args) :
        PyTango.Device_4Impl.__init__(self,*args)

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
                    function2Call = getattr(_PcoAcq,functionName)
                    callable_obj = CallableReadEnum(d,function2Call)
                else:
                    functionName = 'set' + attr_name
                    function2Call = getattr(_PcoAcq,function2Call)
                    callable_obj = CallableWriteEnum(d,function2Call)
                self.__dict__[name] = callable_obj
                return callable_obj
        raise AttributeError('Pco has no attribute %s' % name)

#==================================================================
#
#    Pco read/write attribute methods
#
#==================================================================

#------------------------------------------------------------------
#    Read attribute
#------------------------------------------------------------------
    def read_cocRunTime(self, attr):
        val  = _PcoCam.talk("cocRunTime")
        attr.set_value(val)

    def read_frameRate(self, attr):
        val  = _PcoCam.talk("frameRate")
        attr.set_value(val)

    def read_maxNbImages(self, attr):
        val  = _PcoCam.talk("maxNbImages")
        attr.set_value(val)

    def read_info(self, attr):
        val= _PcoCam.talk("")
        attr.set_value(val)




#==================================================================
#
#    Pco command methods
#
#==================================================================
    def talk(self, argin):
        val= _PcoCam.talk(argin)
        return val


#==================================================================
#
#    PcoClass class definition
#
#==================================================================
class PcoClass(PyTango.DeviceClass):

    #    Class Properties
    class_property_list = {}

    #    Device Properties
    device_property_list = {
        }

    #    Command definitions
    cmd_list = {
        'getAttrStringValueList':
        [[PyTango.DevString, "Attribute name"],
         [PyTango.DevVarStringArray, "Authorized String value list"]],
        'talk':
        [[PyTango.DevString, "str argin"],
         [PyTango.DevString, "str argout"]],
        }

    #    Attribute definitions
    attr_list = {
         'cocRunTime':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
         {
             'label':"COC",
             'unit':"",
             'format':"",
             'description':"coc Run Time",
          }],
         'frameRate':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
         {
             'label':"frameRate",
             'unit':"",
             'format':"",
             'description':"frame rate",
          }],
         'maxNbImages':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
         {
             'label':"maxImg",
             'unit':"",
             'format':"",
             'description':"max nb of images in the segment",
          }],
         'info':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
         {
             'label':"INFO",
             'unit':"",
             'format':"",
             'description':"general information",
          }],
    
        }

#------------------------------------------------------------------
#    PcoClass Constructor
#------------------------------------------------------------------
    def __init__(self,name) :
        PyTango.DeviceClass.__init__(self,name)
        self.set_type(name)

#----------------------------------------------------------------------------
# Plugins
#----------------------------------------------------------------------------
_PcoCam = None
_PcoInterface = None

def get_control(**keys) :
    global _PcoCam
    global _PcoInterface


    if 0:
        Core.DebParams.setModuleFlags(0xffffffff)
        Core.DebParams.setTypeFlags(0xffffffff)
    else:
        Core.DebParams.setTypeFlags(0)
        Core.DebParams.setModuleFlags(0)

    Core.DebParams.setFormatFlags(0x30)

    if _PcoCam is None:
        _PcoCam = PcoAcq.Camera("")
        _PcoInterface = PcoAcq.Interface(_PcoCam)
    return Core.CtControl(_PcoInterface)

def get_tango_specific_class_n_device():
    return PcoClass,Pco

def close_interface() :
    global _PcoCam
    _PcoCam = None
