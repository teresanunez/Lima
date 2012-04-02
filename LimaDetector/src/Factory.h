#ifndef _FACTORY_H_
#define _FACTORY_H_


#include <Singleton.h>

#include <HwInterface.h>
#include <CtControl.h>
#include "Debug.h"
#include <yat/threading/Mutex.h>

#include <tango.h>


#ifdef SIMULATOR_ENABLED
#include <SimulatorInterface.h>
#endif

#ifdef BASLER_ENABLED  
#include <BaslerInterface.h>
#endif

#ifdef XPAD_ENABLED
#include <XpadInterface.h>
#endif

#ifdef PILATUS_ENABLED
#include <PilatusInterface.h>
#endif

#ifdef MARCCD_ENABLED
#include <MarccdInterface.h>
#endif

#ifdef ADSC_ENABLED
#include <AdscInterface.h>
#endif

#ifdef PROSILICA_ENABLED
    #include <ProsilicaInterface.h>
    #include <ProsilicaCamera.h>
    #include <ProsilicaDetInfoCtrlObj.h>
    #include <ProsilicaBufferCtrlObj.h>
    #include <ProsilicaVideoCtrlObj.h>
    #include <ProsilicaSyncCtrlObj.h>   
#endif

using namespace lima;
using namespace std;
using namespace Tango;

class ControlFactory : public Singleton<ControlFactory>
{
public:

	CtControl*                     get_control( const string& detector_type);
	void                           reset(const string& detector_type );
	void                           init_specific_device(const string& detector_type );

private:  
#ifdef SIMULATOR_ENABLED
	Simulator::Camera*             my_camera_simulator;
	Simulator::Interface*          my_interface_simulator;
#endif

#ifdef BASLER_ENABLED  
	Basler::Camera*                my_camera_basler;
	Basler::Interface*             my_interface_basler;
#endif

#ifdef XPAD_ENABLED
	Xpad::Camera*                  my_camera_xpad;
	Xpad::Interface*               my_interface_xpad;
#endif

#ifdef PILATUS_ENABLED      
	Pilatus::Camera*            my_camera_pilatus;  
	Pilatus::Interface*         my_interface_pilatus;  
#endif

#ifdef MARCCD_ENABLED      
	Marccd::Camera*     			my_camera_marccd;  
	Marccd::Interface*         		my_interface_marccd;  
#endif

#ifdef ADSC_ENABLED      
	Adsc::Camera*     				my_camera_adsc;  
	Adsc::Interface*         		my_interface_adsc;  
#endif

#ifdef PROSILICA_ENABLED      
  Prosilica::Camera*             my_camera_prosilica;  
  Prosilica::Interface*          my_interface_prosilica;  
#endif
	CtControl*                     my_control;
	static bool                    is_created;
	string                         my_server_name;  
	string                         my_device_name;

	//lock the singleton acess
	yat::Mutex 								    object_lock;  

};

#endif

