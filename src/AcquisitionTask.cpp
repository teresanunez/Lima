// ============================================================================
//
// = CONTEXT
//		DeviceTask attached to the Main device,
//
// = File
//		AcquisitionTask.cpp
//
// = AUTHOR
//		Arafat NOUREDDINE - SOLEIL (MEDIANE SYSTEME)
//
// ============================================================================
#include <yat/threading/Mutex.h>
#include <yat/time/Timer.h>
#include <Tools.h>
#include <AcquisitionTask.h>
					
namespace LimaDetector_ns {
// ============================================================================
// ctor
// ============================================================================	

AcquisitionTask::AcquisitionTask(Tango::DeviceImpl* dev) :
	yat4tango::DeviceTask(dev)
{
	INFO_STREAM << "AcquisitionTask::AcquisitionTask"<< endl;

	this->enable_timeout_msg(false);
	this->set_periodic_msg_period(kTASK_PERIODIC_TIMEOUT_MS);
	this->enable_periodic_msg(false);
	this->m_device = dev;
	this->m_status<<""<<endl;
	this->m_footer_status<<""<<endl;
	set_state(Tango::INIT);
	set_status("INIT");
}

// ============================================================================
// dtor
// ============================================================================	
AcquisitionTask::~AcquisitionTask() 
{
	INFO_STREAM << "AcquisitionTask::~AcquisitionTask"<< endl;

}

//=============================================================================
// exiter AcquisitionTask
//=============================================================================
void AcquisitionTask::Discard() const
{
   // Ugly method to call a no-const method from a const one
  ((AcquisitionTask*)((void*)this))->exit();
}

// ============================================================================
// Process the message queue of the Task
// ============================================================================	
void AcquisitionTask::process_message(yat::Message& msg) throw (Tango::DevFailed) 
{
	try
	{
		switch ( msg.type() )
		{
			//-----------------------------------------------------------------------------------------------
			case yat::TASK_INIT:
			{
				INFO_STREAM << "-> yat::TASK_INIT" << endl;

				try
				{
					m_acq_conf = msg.get_data<AcqConfig>();					
					set_state(Tango::STANDBY);	
					set_status(string("Waiting for request ..."));
				}
				catch( Tango::DevFailed& df )
				{
					ERROR_STREAM << df <<endl;
					set_state(Tango::FAULT);
					set_status(string(df.errors[0].desc));	
					throw;
				}
			}
			break;
				
			//-----------------------------------------------------------------------------------------------
			case yat::TASK_EXIT:
			{
				INFO_STREAM << "-> yat::TASK_EXIT" << endl;
				try
				{
					set_state(Tango::INIT);	
					set_status(string("Acquisition is Stopped."));	
				}
				catch( Tango::DevFailed& df )
				{
					ERROR_STREAM << df <<endl;
					set_state(Tango::FAULT);	
					set_status(string(df.errors[0].desc));
				}				
			}
			break;

			//-----------------------------------------------------------------------------------------------			
			case DEVICE_SNAP_MSG:
			{
				INFO_STREAM << "-> yat::DEVICE_SNAP_MSG" << endl;
				try
				{				
					set_state(Tango::RUNNING);	
					set_status(string("Acquisition is Running in snap mode..."));					

					m_acq_conf.ct->prepareAcq();
					m_acq_conf.ct->startAcq();
				}
				catch(Tango::DevFailed &df)
				{
					ERROR_STREAM << df << endl;
					on_abort(df);							
				}
				catch(Exception& e)
				{
					ERROR_STREAM << e.getErrMsg() << endl;
					on_abort(e.getErrMsg());							
				}					
			}
			break;
		
			//-----------------------------------------------------------------------------------------------			
			case DEVICE_START_MSG:
			{
				INFO_STREAM << "-> yat::DEVICE_START_MSG" << endl;
				try
				{				
					set_state(Tango::RUNNING);	
					set_status(string("Acquisition is Running in continuous mode ..."));					
					
					m_acq_conf.ct->prepareAcq();
					m_acq_conf.ct->startAcq();
				}
				catch(Tango::DevFailed &df)
				{
					ERROR_STREAM << df << endl;
					on_abort(df);							
				}
				catch(Exception& e)
				{
					ERROR_STREAM << e.getErrMsg() << endl;
					on_abort(e.getErrMsg());							
				}					
			}
			break;
		
			//----------------------------------------------------------------------------------------------- 
			case DEVICE_STOP_MSG:
			{
				INFO_STREAM << "-> yat::DEVICE_STOP_MSG" << endl;
				try
				{
					m_acq_conf.ct->stopAcq();
					set_state(Tango::STANDBY);
					set_status(string("Waiting for request ..."));				
					INFO_STREAM << "Acquisition is Stoped." << endl;
				}
				catch(Tango::DevFailed &df)
				{
					ERROR_STREAM << df << endl;
					on_abort(df);							
				}
				catch(Exception& e)
				{
					ERROR_STREAM << e.getErrMsg() << endl;
					on_abort(e.getErrMsg());							
				}					
			}
			break;
		
			//----------------------------------------------------------------------------------------------- 
			case DEVICE_ABORT_MSG:
			{
				INFO_STREAM << "-> yat::DEVICE_ABORT_MSG" << endl;
				//display here the final status, otherwise is overwrited.
				set_state(Tango::FAULT);
				set_status(m_acq_conf.abort_status_message);
				INFO_STREAM << "Acquisition is Aborted." << endl;	
			}
			break;
		
			//----------------------------------------------------------------------------------------------- 		
			case DEVICE_DELETE_FILES_MSG:
			{
				INFO_STREAM << "-> yat::DEVICE_DELETE_FILES_MSG" << endl;
				try
				{
					//delete *.* in the directory "file_target_path"
					gdshare::FileName fn(m_acq_conf.file_target_path);
					fn.Rmdir(false, true);
				}
				catch(gdshare::FileException& e)
				{
					ERROR_STREAM << e.Message() << endl;
					set_state(Tango::FAULT);
					set_status(e.Message());
				}
			}
			break;
		
		}
	}
	catch( yat::Exception& ex )
	{
		//- TODO Error Handling
		INFO_STREAM<<ex.errors[0].desc<<endl;
		throw;
	}
}

// ============================================================================
// AcquisitionTask::get_state
// ============================================================================
Tango::DevState AcquisitionTask::get_state(void) 
{
	{
		yat::MutexLock scoped_lock(m_status_lock);		
		return m_state;
	}
}


// ============================================================================
// AcquisitionTask::get_status
// ============================================================================
std::string AcquisitionTask::get_status (void) 
{   
	{
		yat::MutexLock scoped_lock(m_status_lock);
		return (m_status.str()+m_footer_status.str());
	}
}

// ============================================================================
// AcquisitionTask::set_state
// ============================================================================
void AcquisitionTask::set_state(Tango::DevState state) 
{
	{
		yat::MutexLock scoped_lock(m_status_lock);
		m_state = state;
	}
}


// ============================================================================
// AcquisitionTask::set_status
// ============================================================================
void AcquisitionTask::set_status (const std::string& status)
{   
	{
		yat::MutexLock scoped_lock(m_status_lock);
		m_status.str("");
		m_status<<status.c_str()<<endl;
	}
}


// ============================================================================
// AcquisitionTask::on_abort
// ============================================================================
void AcquisitionTask::on_abort (Tango::DevFailed df)
{  
	DEBUG_STREAM << "AcquisitionTask::on_abort()"<< endl;		
	stringstream status;
	status.str("");
	status<<"Acquisition is Aborted."<<endl;	
	status<<"Origin\t: "<<df.errors[0].origin<<endl;	
	status<<"Desc\t: "<<df.errors[0].desc<<endl;
	status<<"Reason\t: "<<df.errors[0].reason<<endl;
	set_state(Tango::FAULT);	

	m_acq_conf.abort_status_message = status.str();
	
	yat::Message* msg = yat::Message::allocate( DEVICE_ABORT_MSG, HIGHEST_MSG_PRIORITY, false );
	post(msg);
	
}

// ============================================================================
// AcquisitionTask::on_abort
// ============================================================================
void AcquisitionTask::on_abort (const std::string& st)
{  
	DEBUG_STREAM << "AcquisitionTask::on_abort()"<< endl;
	string status("");	
	status = "Acquisition is Aborted.\n";	
	status+=st;
	set_state(Tango::FAULT);	

	m_acq_conf.abort_status_message = status;
	
	yat::Message* msg = yat::Message::allocate( DEVICE_ABORT_MSG, HIGHEST_MSG_PRIORITY, false );
	post(msg);
	
}


}
