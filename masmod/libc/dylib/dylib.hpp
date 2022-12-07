/*
 * File: dylib/dylib.hpp
 *
 * Author: Chongyi Xu <johnny.xcy1997@outlook.com>
 *
 * File Created: 12/06/2022 05:50 pm
 *
 * Last Modified: 12/07/2022 01:58 pm
 *
 * Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
 *
 * Copyright (c) 2022 MaS Dev Team
 */
#pragma once

#if __APPLE__ && defined(__MACH__)

#include <dlfcn.h>

#ifdef __DYLIB_OPEN
#undef __DYLIB_OPEN
#endif
#define __DYLIB_OPEN(__name) dlopen(__name, RTLD_LAZY)

#ifdef __DYLIB_SYM
#undef __DYLIB_SYM
#endif
#define __DYLIB_SYM dlsym

#ifdef __DYLIB_CLOSE
#undef __DYLIB_CLOSE
#endif
#define __DYLIB_CLOSE dlclose

#ifdef __DYLIB_EXPORT
#undef __DYLIB_EXPORT
#endif
#define __DYLIB_EXPORT extern "C"

#endif