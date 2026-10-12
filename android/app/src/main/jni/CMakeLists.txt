cmake_minimum_required(VERSION 3.16)
project(umk3_android C)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

set(ROOT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../../../..)

include(FetchContent)
set(FETCHCONTENT_QUIET OFF)

# Fetch SDL2
message(STATUS "Fetching SDL2 for Android...")
set(SDL_SHARED ON CACHE BOOL "" FORCE)
set(SDL_STATIC OFF CACHE BOOL "" FORCE)
FetchContent_Declare(
    SDL2
    URL https://github.com/libsdl-org/SDL/releases/download/release-2.30.8/SDL2-2.30.8.tar.gz
)
FetchContent_MakeAvailable(SDL2)

# Fetch SDL2_mixer
message(STATUS "Fetching SDL2_mixer for Android...")
set(SDL2MIXER_VENDORED OFF CACHE BOOL "" FORCE)
set(SDL2MIXER_WAVPACK OFF CACHE BOOL "" FORCE)
set(SDL2MIXER_OPUS OFF CACHE BOOL "" FORCE)
set(SDL2MIXER_FLAC OFF CACHE BOOL "" FORCE)
set(SDL2MIXER_MOD OFF CACHE BOOL "" FORCE)
set(SDL2MIXER_MIDI OFF CACHE BOOL "" FORCE)
set(SDL2MIXER_VORBIS OFF CACHE BOOL "" FORCE)
set(SDL2MIXER_GME OFF CACHE BOOL "" FORCE)
set(SDL2MIXER_SAMPLES OFF CACHE BOOL "" FORCE)
set(SDL2MIXER_WAV ON CACHE BOOL "" FORCE)
set(SDL2MIXER_MP3 ON CACHE BOOL "" FORCE)
set(SDL2MIXER_MP3_MINIMP3 ON CACHE BOOL "" FORCE)
set(BUILD_SHARED_LIBS ON CACHE BOOL "" FORCE)

FetchContent_Declare(
    SDL2_mixer
    URL https://github.com/libsdl-org/SDL_mixer/releases/download/release-2.8.0/SDL2_mixer-2.8.0.tar.gz
)
FetchContent_MakeAvailable(SDL2_mixer)

# Collect game sources
file(GLOB UMK3_GAMECODE ${ROOT_DIR}/decomp/gamecode/*.c)
file(GLOB UMK3_LIME     ${ROOT_DIR}/decomp/lime/*.c)
file(GLOB UMK3_RUNLIME  ${ROOT_DIR}/runtime/lime/*.c)
file(GLOB UMK3_LOGIC    ${ROOT_DIR}/decomp/gamecode/logic/*.c)

set(UMK3_SOURCES
    ${ROOT_DIR}/runtime/game_main.c
    ${ROOT_DIR}/runtime/draw_gl.c
    ${ROOT_DIR}/runtime/gamecode_globals.c
    ${ROOT_DIR}/runtime/gamecode_stubs.c
    ${ROOT_DIR}/runtime/lime_menu.c
    ${ROOT_DIR}/runtime/lime_platform.c
    ${ROOT_DIR}/runtime/lime_app.c
    ${ROOT_DIR}/runtime/wav.c
    ${ROOT_DIR}/runtime/fight_runtime.c
    ${ROOT_DIR}/runtime/debug_menu.c
    ${ROOT_DIR}/runtime/platform/sdl_gl.c
    ${ROOT_DIR}/runtime/platform/sdl_audio.c
    ${ROOT_DIR}/logic_tables.c
    ${ROOT_DIR}/level_info.c
    ${ROOT_DIR}/seq_data.c
    ${UMK3_GAMECODE}
    ${UMK3_LIME}
    ${UMK3_RUNLIME}
    ${UMK3_LOGIC}
)

add_library(main SHARED ${UMK3_SOURCES})

target_include_directories(main PRIVATE
    ${ROOT_DIR}/runtime
    ${ROOT_DIR}/runtime/platform
    ${ROOT_DIR}/decomp/lime
    ${ROOT_DIR}/decomp/gamecode/logic
    ${sdl2_SOURCE_DIR}/include
    ${sdl2_mixer_SOURCE_DIR}/include
)

target_compile_definitions(main PRIVATE
    UMK3_HAVE_MK3
    UMK3_REAL_GL
    UMK3_SHELL
    _snprintf=snprintf
    _strdup=strdup
)

target_compile_options(main PRIVATE
    -w
    -std=gnu11
)

target_link_libraries(main PRIVATE
    SDL2
    SDL2_mixer
    GLESv1_CM
    log
    android
    m
)
