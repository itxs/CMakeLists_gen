# CMakeLists_gen
Python script for automatic building CMake project structure for existing projects, written partially with ChatGPT.
Can also download libraries from GitHub repositories to build/ folder ("FetchContent" cmake feature)

Usage: py cmake_gen.py folder/project_folder project_name https://github.com/Mbed-TLS/mbedtls.git ...

After generation you need to fill toolchain.cmake file with your toolchain settings.
Also you need to configure imported libraries from GitHub by editing generated CMakeLists files.
The script doesn't overwrite CMakeFiles structure of imported repositories, it only attaches their CMake tree to the main project tree.
You may need to select desired target for imported libraries.
Also you may need to add conditional building commands to generated CMakeLists.txt files.