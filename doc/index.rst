TANGO
=====

This is the python Tango devices server developped at ESRF.
Thanks to the Lima framework,  the control can be achieved through a common device as well as some features like calculations. The configuration of the detector is done by  the specific detector device. 
At ESRF we decided to develop the Tango devices only in python language
which implies that all the detector C++ interfaces have been wrapped to python modules.

Control device
--------------

**LimaCCDs** is the generic device:

Commandes
'''''''''

+-----------------------+-------------------------------------------+-------------------------------------+-----------------------------------------------------------------------------------------------------+
|**Command name**       |**Arg. in**                                |**Arg. out**                         |**Description**                                                                                      |
+-----------------------+-------------------------------------------+-------------------------------------+-----------------------------------------------------------------------------------------------------+
|Init                   |DevVoid                                    |DevVoid                              |Do not use                                                                                           |
+-----------------------+-------------------------------------------+-------------------------------------+-----------------------------------------------------------------------------------------------------+
|State                  |DevVoid                                    |DevLong                              |Return the device state                                                                              |
+-----------------------+-------------------------------------------+-------------------------------------+-----------------------------------------------------------------------------------------------------+
|Status                 |DevVoid                                    |DevString                            |Return the device state as a string                                                                  |
+-----------------------+-------------------------------------------+-------------------------------------+-----------------------------------------------------------------------------------------------------+
|getAttrStringValueList |DevString:				    |DevVarStringArray:			  |		                                                                                        |
|			|Attribute name		                    |String value list			  |Return the authorized string value list for a given attribute name                                   |
+-----------------------+-------------------------------------------+-------------------------------------+-----------------------------------------------------------------------------------------------------+
|prepareAcq             |DevVoid                                    |DevVoid                              |Prepare the camera for a new acquisition, has to be called each time a parameter is set.             |
+-----------------------+-------------------------------------------+-------------------------------------+-----------------------------------------------------------------------------------------------------+
|startAcq               |DevVoid                                    |DevVoid                              |Start the acquisition                                                                                |
+-----------------------+-------------------------------------------+-------------------------------------+-----------------------------------------------------------------------------------------------------+
|stopAcq                |DevVoid                                    |DevVoid                              |Stop the acquisition                                                                                 |
+-----------------------+-------------------------------------------+-------------------------------------+-----------------------------------------------------------------------------------------------------+
|setImageHeader         |DevVarStringArray:                         |					  |		                                                                                        |
|                       |Array of string header                     |DevVoid                              |Set the image header:                                                                                |
|			|					    |                                     | - [0]="ImageId0 delimiter imageHeader0,                                                             |
|			|					    |					  | - [1] = ImageId1 delimiter  imageHeader1..                                                          |
+-----------------------+-------------------------------------------+-------------------------------------+-----------------------------------------------------------------------------------------------------+
|getImage               |DevLong: Image number(0-N)                 |DevVarCharArray: Image data          |Return the image data in raw format (char array)                                                     |
+-----------------------+-------------------------------------------+-------------------------------------+-----------------------------------------------------------------------------------------------------+
|closeShutterManual     |DevVoid                                    |DevVoid                              |N/A for Maxipix                                                                                      |
+-----------------------+-------------------------------------------+-------------------------------------+-----------------------------------------------------------------------------------------------------+
|openShutterManual      |DevVoid                                    |DevVoid                              |N/A for Maxipix                                                                                      |
+-----------------------+-------------------------------------------+-------------------------------------+-----------------------------------------------------------------------------------------------------+
|reset                  |DevVoid                                    |DevVoid                              |Reset the camera to factory setting                                                                  |
+-----------------------+-------------------------------------------+-------------------------------------+-----------------------------------------------------------------------------------------------------+


Attributes
''''''''''

======================= ======= ======================= ==============================================================
Attribute name		RW	Type			Description
======================= ======= ======================= ==============================================================
lima_type		ro	DevString		LImA camera type: 
							Maxipix,Pilatus,Frelon,Pco, Basler ...
camera_model		ro	DevString		Camera model return by the detector layer:.e.g. 5x1- TPX1
acq_status		ro	DevString		Acquisition status: Ready, Running, Fault
acq_mode		rw	DevString		Acquisition mode:

							 - **Single**, default mode one frame per image
							 - **Concatenation**, frames are concatenated in image
							 - **Accumulation**, powerful mode to avoid saturation 
							   of the pixel, the exposure is shared
							   by multiple frames, see acc\_ attributes for more
acq_nb_frames		rw	DevLong			Number of frames to be acquired, Default is 1 frame
acq_trigger_mode	rw	DevString		Trigger mode:
							 - **Internal_tirgger**, the software trigger, 
							   start the acquisition immediately after an acqStart() call,
							   all the acq_nb_frames are acquired in an sequence.
							 - **External_trigger**, wait for an external trigger signal 
							   to start the an acquisition for the acq_nb_frames number 
							   of frames.
							 - **External_trigger_multi**, as the previous mode except 
							   that each frames need a new trigger input 
							   (e.g. for 4 frames 4 pulses are waiting for)
							 - **Internal_trigger_multi**, as for internal_trigger except 
							   that for each frame the acqStart() has to called once.
							 - **External_gate**, wait for a gate signal for each frame, 
							   the gate period is the exposure time.
							 - **External_start_stop**

latency_time		rw	DevDouble		Latency time in second between two frame acquisitions,
							can not be zero, the minimum time corresponds to the
							readout time of the detector.
acq_expo_time		rw	DevDouble		The exposure time of the image, Default is 1 second
acc_expotime		ro	DevDouble		The effective accumulation total exposure time.
acc_nb_frames		ro	DevLong			The calculated accumulation number of frames per
							image.
acc_max_expotime	rw	DevDouble		The maximum exposure time per frame for accumulation
acc_time_mode		rw	DevString		Accumulation time mode:
							 - **Live**,acq_expo_time = acc_live_time
							 - **Real**,acq_expo_time = acc_dead_time + acc_live_time
acc_dead_time		ro	DevDouble		Total accumulation dead time
acc_live_time		ro	DevDouble		Total accumulation live time which corresponds to the
							detector total counting time.
image_type		ro	DevString		Return the current image data type, bit per pixel signed
							or unsigned:
							Bpp8, Bpp8S, Bpp10, Bpp10S, Bpp12, Bpp12S, Bpp14,
							Bpp14S, Bpp16, Bpp16S, Bpp32, Bpp32S.
image_width		ro	DevLong			Width size of the detector in pixel
image_height		ro	DevLong			Height size of the detector in pixel
image_roi		rw	Spectrum		Region Of Interest on image, [0] = Begin X, [1] = End X,
				DevLong			[2] Begin Y, [3] = End Y, default ROI is [0,0,0,0] (no ROI)
image_bin		rw	Spectrum		Binning on image, [0] = Binning factor on X, [1] =
				DevLong			Binning factor on Y. Default binning is 1 x 1
image_flip		rw	Spectrun		Flip on the image, [0] = flip over X axis, [1] flip over Y
				DevBoolean		axis. Default flip is False x False
shutter_mode		rw	DevString		Using the external shutter output to synchronize a
							shutter with the acquisition several modes are available:

							 - **Manual**
							 - **Auto_frame**, the output signal is activated for
							   each individual frame of a sequence
							 - **Auto_sequence**, the output signal is activated
							   during the whole sequence
shutter_open_time	rw	DevDouble		delay (sec.) between the output shutter trigger and the
							beginning of the acquisition, if not null the shutter signal
							is set on before the acquisition is started.
shutter_close_time	rw	DevDouble		delay (sec.) between the shutter trigger and the end of
							the acquisition, if not null the shutter signal is set on
							before the end of the acquisition.
saving_mode		rw	DevString		Saving mode:

							 - **Manual**, no automatic saving, a command will
							   be implemented in a next release to be able to
							   save an acquired image.
							 - **Auto_Frame**, Frames are automatically saved
							   according the saving parameters (see below).
							 - **Auto_header**, Frames are only saved when the
							   setImageHeader() is called in order to set
							   header information with image data.
saving_directory	rw	DevString		The directory where to save the image files
saving_prefix		rw	DevString		The image file prefix
saving_suffix		rw	DevString		The image file suffix
saving_next_number	rw	DevLong			The image next number:
							The full image file name is:
							/saving_directory/saving_prefix+sprintf("%04d",
							saving_next_number)+saving_suffix
							Default is 0
saving_format		rw	DevString		The data format for saving:

							 - **Raw**, save in binary format
							 - **Edf**, save in ESRF Data Format
							 - **Cbf**, save in CBF format (a compressed format
							   for crystallography)
saving_overwrite_policy	rw	DevString		In case of existing files an overwite policy is mandatory:

							- **Abort**, if the file exists the saving is aborted
							- **Overwrite**, if the file exists it is overwritten
							- **Append**, if the file exists the image is append
							  to the file
saving_frame_per_file	rw	DevLong			Number of frames saved in each file
saving_common_header	rw	Spectrum		Common header with multiple entries
				DevString
saving_header_delimiter rw	Spectrum		The header delimiters, [0] = key header delimiter, [1] =
				DevString		entry header delimiter, [2] = image number header
							delimiter. Default : [0] = "=", [1] = "\n", [2] = ";"
last_image_ready	ro	DevLong			The last acquired image number, ready for reading
last_image_saved	ro	DevLong			The last saved image number
ready_for_next_image	ro	DevBoolean		True after a camera readout, otherwise false. Can be
							used for fast synchronisation with trigger mode (internal
							or external).
ready_for_next_acq	ro	DevBoolean		True after end of acquisition, otherwise false.

write_statistic		ro	Spectrum		performance writing time for last images in second.
				DevDouble
debug_modules		rw	Spectrun		Set the debug module level of LImA:
				DevString		
							 - "None"
							 - "Common"
							 - "Hardware"
							 - "HardwareSerial"
							 - "Control"
							 - "Espia"
							 - "EspiaSerial"
							 - "Focla"
							 - "Camera"
							 - "CameraCom"
							 - "Test"
							 - "Application"
debug_types		rw	Spectrum		Set the debug type level of LImA:
				DevString 
							 - "Fatal"
							 - "Error"
							 - "Warning"
							 - "Trace"
							 - "Funct"
							 - "Param"
							 - "Return"
							 - "Always"
======================= ======= ======================= ==============================================================


Property
''''''''
======================= =============== =============== ============================
Property name		Mandatory	Default value	Description
======================= =============== =============== ============================
LimaCameraType		Yes		N/A		The camera type: e.g. Maxipix
======================= =============== =============== ============================


Configuration device
--------------------

.. toctree::
  :maxdepth: 2

  basler
  frelon
  maxipix
  pilatus
  prosilica 
  andor

Calculation devices
-------------------

