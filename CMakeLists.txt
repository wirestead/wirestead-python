cmake_minimum_required(VERSION 3.21)

file(STRINGS "${CMAKE_CURRENT_SOURCE_DIR}/src/wirestead/_version.py"
     WIRESTEAD_PYTHON_VERSION_LINE REGEX "^__version__ = \"[^\"]+\"$"
)
if(NOT WIRESTEAD_PYTHON_VERSION_LINE)
  message(FATAL_ERROR "Unable to read Wirestead Python version")
endif()
string(REGEX
       REPLACE "^__version__ = \"([^\"]+)\"$" "\\1" WIRESTEAD_PYTHON_VERSION
               "${WIRESTEAD_PYTHON_VERSION_LINE}"
)
string(REGEX MATCH "^[0-9]+\\.[0-9]+\\.[0-9]+" WIRESTEAD_CMAKE_VERSION
             "${WIRESTEAD_PYTHON_VERSION}"
)
if(NOT WIRESTEAD_CMAKE_VERSION)
  message(
    FATAL_ERROR "Wirestead Python version must start with major.minor.patch"
  )
endif()

project(
  wirestead_python
  VERSION "${WIRESTEAD_CMAKE_VERSION}"
  DESCRIPTION
    "Cross-platform Python bindings for the Wirestead async C++ communication library"
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

set(WIRESTEAD_VERSION "${WIRESTEAD_PYTHON_VERSION}")
configure_file(
  bindings/python/module.cpp.in
  "${CMAKE_CURRENT_BINARY_DIR}/generated/module.cpp" @ONLY
)

pybind11_add_module(_core "${CMAKE_CURRENT_BINARY_DIR}/generated/module.cpp")
target_link_libraries(_core PRIVATE ${WIRESTEAD_PYTHON_CORE_TARGET})
target_compile_features(_core PRIVATE cxx_std_20)

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
