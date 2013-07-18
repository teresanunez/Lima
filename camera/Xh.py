############################################################################
# This file is part of LImA, a Library for Image Acquisition
#
# Copyright (C) : 2009-2013
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
# file :        Xh.py
#
# description : Python source for the Xh and its commands.
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
from Lima import Xh as XhAcq
# import some useful helpers to create direct mapping between tango attributes
# and Lima interfaces.
from AttrHelper import get_attr_4u, get_attr_string_value_list

#------------------------------------------------------------------
#------------------------------------------------------------------
#    class Xh
#------------------------------------------------------------------
#------------------------------------------------------------------

class Xh(PyTango.Device_4Impl):

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

#------------------------------------------------------------------
#    getAttrStringValueList command:
#
#    Description: return a list of authorized values if any
#    argout: DevVarStringArray   
#------------------------------------------------------------------
    @Core.DEB_MEMBER_FUNCT
    def getAttrStringValueList(self, attr_name):
        valueList=[]
        dict_name = '_' + self.__class__.__name__ + '__' + ''.join([x.title() for x in attr_name.split('_')])
        d = getattr(self,dict_name,None)
        if d:
            valueList = d.keys()

        return valueList


#==================================================================
#
#    Andor read/write attribute methods
#
#==================================================================


    def __getattr__(self,name) :
        return get_attr_4u(self, name, _XhInterface)



#------------------------------------------------------------------
#------------------------------------------------------------------
#    class XhClass
#------------------------------------------------------------------
#------------------------------------------------------------------

class XhClass(PyTango.DeviceClass):

    class_property_list = {}

    device_property_list = {
        'cam_ip_address':
        [PyTango.DevString,
         "Camera ip address",[]],
        'port':
        [PyTango.DevShort,
         "port number",[]],
        'config_name':
        [PyTango.DevString,
         "The default configuration loaded",[]],
        }

    cmd_list = {
        'getAttrStringValueList':
        [[PyTango.DevString, "Attribute name"],
         [PyTango.DevVarStringArray, "Authorized String value list"]],
        }

    attr_list = {
        }

    def __init__(self,name) :
        PyTango.DeviceClass.__init__(self,name)
        self.set_type(name)

#------------------------------------------------------------------
#------------------------------------------------------------------
#    Plugins
#------------------------------------------------------------------
#------------------------------------------------------------------

_XhCam = None
_XhInterface = None

def get_control(cam_ip_address = "0",port = 1972,config_name = 'config',**keys) :
    global _XhCam
    global _XhInterface
    if _XhCam is None:
        print cam_ip_address
	print port
	print config_name
	_XhCam = XhAcq.Camera(cam_ip_address,int(port),config_name)
	_XhInterface = XhAcq.Interface(_XhCam)
    return Core.CtControl(_XhInterface)

def get_tango_specific_class_n_device():
    return XhClass,Xh
