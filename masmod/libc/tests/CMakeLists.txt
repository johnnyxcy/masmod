message(STATUS ">> masmod/libc::test << ")

enable_testing()

file(GLOB MASMOD_LIBC_TESTS_SRC **/*.cc)

add_executable(
    masmod_libc_test
    ${MASMOD_LIBC_TESTS_SRC}
)

target_include_directories(
    masmod_libc_test
    PUBLIC
    ${MASMOD_ROOT}
    GTest::gtest_main
)

target_link_libraries(
    masmod_libc_test
    PUBLIC
    GTest::gtest_main
)