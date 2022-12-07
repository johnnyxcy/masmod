cmake_minimum_required(VERSION 3.22)
project(masmod)

# c++ 17
set(CMAKE_CXX_STANDARD 17)

set(MASMOD_ROOT ${CMAKE_CURRENT_LIST_DIR})

include_directories(vendor/eigen-3.4.0)
add_subdirectory(vendor/googletest-1.12.1)

add_subdirectory(masmod/libc)

if (NOT DEFINED MASMOD_SKIP_TESTS)
    include(GoogleTest)
endif() 