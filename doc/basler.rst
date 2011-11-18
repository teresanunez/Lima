Basler
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
=======================	=============== =======================	===========================================


Properties
----------

=============== =============== =============== ==============================================================
Property name	Mandatory	Default value	Description
=============== =============== =============== ==============================================================
cam_ip_address	Yes		N/A		The camera's ip or hostname 
packet_size	No		8000		Suppose that eth MTU is set at least to 8192 (Jumbo mode !).
						if you want default Basler packet size set it to -1
=============== =============== =============== ==============================================================
