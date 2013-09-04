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
# file :        LiveViewer.py
#
# description : A Live viewer plugin for the LimaCCDs device server.
#		It offers a simple interface live acquisition and display of
#		images for camera support the continuous acquistion mode
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

"""
A Live viewer plugin for the LimaCCDs device server.
it offers a simple interface live acquisition and display of
images for camera support the continuous acquistion mode
"""

__docformat__ = 'restructuredtext'

import PyTango
import sys
# Add additional import
from Lima import Core

import numpy
import time

## Device States Description
## No states for this device

class LiveViewer (PyTango.Device_4Impl):
    Core.DEB_CLASS(Core.DebModApplication, 'LimaCCDs')

    attr_Exposure_Time = 0.01
    attr_Nb_Frame = 0
    attr_Frame_Rate = 20
    attr_JPeg_Quality = 50
    
#------------------------------------------------------------------
#    Device constructor
#------------------------------------------------------------------
    @Core.DEB_MEMBER_FUNCT
    def __init__(self,cl, name):
        PyTango.Device_4Impl.__init__(self,cl,name)
        self.init_device()

#------------------------------------------------------------------
#    Device destructor
#------------------------------------------------------------------
    @Core.DEB_MEMBER_FUNCT
    def delete_device(self):
        self.debug_stream("In delete_device()")

        self.control.stopAcq()

#------------------------------------------------------------------
#    Device initialization
#------------------------------------------------------------------	
    @Core.DEB_MEMBER_FUNCT
    def init_device(self):
        self.get_device_properties(self.get_device_class())
        self.attr_Image_ccd_read = [[0]]
        self.control = _control_ref()
        self.image = self.control.image()        
	self.interface = self.control.hwInterface()	
	self.acquisition = self.control.acquisition()
	
	self.acquisition.setAcqExpoTime(self.attr_Exposure_Time)
        self.acquisition.setAcqNbFrames(self.attr_Nb_Frame)
        self.interface.setFrameRate(self.attr_Frame_Rate)

	if self.AcquisitionAutoStart:
           self.control.prepareAcq()
           self.control.startAcq()

		
        self.data = []

    #-----------------------------------------------------------------------------
    #    LiveViewer read/write attribute methods
    #-----------------------------------------------------------------------------
    
    ## @brief Read acquisition exposure time
    #
    @Core.DEB_MEMBER_FUNCT
    def read_Exposure(self,attr) :        
        value = self.acquisition.getAcqExpoTime()
        if value is None: value = -1

        attr.set_value(value)

    ## @brief Write the acquisition exposure time
    #
    @Core.DEB_MEMBER_FUNCT
    def write_Exposure(self, attr):

        data=attr.get_write_value()
        self.control.stopAcq()
        try:
            self.acquisition.setAcqExpoTime(data)
        except:
            self.debug_stream("Exposure time out of range")
	    
        self.control.prepareAcq()
        self.control.startAcq()

    ## @brief Read the gain
    #
    @Core.DEB_MEMBER_FUNCT
    def read_Gain(self,attr) :        
        gain=0
	try:
	    gain = self.interface.getGain()
	except:
	    self.debug_stream("Camera interface does not support Gain")
        attr.set_value(gain)

    ## @brief Write the gain
    #
    @Core.DEB_MEMBER_FUNCT
    def write_Gain(self, attr):

        data=attr.get_write_value()
	self.control.stopAcq()
        try:
            self.interface.setGain(data)
        except:
	    self.debug_stream("Camera interface does not support Gain")
	    
        self.control.prepareAcq()
        self.control.startAcq()
	
    ## @brief Read Frame rate
    #
    @Core.DEB_MEMBER_FUNCT
    def read_FrameRate(self,attr) :        
        fRate = -1
	try:
	    fRate = self.interface.getFrameRate()
	except:
            self.debug_stream("Camera interface does not support FrameRate")
	    	
        attr.set_value(fRate)

    ## @brief Write the frame rate
    #
    @Core.DEB_MEMBER_FUNCT
    def write_FrameRate(self, attr):

        data=attr.get_write_value()

        self.interface.setFrameRate(data)
        #self.debug_stream("Camera interface does not support FrameRate")
	    	

    ## @brief Read acquisition number of frames
    #
    @Core.DEB_MEMBER_FUNCT
    def read_Frames(self,attr) :        
        value = self.acquisition.getAcqNbFrames()
        attr.set_value(value)

    ## @brief Write acquisition number of frames
    #
    @Core.DEB_MEMBER_FUNCT            
    def write_Frames(self, attr):
        data=attr.get_write_value()

        self.control.stopAcq()
	self.acquisition.setAcqNbFrames(data)
        self.control.prepareAcq()
        self.control.startAcq()

    ## @brief Read last image acquire number
    #
    @Core.DEB_MEMBER_FUNCT
    def read_ImageCounter(self,attr) :        
        status = self.control.getStatus()
        imageCounter = status.ImageCounters
	value = imageCounter.LastImageReady
	
        attr.set_value(value)

    ## @brief Read image depth in byte
    #
    @Core.DEB_MEMBER_FUNCT
    def read_Depth(self,attr) :        
        imageType2NbBytes = {
            Core.Bpp8 : (1,0) ,
            Core.Bpp8S : (1,1) ,
            Core.Bpp10 : (2,0) ,
            Core.Bpp10S : (2,1) ,
            Core.Bpp12 : (2,0) ,
            Core.Bpp12S : (2,1) ,
            Core.Bpp14 : (2,0) ,
            Core.Bpp14S : (2,1) , 
            Core.Bpp16 : (2,0),
            Core.Bpp16S : (2,1),
            Core.Bpp32 : (4,0) ,
            Core.Bpp32S : (4,1)
            }        
        imageType = self.image.getImageType()
        depth, signed = imageType2NbBytes.get(imageType,(0,0))
        attr.set_value(depth)

    ## @brief Write the image depth in byte
    #
    @Core.DEB_MEMBER_FUNCT
    def write_depth(self, attr):
	pass

    ## @brief Read JPEG quality factor in %
    #
    @Core.DEB_MEMBER_FUNCT
    def read_JpegQuality(self,attr) :        
        value = self.attr_JPeg_Quality

        attr.set_value(value)

    ## @brief Write the JPEG quality factor in %
    #
    @Core.DEB_MEMBER_FUNCT
    def write_JpegQuality(self, attr):

        data=attr.get_write_value()
        self.attr_JPeg_Quality = data

    ## @brief Read external trigger flag
    #
    @Core.DEB_MEMBER_FUNCT
    def read_ExternalTrigger(self,attr) :        
        trigMode = self.acquisition.getTriggerMode()	
	if trigMode == Core.IntTrig: value = False
	else: value = True	
        attr.set_value(value)

    ## @brief Write the external trigger flag
    #
    @Core.DEB_MEMBER_FUNCT
    def write_ExternalTrigger(self, attr):

        data=attr.get_write_value()
	if data: trigMode = Core.ExtTrigSingle
	else: trigMode = Core.IntTrig
	
	self.control.stopAcq()

        self.acquisition.setTriggerMode(trigMode)

        self.control.prepareAcq()
        self.control.startAcq()

    ## @brief Read ROI definition
    #
    @Core.DEB_MEMBER_FUNCT
    def read_Roi(self,attr) :        
        roi = self.image.getRoi()
	p0 = roi.getTopLeft(); p1 = roi.getBottomRight()
	value=[p0.x,p1.x,p0.y,p1.y]
	
        attr.set_value(value)

    ## @brief Write the ROI definition
    #
    @Core.DEB_MEMBER_FUNCT
    def write_Roi(self, attr):

        data=attr.get_write_value()
	self.control.stopAcq()
        
	roi = Core.Roi()
	roi.setCorners(Core.Point(data[0],data[1]), Core.Point(data[2],data[3]))
	self.image.setRoi(roi)
	
        self.control.prepareAcq()
        self.control.startAcq()
        
    ## @brief Read the last Image
    #
    @Core.DEB_MEMBER_FUNCT            
    def read_Image(self, attr):

	if self.get_state() != PyTango.DevState.FAULT:
	    control = _control_ref()
            image = control.image()        
            dim = image.getImageDim()
           	    	
            data = control.ReadImage(-1)	    
            self.attr_Image_ccd_read = data.buffer	    
	    data.releaseBuffer()
	    self.attr_Image_ccd_read.ravel()
	    self.attr_Image_ccd_read.dtype=numpy.uint8
        attr.set_value(self.attr_Image_ccd_read, dim.getSize().getWidth(), dim.getSize().getHeight())

    ## @brief Read the last Image in JPEG format (DevEncoded)
    #
    @Core.DEB_MEMBER_FUNCT            
    def read_JpegImage(self, attr):

	if self.get_state() != PyTango.DevState.FAULT:
	    control = _control_ref()
            image = control.image()        
            dim = image.getImageDim()
           	    	
            data = control.ReadImage(-1)	    
            dd = data.buffer	    
	    data.releaseBuffer()
	    enc = PyTango.EncodedAttribute()
	    enc.encode_jpeg_gray8(dd, quality=self.attr_JPeg_Quality)
        attr.set_value(enc)
            

#==================================================================
#
#    LiveViewer command methods
#
#==================================================================

    ## @brief State command: try to return a "simple" Lima state of the camera
    #
    @Core.DEB_MEMBER_FUNCT
    def dev_state(self):
        ct_status = self.control.getStatus()
        acq_status = ct_status.AcquisitionStatus
        if acq_status == Core.AcqReady:
            state = PyTango.DevState.OFF
        elif acq_status == Core.AcqRunning:
            state = PyTango.DevState.ON
        else:
            state = PyTango.DevState.FAULT
	self.set_state(state)
	return state

	
    ## @brief Reset command: try to reset the camera after a fault start
    #
    @Core.DEB_MEMBER_FUNCT
    def Reset(self):
    	self.control.reset()
	
    ## @brief ResetRoi command: reset the camera to full image size
    #
    @Core.DEB_MEMBER_FUNCT
    def ResetRoi(self):
	self.control.stopAcq()
	self.image.resetRoi()
        	
        self.control.prepareAcq()
        self.control.startAcq()
	
    ## @brief Start command: start the acquisition
    #
    @Core.DEB_MEMBER_FUNCT
    def Start(self):
        self.control.stopAcq()
	self.control.prepareAcq()
	self.control.startAcq()

    ## @brief Stop command: stop the acquisition
    #
    @Core.DEB_MEMBER_FUNCT
    def Stop(self):
        self.control.stopAcq()
   
class LiveViewerClass(PyTango.DeviceClass): 
    #    Class Properties
    class_property_list = {
        }


    #    Device Properties
    device_property_list = {
        'AcquisitionAutoStart':
            [PyTango.DevBoolean,
            "Flag to start acquisition at startup",
            [ True ] ],
        }


    #    Command definitions
    cmd_list = {
        'Reset':
        [[PyTango.DevVoid,""],
         [PyTango.DevVoid,""]], 
        'ResetRoi':
        [[PyTango.DevVoid,""],
         [PyTango.DevVoid,""]], 
        'Start':
        [[PyTango.DevVoid,""],
         [PyTango.DevVoid,""]], 
        'Stop':
        [[PyTango.DevVoid,""],
         [PyTango.DevVoid,""]], 	    
        }


    #    Attribute definitions
    attr_list = {
        'Exposure':
            [[PyTango.DevDouble,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
         {
             'label':"Exposure time in second",
             'description':"change the exposure and restart the acquisition",
             'unit':"second",
             'standard unit':"second",
             'display unit':"second",
             'format':"%f",
         }],
        'Gain':
            [[PyTango.DevDouble,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
         {
             'label':"Gain",
             'description':"Gain of the camera",
             'unit':"dB",
             'display unit':"dB",
             'format':"%d",
         }],
        'FrameRate':
            [[PyTango.DevDouble,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
         {
             'label':"Frame rate",
             'description':"Frame rate of the acquisition",
             'unit':"Hz",
             'standard unit':"Hz",
             'display unit':"Hz",
             'format':"%f",
         }],
        'Frames':
            [[PyTango.DevLong,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
         {
             'label':"Frame number",
             'description':"Number of frames to be acquired",
             'unit':"image",
             'standard unit':"image",
             'display unit':"image",
             'format':"%d",
         }],
        'ImageCounter':
            [[PyTango.DevLong,
            PyTango.SCALAR,
            PyTango.READ],
         {
             'label':"Image Counter",
             'description':"Current number of images acquired since the last start",
             'unit':"image",
             'standard unit':"image",
             'display unit':"image",
             'format':"%d",
         }],
	    
        'Depth':
            [[PyTango.DevShort,
            PyTango.SCALAR,
            PyTango.READ],
         {
             'label':"Image Depth",
             'description':"Image Depth in byte",
             'unit':"byte",
             'standard unit':"byte",
             'display unit':"byte",
             'format':"%d",
         }],
        'JpegQuality':
            [[PyTango.DevLong,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
         {
             'label':"JPEG Quality factor",
             'unit':"%",
             'standard unit':"%",
             'display unit':"%",
             'format':"%d",
             'description':"The JPEG Quality factor applied for the JpegImage compression",
         }],
        'ExternalTrigger':
            [[PyTango.DevBoolean,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
         {
             'label':"External Trigger flag",
             'description':"The External trigger mode: True or False. If true, the camera will acquire in gate mode (in supported)",	     
             'unit':"",
             'standard unit':"",
             'display unit':"",
             'format':"%d",
         }],
        'Roi':
            [[PyTango.DevLong,
            PyTango.SPECTRUM,
            PyTango.READ_WRITE,4],
         {
             'label':"Region of Interest",
             'description':"ROI definition: startX, endX, stopY, endY",
             'unit':"",
             'standard unit':"",
             'display unit':"",
             'format':"%d",
         }],	    
        'Image':
            [[PyTango.DevUChar,
            PyTango.IMAGE,
            PyTango.READ, 4096, 4096],
         {
             'label':"Last Image",
             'description':"The last image ready",	     
         }],
        'JpegImage':
            [[PyTango.DevEncoded,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
         {
             'label':"Last JpegImage",
             'description':"The last image ready in JPEG format (DevEncoded)",
	     'format': "RawImage",
	 }],	    
        }
#------------------------------------------------------------------
#    LiveViewerClass Constructor
#------------------------------------------------------------------
    def __init__(self, name):
        PyTango.DeviceClass.__init__(self, name)
        self.set_type(name);

_control_ref = None
def set_control_ref(control_class_ref) :
    global _control_ref
    _control_ref= control_class_ref

def get_tango_specific_class_n_device() :
   return LiveViewerClass,LiveViewer
