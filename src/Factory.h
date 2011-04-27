#ifndef _FACTORY_H_
#define _FACTORY_H_

#include <tango.h>
#include <Singleton.h>

#include <HwInterface.h>
#include <CtControl.h>
#include <SimuHwInterface.h>
#include <BaslerInterface.h>
#include <XpadInterface.h>

using namespace lima;
using namespace std;

class ControlFactory : public Singleton<ControlFactory>
{
public:

  CtControl* 			get_control( const string& detector_type, const string& camera_ip = "0.0.0.0", bool is_master = true);
  void 					reset(const string& detector_type );
  
private:  
  Simulator* 			my_camera_simulator;
  Basler::Camera* 		my_camera_basler;
  XpadCamera*			my_xpad_camera;
  
  XpadInterface*		my_xpad_interface;
  Basler::Interface* 	my_interface_basler;
  SimuHwInterface* 		my_interface_simulator;

  CtControl* 			my_control;
  static bool 			is_created;

};


#endif
