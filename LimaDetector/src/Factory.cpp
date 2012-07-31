#include <Factory.h>

#include <iostream>

bool  ControlFactory::is_created = false;


//-----------------------------------------------------------------------------------------
ControlFactory::ControlFactory()
{
	my_control				= 0;

#ifdef SIMULATOR_ENABLED
	my_camera_simulator 	= 0;
	my_interface_simulator 	= 0;
#endif

#ifdef BASLER_ENABLED
	my_camera_basler 		= 0;
	my_interface_basler 	= 0;
#endif

#ifdef XPAD_ENABLED
	my_camera_xpad 			= 0;
	my_interface_xpad 		= 0;
#endif

#ifdef PILATUS_ENABLED
	my_camera_pilatus 		= 0;
	my_interface_pilatus 	= 0;
#endif

#ifdef MARCCD_ENABLED
	my_camera_marccd 		= 0;
	my_interface_marccd 	= 0;
#endif

#ifdef ADSC_ENABLED
	my_camera_adsc 			= 0;
	my_interface_adsc 		= 0;
#endif

#ifdef PROSILICA_ENABLED
	my_camera_prosilica 	= 0;
	my_interface_prosilica 	= 0;
#endif

#ifdef PRINCETON_ENABLED
	my_camera_princeton 	= 0;
	my_interface_princeton 	= 0;
#endif

	my_server_name 			= "none";
	my_device_name 			= "none";
	
	my_status.str("");
	my_state 				= Tango::INIT;
}

//-----------------------------------------------------------------------------------------
CtControl* ControlFactory::get_control( const std::string& detector_type)
{
    yat::MutexLock scoped_lock(object_lock);
    try
    {
        //get the tango device/instance
        if(!ControlFactory::is_created)
        {
            std::string  detector = detector_type;
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
                my_camera_simulator         = new Simulator::Camera();
                my_interface_simulator      = new Simulator::Interface(*my_camera_simulator);
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
                db_data.push_back(DbDatum("DetectorTimeout"));
                db_data.push_back(DbDatum("DetectorPacketSize"));
                (Tango::Util::instance()->get_database())->get_device_property(my_device_name, db_data);
                std::string camera_ip;
                db_data[0] >> camera_ip;
                short detector_timeout = 11000;
                db_data[1] >> detector_timeout;
                long packet_size = -1;
                db_data[2] >> packet_size;
                my_camera_basler            = new Basler::Camera(camera_ip, packet_size);
                my_interface_basler         = new Basler::Interface(*my_camera_basler);
                if(my_interface_basler)
                	my_interface_basler->setTimeout(detector_timeout);
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
            	DbData db_data;
				db_data.push_back(DbDatum("XpadModel"));
				(Tango::Util::instance()->get_database())->get_device_property(my_device_name, db_data);
				std::string xpad_model;
				db_data[0] >> xpad_model;
				my_camera_xpad                = new Xpad::Camera(xpad_model);
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
                db_data.push_back(DbDatum("UseReader"));
                (Tango::Util::instance()->get_database())->get_device_property(my_device_name, db_data);
                std::string camera_ip;
                long camera_port;
                bool use_reader;
                db_data[0] >> camera_ip;
                db_data[1] >> camera_port;
                db_data[2] >> use_reader;

                my_camera_pilatus           = new Pilatus::Camera(camera_ip.c_str(), camera_port);
                if(my_camera_pilatus && use_reader)
                	my_camera_pilatus->enableDirectoryWatcher();
                if(my_camera_pilatus && !use_reader)
                	my_camera_pilatus->disableDirectoryWatcher();
                my_interface_pilatus        = new Pilatus::Interface(*my_camera_pilatus);
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
          db_data.push_back(DbDatum("DetectorTargetPath"));
          db_data.push_back(DbDatum("ReaderTimeout"));
          db_data.push_back(DbDatum("UseReader"));

          (Tango::Util::instance()->get_database())->get_device_property(my_device_name, db_data);
          std::string camera_ip;
          std::string img_path;
          unsigned long camera_port = 2222;
          unsigned short reader_timeout = 10000;
          bool use_reader = true;

          db_data[0] >> camera_ip;
          db_data[1] >> camera_port;
          db_data[2] >> img_path;
          db_data[3] >> reader_timeout;
          db_data[4] >> use_reader;

          my_camera_marccd           = new Marccd::Camera(camera_ip.c_str(), camera_port, img_path);
          my_camera_marccd->go(2000);
          my_interface_marccd        = new Marccd::Interface(*my_camera_marccd);
          if(my_interface_marccd && use_reader)
        	  my_interface_marccd->enableReader();
          if(my_interface_marccd && !use_reader)
        	  my_interface_marccd->disableReader();
          if(my_interface_marccd)
        	  my_interface_marccd->setTimeout(reader_timeout);
          my_control                 = new CtControl(my_interface_marccd);
          ControlFactory::is_created = true;
          return my_control;
        }
      }
#endif

#ifdef ADSC_ENABLED
        if (detector_type.compare("AdscCCD")== 0)
        {

            if(!ControlFactory::is_created)
            {
                DbData db_data;
                db_data.push_back(DbDatum("ReaderTimeout"));
                db_data.push_back(DbDatum("UseReader"));
                (Tango::Util::instance()->get_database())->get_device_property(my_device_name, db_data);
                short reader_timeout = 1000;
                bool use_reader;
                db_data[0] >> reader_timeout;
                db_data[1] >> use_reader;
            	my_camera_adsc                = new Adsc::Camera();
                my_interface_adsc             = new Adsc::Interface(*my_camera_adsc);
                if(my_interface_adsc && use_reader)
                	my_interface_adsc->enableReader();
                if(my_interface_adsc && !use_reader)
                	my_interface_adsc->disableReader();
                if(my_interface_adsc)
                	my_interface_adsc->setTimeout(reader_timeout);
                my_control                    = new CtControl(my_interface_adsc);
                ControlFactory::is_created    = true;
                return my_control;
            }
        }
#endif        

#ifdef PROSILICA_ENABLED
        if (detector_type.compare("ProsilicaCCD")== 0)
        {

            if(!ControlFactory::is_created)
            {
				DbData db_data;
				db_data.push_back(DbDatum("DetectorIP"));
				(Tango::Util::instance()->get_database())->get_device_property(my_device_name, db_data);
				std::string camera_ip;
				db_data[0] >> camera_ip;

				my_camera_prosilica           	= new Prosilica::Camera(camera_ip.c_str());
                my_interface_prosilica        	= new Prosilica::Interface(my_camera_prosilica);
                my_control                  	= new CtControl(my_interface_prosilica);
                ControlFactory::is_created  	= true;
                return my_control;
            }
        }
#endif

#ifdef PRINCETON_ENABLED
        if (detector_type.compare("PrincetonCCD")== 0)
        {

            if(!ControlFactory::is_created)
            {
				DbData db_data;
				db_data.push_back(DbDatum("DetectorNum"));
				(Tango::Util::instance()->get_database())->get_device_property(my_device_name, db_data);
				long camera_num;
				db_data[0] >> camera_num;
				my_camera_princeton           	= new RoperScientific::Camera(camera_num);
                my_interface_princeton        	= new RoperScientific::Interface(*my_camera_princeton);
                my_control                  	= new CtControl(my_interface_princeton);
                ControlFactory::is_created  	= true;
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
        throw LIMA_HW_EXC(Error, std::string(df.errors[0].desc).c_str());
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
void ControlFactory::reset(const std::string& detector_type )
{
    yat::MutexLock scoped_lock(object_lock);
    try
    {
        if(ControlFactory::is_created)
        {
            ControlFactory::is_created = false;
            if(my_control)
            {
            	delete my_control;
            	my_control = 0;
            }

#ifdef SIMULATOR_ENABLED
            if (detector_type.compare("SimulatorCCD")== 0)
            {
                if(my_camera_simulator)
                {
                	delete my_camera_simulator;
                	my_camera_simulator = 0;
                }

                if(my_interface_simulator)
                {
                	delete my_interface_simulator;
                	my_interface_simulator = 0;
                }
            }
#endif        

#ifdef BASLER_ENABLED
            if (detector_type.compare("BaslerCCD")==0)
            {
                if(my_camera_basler)
                {
                	delete my_camera_basler;
                	my_camera_basler = 0;
                }

                if(my_interface_basler)
                {
                	delete my_interface_basler;
                	my_interface_basler = 0;
                }
            }
#endif

#ifdef XPAD_ENABLED
            if (detector_type.compare("XpadPixelDetector")==0)
            {
                if(my_camera_xpad)
                {
                	//- do not delete because its a YAT Task
                	my_camera_xpad->exit();
                	my_camera_xpad = 0;
                }

                if(my_interface_xpad)
                {
                	delete my_interface_xpad;
                	my_interface_xpad = 0;
                }
            }
#endif

#ifdef PILATUS_ENABLED
            if (detector_type.compare("PilatusPixelDetector")==0)
            {
                if(my_camera_pilatus)
                {
                	delete my_camera_pilatus;
                	my_camera_pilatus = 0;
                }

                if(my_interface_pilatus)
                {
                	delete my_interface_pilatus;
                	my_interface_pilatus = 0;
                }
            }
#endif

#ifdef MARCCD_ENABLED
            if (detector_type.compare("MarCCD")==0)
            {
                if(my_camera_marccd)
                {
                	//- do not delete because its a YAT Task
                	my_camera_marccd->exit();
                	my_camera_marccd = 0;
                }

                if(my_interface_marccd)
                {
                	delete my_interface_marccd;
                	my_interface_marccd = 0;
                }
            }
#endif     

#ifdef ADSC_ENABLED
            if (detector_type.compare("AdscCCD")==0)
            {
                if(my_camera_adsc)
                {
                	delete my_camera_adsc;
                	my_camera_adsc = 0;
                }

                if(my_interface_adsc)
                {
                	delete my_interface_adsc;
                	my_interface_adsc = 0;
                }
            }
#endif

#ifdef PROSILICA_ENABLED
        if (detector_type.compare("ProsilicaCCD")==0)
        {
            if(my_camera_prosilica)
            {
            	delete my_camera_prosilica;
            	my_camera_prosilica = 0;
            }

            if(my_interface_prosilica)
            {
            	delete my_interface_prosilica;
            	my_interface_prosilica = 0;
            }
        }
#endif

#ifdef PRINCETON_ENABLED
        if (detector_type.compare("PrincetonCCD")==0)
        {
            if(my_interface_princeton)
            {
            	delete my_interface_princeton;
            	my_interface_princeton = 0;
            }
			
			if(my_camera_princeton)
            {
            	delete my_camera_princeton;
            	my_camera_princeton = 0;
            }
        }
#endif
        }
    }
    catch(Tango::DevFailed& df)
    {
        //- rethrow exception
        throw LIMA_HW_EXC(Error, std::string(df.errors[0].desc).c_str());
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
void ControlFactory::init_specific_device(const std::string& detector_type )
{
    yat::MutexLock scoped_lock(object_lock);
    try
    {
        //get the tango device/instance
        if(!ControlFactory::is_created)
        {
            std::string  detector = detector_type;
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
        throw LIMA_HW_EXC(Error, std::string(df.errors[0].desc).c_str());
    }
}

//-----------------------------------------------------------------------------------------
//- call dev_state() command of the generic device.
//-----------------------------------------------------------------------------------------
Tango::DevState ControlFactory::get_state(void )
{
	yat::AutoMutex<> _lock(object_state_lock);
	return my_state;
}
//-----------------------------------------------------------------------------------------
//- call dev_status() command of the generic device.
//-----------------------------------------------------------------------------------------
std::string 	ControlFactory::get_status(void )
{
	yat::AutoMutex<> lock(object_state_lock);
	return (my_status.str());

}
//-----------------------------------------------------------------------------------------
void ControlFactory::set_state(Tango::DevState state) 
{
	yat::AutoMutex<> _lock(object_state_lock);
    my_state = state;
}

//-----------------------------------------------------------------------------------------
void ControlFactory::set_status (const std::string& status)
{      
	yat::AutoMutex<> _lock(object_state_lock);
    my_status.str("");
    my_status<<status.c_str()<<endl;

}
//-----------------------------------------------------------------------------------------


