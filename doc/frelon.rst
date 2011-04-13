Frelon
======

Commands
--------

=======================	=============== =======================	===========================================
Command name		Arg. in		Arg. out		Description
=======================	=============== =======================	===========================================
Init			DevVoid 	DevVoid			Do not use
State			DevVoid		DevLong			Return the device state
Status			DevVoid		DevString		Return the device state as a string
getAttrStringValueList	DevString:	DevVarStringArray:	Return the authorized string value list for
			Attribute name	String value list	a given attribute name
execSerialCommand	DevString	DevString		Send a command through the serial line
			command		command result 
=======================	=============== =======================	===========================================

Attributes
----------
======================= ======= ======================= ===========================================================
Attribute name		RW	Type			Description
======================= ======= ======================= ===========================================================
espia_dev_nb		ro	DevString		The Espia board number.
image_mode		rw	DevString		The acquisition image mode:
							 - **Frame transfert**
							 - **Full frame**
input_channel		rw	DevString		The Inputs ADC channels:
							 - **1**
							 - **2**
							 - **3**
							 - **4**
							 - **1-2**
							 - **3-4**
							 - **1-3**
							 - **2-4**
							 - **1-2-3-4**
e2v_correction		rw	DevString		Active/Desactive the corrstion for e2v cameras:
							 - **On**
							 - **Off**
roi_mode		rw	DevString		The roi mode:
							 - **None**
							 - **Slow**
							 - **Fast**
							 - **Kinetic**
roi_bin_offset		rw	DevLong			The roi offset in line
======================= ======= ======================= ===========================================================

Properties
----------

=============== =============== =============== ==============================================================
Property name	Mandatory	Default value	Description
=============== =============== =============== ==============================================================
espia_dev_nb	No		0		The acquisition Espia board number
=============== =============== =============== ==============================================================
