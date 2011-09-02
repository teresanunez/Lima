#include <Factory.h>

#include <iostream>

bool  ControlFactory::is_created = false;


//-----------------------------------------------------------------------------------------
CtControl* ControlFactory::get_control( const string& detector_type)
{
    yat::MutexLock scoped_lock(object_lock);
    try
    {		
        //get the tango device/instance
        if(!ControlFactory::is_created)
        {    
            string  detector = detector_type;
            DbDatum db_datum;
            my_server_name = Tango::Util::instance()->get_ds_name ();
            db_datum = (Tango::Util::instance()->get_database())->get_device_name(my_server_name,detector);
            db_datum >> my_device_name;
        }

#ifdef SIMULATOR_ENABLED
        if (detector_type.compare("SimulatorCCD")== 0)
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
#endif

#ifdef BASLER_ENABLED
        if (detector_type.compare("BaslerCCD")== 0)
        {    
            if(!ControlFactory::is_created)
            {                
                DbData db_data;
                db_data.push_back(DbDatum("DetectorIP"));
                (Tango::Util::instance()->get_database())->get_device_property(my_device_name, db_data);
                string camera_ip;
                db_data[0] >> camera_ip;
                
                my_camera_basler            = new Basler::Camera(camera_ip);
                my_interface_basler         = new Basler::Interface(*my_camera_basler);
                my_control                  = new CtControl(my_interface_basler);
                ControlFactory::is_created  = true;                
                return my_control;
            }
        }
#endif

#ifdef XPAD_ENABLED
        if (detector_type.compare("XpadPixelDetector")== 0)
        {    
        
            if(!ControlFactory::is_created)
            {
				my_camera_xpad                = new Xpad::Camera();
                my_camera_xpad->go(2000);
				my_interface_xpad             = new Xpad::Interface(*my_camera_xpad);
                my_control                    = new CtControl(my_interface_xpad);
                ControlFactory::is_created    = true;
                return my_control;
            }
        }
#endif

#ifdef PILATUS_ENABLED
        if (detector_type.compare("PilatusPixelDetector")== 0)
        {    
        
            if(!ControlFactory::is_created)
            {                
                DbData db_data;
                db_data.push_back(DbDatum("DetectorIP"));
                db_data.push_back(DbDatum("DetectorPort"));
                (Tango::Util::instance()->get_database())->get_device_property(my_device_name, db_data);
                string camera_ip;
                long camera_port;
                db_data[0] >> camera_ip;
                db_data[1] >> camera_port;
                
                my_camera_pilatus           = new PilatusCpp::Camera(camera_ip.c_str(), camera_port);
                my_interface_pilatus        = new PilatusCpp::Interface(*my_camera_pilatus);
                my_control                  = new CtControl(my_interface_pilatus);
                ControlFactory::is_created  = true;
                return my_control;
            }
        }
#endif

#ifdef MARCCD_ENABLED	
		if (detector_type.compare("MarCCD")== 0)
		{	
			if(!ControlFactory::is_created)
			{
				DbData db_data;
				db_data.push_back(DbDatum("DetectorIP"));
				db_data.push_back(DbDatum("DetectorPort"));
				db_data.push_back(DbDatum("FullImagePathName"));
				(Tango::Util::instance()->get_database())->get_device_property(my_device_name, db_data);
				string camera_ip;
				string full_img_path_name;
				unsigned long camera_port;
				db_data[0] >> camera_ip;
				db_data[1] >> camera_port;
				db_data[2] >> full_img_path_name;

				my_camera_marccd           = new Marccd::MarccdCamera(camera_ip.c_str(), camera_port, full_img_path_name);
				my_camera_marccd->go(2000);        
				my_interface_marccd        = new Marccd::Interface(*my_camera_marccd);
				my_control                 = new CtControl(my_interface_marccd);
				ControlFactory::is_created = true;
				return my_control;
			}
		}
#endif
        
        if(!ControlFactory::is_created)
            throw LIMA_HW_EXC(Error, "Unable to create the lima control object : Unknown Detector Type");
        
    }
    catch(Tango::DevFailed& df)
    {
        //- rethrow exception
        throw LIMA_HW_EXC(Error, string(df.errors[0].desc).c_str());
    }    
    catch(Exception& e)
    {
        throw LIMA_HW_EXC(Error, e.getErrMsg());
    }    
    catch(...)
    {
        throw LIMA_HW_EXC(Error, "Unable to create the lima control object : Unknow Exception");
    }
    return my_control;
}


//-----------------------------------------------------------------------------------------
void ControlFactory::reset(const string& detector_type )
{
    yat::MutexLock scoped_lock(object_lock);
    try
    {
        if(ControlFactory::is_created)
        {    
            ControlFactory::is_created = false;        
            delete my_control;                my_control = 0;     
             
#ifdef SIMULATOR_ENABLED
            if (detector_type.compare("SimulatorCCD")== 0)
            {
                my_camera_simulator->reset(); 
                delete my_camera_simulator;     my_camera_simulator = 0;  
                delete my_interface_simulator;  my_interface_simulator = 0;
            }
#endif        
    
#ifdef BASLER_ENABLED
            if (detector_type.compare("BaslerCCD")==0)
            {                
                my_camera_basler->reset();
                delete my_camera_basler;        my_camera_basler = 0;
                delete my_interface_basler;     my_interface_basler = 0;
            }
#endif
    
#ifdef XPAD_ENABLED
            if (detector_type.compare("XpadPixelDetector")==0)
            {          
                //- do not delete because its a YAT Task
                my_camera_xpad->exit();       my_camera_xpad = 0;
                delete my_interface_xpad;     my_interface_xpad = 0;
            }
#endif
    
#ifdef PILATUS_ENABLED
            if (detector_type.compare("PilatusPixelDetector")==0)
            {          
                delete my_camera_pilatus;        my_camera_pilatus = 0;
                delete my_interface_pilatus;     my_interface_pilatus = 0;
            }
#endif

#ifdef MARCCD_ENABLED
            if (detector_type.compare("MarCCD")==0)
            {          
				//- do not delete because its a YAT Task
                my_camera_marccd->exit();        my_camera_marccd = 0;
                delete my_interface_marccd;		 my_interface_marccd = 0;
            }
#endif     
        }
    }
    catch(Tango::DevFailed& df)
    {
        //- rethrow exception
        throw LIMA_HW_EXC(Error, string(df.errors[0].desc).c_str());
    }    
    catch(Exception& e)
    {
        throw LIMA_HW_EXC(Error, e.getErrMsg());
    }    
    catch(...)
    {
        throw LIMA_HW_EXC(Error, "reset : Unknow Exception");
    }    
}

//-----------------------------------------------------------------------------------------
//- force Init() on the specific device.
//-----------------------------------------------------------------------------------------
void ControlFactory::init_specific_device(const string& detector_type )
{
    yat::MutexLock scoped_lock(object_lock);    
    try
    {
        //get the tango device/instance
        if(!ControlFactory::is_created)
        {    
            string  detector = detector_type;
            DbDatum db_datum;
            my_server_name = Tango::Util::instance()->get_ds_name ();
            db_datum = (Tango::Util::instance()->get_database())->get_device_name(my_server_name,detector);
            db_datum >> my_device_name;
        }

        (Tango::Util::instance()->get_device_by_name(my_device_name))->delete_device();
        (Tango::Util::instance()->get_device_by_name(my_device_name))->init_device();
    }
    catch(Tango::DevFailed& df)
    {
        //- rethrow exception
        throw LIMA_HW_EXC(Error, string(df.errors[0].desc).c_str());
    }

}
//-----------------------------------------------------------------------------------------




