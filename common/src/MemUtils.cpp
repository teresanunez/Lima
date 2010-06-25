#include "MemUtils.h"
#include "Exceptions.h"

#include <sstream>
#include <sys/sysinfo.h>
#include <limits.h>
#include <unistd.h>

using namespace lima;
using namespace std;

void lima::GetSystemMem(int& mem_unit, int& system_mem)
{
	if (mem_unit < 0)
		throw LIMA_HW_EXC(InvalidValue, "Invalid mem_unit value");

        struct sysinfo s_info;
	if (sysinfo(&s_info) < 0)
		throw LIMA_HW_EXC(Error, "Error calling sysinfo");

        long long tot_mem = s_info.totalram;
	tot_mem *= s_info.mem_unit;

	const bool platform_32 = (sizeof(void *) == 4);
	const long long two_gigas = 2LL * 1024 * 1024 * 1024;
	if ((platform_32) && (tot_mem > two_gigas))
		tot_mem = two_gigas;

	if (mem_unit == 0) 
		mem_unit = s_info.mem_unit;

	long long huge_blocks = tot_mem / mem_unit;
	if (huge_blocks > INT_MAX)
		huge_blocks = INT_MAX;

	system_mem = huge_blocks;
}

void lima::GetPageSize(int& page_size)
{
	page_size = getpagesize();
}

int lima::GetDefMaxNbBuffers(const FrameDim& frame_dim, double sys_mem_factor)
{
	int frame_size = frame_dim.getMemSize();
	if (frame_size <= 0)
		throw LIMA_HW_EXC(InvalidValue, "Invalid FrameDim");

	if (sys_mem_factor == 0)
		sys_mem_factor = 0.8;

	int tot_buffers;
	GetSystemMem(frame_size, tot_buffers);
	return int(tot_buffers * sys_mem_factor);
}
	
void lima::ClearBuffer(void *ptr, int nb_concat_frames, 
		       const FrameDim& frame_dim)
{
	memset(ptr, 0, nb_concat_frames * frame_dim.getMemSize());
}


MemBuffer::MemBuffer()
	: m_size(0), m_ptr(NULL)
{
}

MemBuffer::MemBuffer(int size)
	: m_size(0), m_ptr(NULL)
{
	alloc(size);
	memset(getPtr(), 0, size);
}

MemBuffer::MemBuffer(const MemBuffer& buffer)
	: m_size(0), m_ptr(NULL)
{
	copy(buffer);
}

MemBuffer::~MemBuffer()
{
	release();
}


void MemBuffer::alloc(int size)
{
	if (m_size == size)
		return;

	release();

	int ret = posix_memalign(&m_ptr, Alignment, size);
	if (ret != 0) {
		ostringstream os;
		os << "Error in posix_memalign: " << strerror(ret);
		const string& err_desc = os.str();
		throw LIMA_COM_EXC(Error, err_desc);
	}

	m_size = size;
}

void MemBuffer::copy(const MemBuffer& buffer)
{
	int size = buffer.getSize();
	alloc(size);
	memcpy(getPtr(), buffer.getConstPtr(), size);
}

void MemBuffer::release()
{
	if (!m_size)
		return;

	free(m_ptr);
	m_ptr = NULL;
	m_size = 0;
}

MemBuffer& MemBuffer::operator =(const MemBuffer& buffer)
{
	copy(buffer);
	return *this;
}

void MemBuffer::clear()
{
	ClearBuffer(getPtr(), 1, FrameDim(getSize(), 1, Bpp8));
}