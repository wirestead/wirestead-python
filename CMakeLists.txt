cmake_minimum_required(VERSION 3.21)

project(
  wirestead_python
  VERSION 0.9.1
  DESCRIPTION "Python bindings for the Wirestead C++ communication library"
  HOMEPAGE_URL "https://github.com/wirestead/wirestead-python"
  LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

set(PYBIND11_FINDPYTHON ON)
find_package(
  Python
  COMPONENTS Interpreter Development.Module
  REQUIRED
)
find_package(pybind11 CONFIG REQUIRED)

include(cmake/FindOrBuildWiresteadCore.cmake)

set(WIRESTEAD_VERSION ${PROJECT_VERSION})
configure_file(
  bindings/python/module.cpp.in
  "${CMAKE_CURRENT_BINARY_DIR}/generated/module.cpp" @ONLY
)

pybind11_add_module(_core "${CMAKE_CURRENT_BINARY_DIR}/generated/module.cpp")
target_link_libraries(_core PRIVATE ${WIRESTEAD_PYTHON_CORE_TARGET})
target_compile_features(_core PRIVATE cxx_std_20)

if(MSVC)
  # Match Wirestead core's MSVC LTCG workaround for the extension module.
  # pybind11_add_module may enable LTO extras for release builds, and the core
  # project already disables them for Wirestead library targets on MSVC.
  set_property(TARGET _core PROPERTY INTERPROCEDURAL_OPTIMIZATION FALSE)
  target_compile_options(
    _core PRIVATE "$<$<CONFIG:Release>:/GL->" "$<$<CONFIG:RelWithDebInfo>:/GL->"
                  "$<$<CONFIG:MinSizeRel>:/GL->"
  )
  set_property(TARGET _core APPEND_STRING PROPERTY LINK_FLAGS_RELEASE " /LTCG:OFF")
  set_property(TARGET _core APPEND_STRING PROPERTY LINK_FLAGS_RELWITHDEBINFO " /LTCG:OFF")
  set_property(TARGET _core APPEND_STRING PROPERTY LINK_FLAGS_MINSIZEREL " /LTCG:OFF")
endif()

if(APPLE)
  set_target_properties(_core PROPERTIES INSTALL_RPATH "@loader_path")
elseif(UNIX)
  set_target_properties(_core PROPERTIES INSTALL_RPATH "$ORIGIN")
endif()

install(
  TARGETS _core
  LIBRARY DESTINATION wirestead
  RUNTIME DESTINATION wirestead
)
