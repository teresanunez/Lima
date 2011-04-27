#include <Factory.h>

#include <iostream>

bool  ControlFactory::is_created = false;

//-----------------------------------------------------------------------------------------
CtControl* ControlFactory::get_control( const string& detector_type, const string& camera_ip, bool is_master)
{

	//must be false for sub-devices BaslerCCD/Simulator/...
	if(!is_master)
		return my_control;

	if (detector_type.compare("Simulator")== 0)
	{	    
		if(!ControlFactory::is_created)
		{
			my_camera_simulator         = new Simulator();		
			my_interface_simulator      = new SimuHwInterface(*my_camera_simulator);
			my_control                  = new CtControl(my_interface_simulator);
			ControlFactory::is_created  = true;
			return my_control;      
		}
	}
	else if (detector_type.compare("Basler")== 0)
	{	

		if(!ControlFactory::is_created)
		{
			my_camera_basler            = new Basler::Camera(camera_ip);
			my_camera_basler->go(2000);
			my_interface_basler         = new Basler::Interface(*my_camera_basler);
			my_control                  = new CtControl(my_interface_basler);
			ControlFactory::is_created  = true;
			return my_control;
		}
	}
	else if (detector_type.compare("XpadPixelDetector")== 0)
	{	
	
		if(!ControlFactory::is_created)
		{
			my_xpad_camera				= new XpadCamera();
			my_xpad_camera->go(2000);
			my_xpad_interface			= new XpadInterface(*my_xpad_camera);
			my_control                  = new CtControl(my_xpad_interface);
			ControlFactory::is_created  = true;
			return my_control;
		}
	}
	else
	{
		//return 0 to indicate an ERROR
		return 0;
	}
	return my_control;
}


//-----------------------------------------------------------------------------------------
void ControlFactory::reset(const string& detector_type )
{
	if(ControlFactory::is_created)
	{    
		delete my_control;                my_control = 0;      
		if (detector_type.compare("Simulator")== 0)
		{
			my_camera_simulator->reset(); 
			delete my_camera_simulator;     my_camera_simulator = 0;  
			delete my_interface_simulator;  my_interface_simulator = 0;
		}
		else if (detector_type.compare("Basler")==0)
		{          
			//- do not delete because its a YAT Task			
			my_camera_basler->exit();       my_camera_basler = 0;
			delete my_interface_basler;     my_interface_basler = 0;
		}
		else if (detector_type.compare("XpadPixelDetector")==0)
		{          
			//- do not delete because its a YAT Task
			my_xpad_camera->exit();       my_xpad_camera = 0;
			delete my_xpad_interface;     my_xpad_interface = 0;
		}
		else
		{
			///
		}
		ControlFactory::is_created = false;        
	}
}
//-----------------------------------------------------------------------------------------

