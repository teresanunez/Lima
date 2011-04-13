Pilatus
=======


Commands
--------

=======================	=============== =======================	======================================
Command name		Arg. in		Arg. out		Description
=======================	=============== =======================	======================================
Init			DevVoid 	DevVoid			Do not use
State			DevVoid		DevLong			Return the device state
Status			DevVoid		DevString		Return the device state as a string
getAttrStringValueList	DevString:	DevVarStringArray:	Return the authorized string value list for
			Attribute name	String value list	a given attribute name
=======================	=============== =======================	======================================

Attributes
----------
======================= ======= ======================= ============================================================
Attribute name		RW	Type			Description
======================= ======= ======================= ============================================================
threshold_gain		rw	DevString		the detector threshold gain (**LOW,MID,HIGH,ULTRA HIGH**)
fill_mode		rw	DevString		the gap fill mode (**ON,OFF**)
threshold		rw	DevLong			the threshold level of detector in eV
energy_threshold	rw	DevFloat		the energy threshold in keV (set the gain and the threshold)
trigger_delay		rw	DevDouble		the start exposure delay after the hard trigger
======================= ======= ======================= ============================================================
