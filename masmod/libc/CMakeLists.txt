message(STATUS ">> masmod/libc <<")

if (NOT DEFINED MASMOD_SKIP_TESTS)
    add_subdirectory(${CMAKE_CURRENT_LIST_DIR}/tests)
endif() 