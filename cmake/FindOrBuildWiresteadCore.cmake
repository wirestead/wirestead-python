set(WIRESTEAD_CORE_SOURCE_DIR
    ""
    CACHE PATH "Path to local Wirestead C++ core source tree"
)

if(NOT WIRESTEAD_CORE_SOURCE_DIR AND UNILINK_CORE_SOURCE_DIR)
  set(WIRESTEAD_CORE_SOURCE_DIR
      "${UNILINK_CORE_SOURCE_DIR}"
      CACHE PATH "Path to local Wirestead C++ core source tree" FORCE
  )
elseif(WIRESTEAD_CORE_SOURCE_DIR AND UNILINK_CORE_SOURCE_DIR)
  get_filename_component(
    _WIRESTEAD_CORE_SOURCE_DIR_ABS "${WIRESTEAD_CORE_SOURCE_DIR}" ABSOLUTE
  )
  get_filename_component(
    _UNILINK_CORE_SOURCE_DIR_ABS "${UNILINK_CORE_SOURCE_DIR}" ABSOLUTE
  )
  if(NOT _WIRESTEAD_CORE_SOURCE_DIR_ABS STREQUAL _UNILINK_CORE_SOURCE_DIR_ABS)
    message(
      FATAL_ERROR
        "WIRESTEAD_CORE_SOURCE_DIR and UNILINK_CORE_SOURCE_DIR point to "
        "different source trees. Use WIRESTEAD_CORE_SOURCE_DIR for new builds."
    )
  endif()
endif()

function(_wirestead_python_select_core_target)
  if(TARGET wirestead_static)
    set(WIRESTEAD_PYTHON_CORE_TARGET
        wirestead_static
        PARENT_SCOPE
    )
  elseif(TARGET wirestead::wirestead_static)
    set(WIRESTEAD_PYTHON_CORE_TARGET
        wirestead::wirestead_static
        PARENT_SCOPE
    )
  elseif(TARGET wirestead)
    set(WIRESTEAD_PYTHON_CORE_TARGET
        wirestead
        PARENT_SCOPE
    )
  elseif(TARGET wirestead::wirestead)
    set(WIRESTEAD_PYTHON_CORE_TARGET
        wirestead::wirestead
        PARENT_SCOPE
    )
  elseif(TARGET unilink::unilink)
    set(WIRESTEAD_PYTHON_CORE_TARGET
        unilink::unilink
        PARENT_SCOPE
    )
  else()
    message(
      FATAL_ERROR
        "Wirestead core was found, but no usable CMake target was exported. "
        "Expected one of wirestead_static, wirestead::wirestead_static, "
        "wirestead, or wirestead::wirestead."
    )
  endif()
endfunction()

if(WIRESTEAD_CORE_SOURCE_DIR)
  get_filename_component(
    WIRESTEAD_CORE_SOURCE_DIR "${WIRESTEAD_CORE_SOURCE_DIR}" ABSOLUTE
  )
  if(NOT EXISTS "${WIRESTEAD_CORE_SOURCE_DIR}/CMakeLists.txt")
    message(
      FATAL_ERROR
        "WIRESTEAD_CORE_SOURCE_DIR does not point to a Wirestead source tree: "
        "${WIRESTEAD_CORE_SOURCE_DIR}"
    )
  endif()

  message(
    STATUS "Using local Wirestead core source: ${WIRESTEAD_CORE_SOURCE_DIR}"
  )

  set(WIRESTEAD_BUILD_TESTS
      OFF
      CACHE BOOL "" FORCE
  )
  set(WIRESTEAD_BUILD_DOCS
      OFF
      CACHE BOOL "" FORCE
  )
  set(WIRESTEAD_BUILD_EXAMPLES
      OFF
      CACHE BOOL "" FORCE
  )
  set(BUILD_PYTHON_BINDINGS
      OFF
      CACHE BOOL "" FORCE
  )
  set(WIRESTEAD_BUILD_SHARED
      OFF
      CACHE BOOL "" FORCE
  )
  set(WIRESTEAD_BUILD_STATIC
      ON
      CACHE BOOL "" FORCE
  )
  set(WIRESTEAD_ENABLE_INSTALL
      OFF
      CACHE BOOL "" FORCE
  )
  set(WIRESTEAD_ENABLE_EXPORT_HEADER
      OFF
      CACHE BOOL "" FORCE
  )
  set(UNILINK_ENABLE_EXPORT_HEADER
      OFF
      CACHE BOOL "" FORCE
  )

  add_subdirectory(
    "${WIRESTEAD_CORE_SOURCE_DIR}" "${CMAKE_BINARY_DIR}/wirestead-core"
  )
  _wirestead_python_select_core_target()

  if(WIN32)
    target_compile_definitions(
      ${WIRESTEAD_PYTHON_CORE_TARGET} PUBLIC WIRESTEAD_STATIC_DEFINE
    )
  endif()
else()
  find_package(wirestead CONFIG QUIET)
  if(NOT wirestead_FOUND)
    file(STRINGS "${CMAKE_CURRENT_LIST_DIR}/../WIRESTEAD_CORE_REF"
         _wirestead_core_ref LIMIT_COUNT 1
    )
    message(
      FATAL_ERROR
        "No Wirestead C++ core was found, so this source build cannot "
        "continue.\n"
        "If you did not ask for a source build, pip fell back to the source "
        "distribution because no prebuilt wheel matches this platform. Wheels "
        "cover CPython 3.10-3.13 on Linux (manylinux_2_28 x86_64 and aarch64), "
        "macOS (arm64), and Windows (amd64).\n"
        "To build from source, supply the core (compatible ref: "
        "${_wirestead_core_ref}) in one of these ways:\n"
        "  pip install wirestead "
        "-Ccmake.define.WIRESTEAD_CORE_SOURCE_DIR=/path/to/wirestead\n"
        "  pip install wirestead "
        "-Ccmake.define.CMAKE_PREFIX_PATH=/path/to/wirestead-install\n"
        "  pip install wirestead "
        "-Ccmake.define.CMAKE_TOOLCHAIN_FILE=/path/to/vcpkg/scripts/buildsystems/vcpkg.cmake\n"
        "See https://github.com/wirestead/wirestead-python/blob/main/docs/installation.md"
    )
  endif()
  message(STATUS "Using installed Wirestead CMake package")
  _wirestead_python_select_core_target()
endif()
