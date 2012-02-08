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
# file :        Andor.py
#
# description : Python source for the Andor and its commands. 
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
import sys, types, os, time

from Lima import Core
from Lima import Andor as AndorModule
from LimaCCDs import CallableReadEnum,CallableWriteEnum

class Andor(PyTango.Device_4Impl):

    Core.DEB_CLASS(Core.DebModApplication, 'LimaCCDs')
    
#==================================================================
#   Andor Class Description:
#
#
#==================================================================

class Andor(PyTango.Device_4Impl):

#--------- Add you global variables here --------------------------
    Core.DEB_CLASS(Core.DebModApplication, 'LimaCCDs')

#------------------------------------------------------------------
#    Device constructor
#------------------------------------------------------------------
    @Core.DEB_MEMBER_FUNCT
    def __init__(self,cl, name):
        PyTango.Device_4Impl.__init__(self,cl,name)
        self.init_device()

        self.__FastTrigger = {'ON':True,
                           'OFF':False}
        self.__Cooler = {'ON': True,
                             'OFF': False}
        self.__ShutterLevel = {'LOW':0,
                                   'HIGH':1}       
        self.__Attribute2FunctionBase = {'fast_trigger': 'FastExtTrigger',
                                         'shutter_level': 'ShutterLevel',
                                         'temperature': 'Temperature',
                                         'temperature_sp': 'TemperatureSP',
                                         'cooler': 'Cooler',
                                         'cooling_status': 'CoolingStatus',
                                         }
                                         

        
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

        # Load the properties
        self.get_device_properties(self.get_device_class())

        # Apply properties if any
        if self.preamp_gain:
            _AndorCamera.setPGain(self.preamp_gain)
            
        if self.vss:
            _AndorCamera.setVSS(self.vss)
            
        if self.adc:
            _AndorCamera.setAdcSpeed(self.adc)

        if self.temperature_sp:            
            _AndorCamera.setTemperatureSP(self.temperature_sp)
            
        if self.cooler:
            _AndorCamera.setCooler(self.__Cooler[self.cooler])
            
        if self.fast_trigger:
            _AndorCamera.setFastExtTrigger(self.__FastTrigger[self.fast_trigger])
            
        if self.shutter_level:
            _AndorCamera.setShutterLevel(self.__ShutterLevel[self.shutter_level])

#==================================================================
#
#    Andor read/write attribute methods
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
                    function2Call = getattr(_AndorCamera,functionName)
                    callable_obj = CallableReadEnum(d,function2Call)
                else:
                    functionName = 'set' + attr_name
                    function2Call = getattr(_AndorCamera,functionName)
                    callable_obj = CallableWriteEnum('_'.join(split_name),
                                                     d,function2Call)

            else:
                if name.startswith('read_') :
                    functionName = 'get' + attr_name
                    function2Call = getattr(_AndorCamera,functionName)
                    callable_obj = CallableRead(function2Call)
                else:
                    functionName = 'set' + attr_name
                    function2Call = getattr(_AndorCamera,functionName)
                    callable_obj = CallableWrite('_'.join(split_name),
                                                     function2Call)
                
            self.__dict__[name] = callable_obj
            return callable_obj
        raise AttributeError('Andor has no attribute %s' % name)

    ## @brief return the timing times, exposure and latency
    #  
    def read_timing(self, attr):
        timing=[]
        timing.append(_AndorCamera.getExpTime())
        timing.append(_AndorCamera.getLatTime())
        
        attr.set_value(timing,2)        
        

#==================================================================
#
#    Andor command methods
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


#==================================================================
#
#    Andor class definition
#
#==================================================================
class AndorClass(PyTango.DeviceClass):

    #    Class Properties
    class_property_list = {
        }

    #    Device Properties
    device_property_list = {
        'config_path':
        [PyTango.DevString,
         'configuration path directory', []],
        'camera_number':
        [PyTango.DevShort,
         'Camera number', []],
        'preamp_gain':
        [PyTango.DevShort,
         'Preamplifier gain', []],
        'vss':
        [PyTango.DevShort,
         'Vertical shift speed', []],
        'adc':
        [PyTango.DevShort,
         'ADC speed pairs', []],
        'temperature_sp':
        [PyTango.DevShort,
         'Temperature set point in Celsius', []],
        'cooler':
        [PyTango.DevString,
         'Start or stop the cooler ("ON"/"OFF")', []],
        'fast_trigger':
        [PyTango.DevString,
         'Trigger fast mode ("ON"/"OFF")', []],
        'shutter_level':
        [PyTango.DevString,
         'level of the shutter output ("LOW"/"HIGH")', []],                 
        }


    #    Command definitions
    cmd_list = {
        'getAttrStringValueList':
        [[PyTango.DevString, "Attribute name"],
         [PyTango.DevVarStringArray, "Authorized String value list"]]
        }


    #    Attribute definitions
    attr_list = {
        'fast_trigger':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':'Fast trigger mode, see manual for usage',
             'unit': 'N/A',
             'format': '',
             'description': 'OFF or ON',
             }],
        'shutter_level':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':'Shutter output level, see manual for usage',
             'unit': 'N/A',
             'format': '',
             'description': 'LOW or HIGH',
             }],
       'temperature_sp':
        [[PyTango.DevShort,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':'Set/get the temperature set-point',
             'unit': 'C',
             'format': '%1d',
             'description': 'in Celsius',
             }],
        'temperature':
        [[PyTango.DevShort,
          PyTango.SCALAR,
          PyTango.READ],
         {
             'label':'get the current temperature sensor',
             'unit': 'C',
             'format': '%1d',
             'description': 'in Celsius',
             }],
        'cooler':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':'Start/stop the cooler',
             'unit': 'N/A',
             'format': '',
             'description': 'OFF or ON',
             }],
        'cooling_status':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ],
         {
             'label':'Fast trigger mode, see manual for usage',
             'unit': 'N/A',
             'format': '%1d',
             'description': '0-OFF / 1-ON',
             }],
        'timing':
        [[PyTango.DevFloat,
          PyTango.SPECTRUM,
          PyTango.READ,2],
        {
             'label':'Timing values, exposure and latency times',
             'unit': 'second',
             'format': '%f',
             'description': '[0]: exposure, [1]: latency',
             }],
        }

#------------------------------------------------------------------
#    AndorClass Constructor
#------------------------------------------------------------------
    def __init__(self, name):
        PyTango.DeviceClass.__init__(self, name)
        self.set_type(name)

#------------------------------------------------------------------
#    Tools
#------------------------------------------------------------------

class CallableRead:
    def __init__(self,func2Call) :        
        self.__func2Call = func2Call

    def __call__(self,attr) :
        value = self.__func2Call()
        attr.set_value(value)

class CallableWrite:
    def __init__(self,attr_name,func2Call) :
        self.__attr_name = attr_name
        self.__func2Call = func2Call
        
    def __call__(self,attr) :
        data = []
        attr.get_write_value(data)
        value = data[0]
        if value is None:
            PyTango.Except.throw_exception('WrongData',\
                                           'Wrong value %s: %s'%(self.__attr_name,data[0].upper()),\
                                           'LimaCCD Class')
        else:
            self.__func2Call(value)
            
#----------------------------------------------------------------------------
#                              Plugins
#----------------------------------------------------------------------------
from Lima  import Andor as AndorAcq

_AndorCamera = None
_AndorInterface = None

def get_control(config_path='/usr/local/etc/andor', camera_number = '0',**keys) :
    #properties are passed here as string
    global _AndorCamera
    global _AndorInterface
    if _AndorCamera is None:
        print '\n\nStarting and configuring the Andor camera ...'
        _AndorCamera = AndorAcq.Camera(config_path, int(camera_number))
        _AndorInterface = AndorAcq.Interface(_AndorCamera)
        print '\n\nAndor Camera #%s (%s:%s) is started'%(camera_number,_AndorCamera.getDetectorType(),_AndorCamera.getDetectorModel())
    return Core.CtControl(_AndorInterface)

    
def get_tango_specific_class_n_device():
    return AndorClass,Andor

