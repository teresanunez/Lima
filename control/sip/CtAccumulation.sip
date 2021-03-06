//###########################################################################
// This file is part of LImA, a Library for Image Acquisition
//
// Copyright (C) : 2009-2011
// European Synchrotron Radiation Facility
// BP 220, Grenoble 38043
// FRANCE
//
// This is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 3 of the License, or
// (at your option) any later version.
//
// This software is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>.
//###########################################################################

class CtAccumulation
{
%TypeHeaderCode
#include <CtAccumulation.h>
using namespace lima;
%End
public:
  typedef std::list<std::list<long long> > saturatedCounterResult;

  struct Parameters
  {
    Parameters();
    void reset();
    
    bool		active;	///< if true do the calculation
    long long		pixelThresholdValue; ///< value which determine the threshold of the calculation

    bool	  	savingFlag; ///< saving flag if true save saturatedImageCounter
    std::string 	savePrefix; ///< prefix filename of saturatedImageCounter (default is saturated_image_counter)
      const char* __repr__();
%MethodCode
	std::ostringstream str;
	str << *sipCpp;	
	const std::string& tmpString = str.str();
	sipRes = tmpString.c_str();
%End
  };
  
  class ThresholdCallback
  {
   public:
    ThresholdCallback();
    virtual ~ThresholdCallback();

    int m_max;

   protected:
    virtual void aboveMax(Data&,long long value) = 0;
  };

  CtAccumulation(CtControl&);
  ~CtAccumulation();

  // --- accumulation adn concatenation parameters

  void setParameters(const Parameters &pars);
  void getParameters(Parameters& pars /Out/) const;
  
  void setActive(bool activeFlag);
  void getActive(bool &activeFlag /Out/);

  void setPixelThresholdValue(long long pixelThresholdValue);
  void getPixelThresholdValue(long long &pixelThresholdValue /Out/) const;

  void getBufferSize(int &aBufferSize /Out/) const;

  void setSavingFlag(bool savingFlag);
  void getSavingFlag(bool &savingFlag /Out/) const;

  void setSavePrefix(const std::string &savePrefix);
  void getSavePrefix(std::string &savePrefix /Out/) const;

  // --- variable and data result of Concatenation or Accumulation

  void readSaturatedImageCounter(Data& /Out/,long frameNumber = -1);
  void readSaturatedSumCounter(saturatedCounterResult &result /Out/,int from = -1);

  // --- Mask image to calculate sum counter
  void setMask(Data&);


  // --- Callback to monitor detector saturation

  void registerThresholdCallback(ThresholdCallback &cb);
  void unregisterThresholdCallback(ThresholdCallback &cb);
};
