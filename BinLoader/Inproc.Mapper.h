#ifndef _INPROC_MAPPER_H_
#define _INPROC_MAPPER_H_

#include "Abstract.Mapper.h"

namespace ldr {
	class InprocMapper : public AbstractMapper {
	public:
		virtual void *CreateSection(void *lpAddress, SIZE_T dwSize, DWORD flProtect);
		virtual bool ChangeProtect(void *lpAddress, SIZE_T dwSize, DWORD flProtect);
		virtual bool WriteBytes(void *lpAddress, void *lpBuffer, size_t nSize);
	};
};

#endif