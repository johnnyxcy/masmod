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
)
 
target_link_directories(
    masmod_libc_test
    PUBLIC
    GTest::gtest_main
)