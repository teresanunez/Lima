.. image:: ../../../camera/pco/doc/Under_cons.jpg

PCO
===

Commands
--------

======================= =============== ======================= ===========================================
Command name            Arg. in         Arg. out                Description
======================= =============== ======================= ===========================================
Init                    DevVoid         DevVoid                 Do not use
State			DevVoid		DevLong			Return the device state
Status			DevVoid		DevString		Return the device state as a string
getAttrStringValueList	DevString:	DevVarStringArray:	Return the authorized string value list for
			Attribute name	String value list	a given attribute name
=======================	=============== =======================	===========================================


Attributes
----------

======================= ======= ======================= ======================================================================
Attribute name          RW      Type                    Description
======================= ======= ======================= ======================================================================
rollingShutter          rw      DevString		TODO ...
							 - **On**, the cooler is started
							 - **Off**, the cooler is stopped 	
lastError		ro	DevString		TODO ... 
camInfo 		ro	DevString		TODO ...
camType 		ro	DevString		TODO ...
clXferPar 		ro	DevString		TODO ...
cocRunTime 		ro	DevString		TODO ...
frameRate 		ro	DevString		TODO ...
pixelRate 		ro	DevString		TODO ...
maxNbImages             ro	DevString		TODO ...
info     		ro	DevString		TODO ...
version     		ro	DevString		TODO ...
======================= ======= ======================= ======================================================================


Properties
----------

=============== =============== =============== ==============================================================
Property name	Mandatory	Default value	Description
=============== =============== =============== ==============================================================
ident   	TODO ...	TODO ...		TODO ...	
=============== =============== =============== ==============================================================
