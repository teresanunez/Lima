#ifndef _FACTORY_H_
#define _FACTORY_H_

#include <tango.h>
#include <Singleton.h>

#include <HwInterface.h>
#include <CtControl.h>
#include <SimuHwInterface.h>
#include "Debug.h"

#ifdef BASLER_ENABLED  
	#include <BaslerInterface.h>
#endif

#ifdef XPAD_ENABLED
	#include <XpadInterface.h>
#endif

#ifdef PILATUS_ENABLED
	#include <PilatusInterface.h>
#endif

using namespace lima;
using namespace std;

class ControlFactory : public Singleton<ControlFactory>
{
public:

  CtControl* 			        get_control( const string& detector_type, const string& camera_ip = "0.0.0.0", int camera_port = -1, bool is_master = false);
  void 					        reset(const string& detector_type );
  
private:  
  Simulator* 				    my_camera_simulator;
  SimuHwInterface* 			    my_interface_simulator;

#ifdef BASLER_ENABLED  
  Basler::Camera* 			    my_camera_basler;
  Basler::Interface* 		    my_interface_basler;
#endif

#ifdef XPAD_ENABLED
  XpadCamera*				    my_xpad_camera;
  XpadInterface*			    my_xpad_interface;
#endif

#ifdef PILATUS_ENABLED	  
  PilatusCpp::Communication*	my_camera_pilatus;  
  PilatusCpp::Interface* 	    my_interface_pilatus;  
#endif

  CtControl* 		            my_control;
  static bool 		            is_created;

};

#endif

