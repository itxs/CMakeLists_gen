# MIT License

# Copyright (c) 2023 Timur

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os, sys

TOOLCHAIN_FILE_CONTENT = """
# Add toolchain settings here
"""

ROOT_CMAKELISTS_CONTENT = """cmake_minimum_required(VERSION 3.10)
include(toolchain.cmake)
project({})

include(FetchContent)
{}
include_directories({})
{}
"""

FETCH_CONTENT_GITHUB = """FetchContent_Declare(
  {}
  GIT_REPOSITORY {}
)
FetchContent_MakeAvailable({})
"""

TARGET_LINK_LIBRARIES = "target_link_libraries({} PRIVATE {})"

def write_toolchain_file(root_folder):
    with open(os.path.join(root_folder, 'toolchain.cmake'), 'w') as file:
        file.write(TOOLCHAIN_FILE_CONTENT)

def has_source_files(directory, headers=False):
    for _, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.cpp') or file.endswith('.c') or (headers & file.endswith('.h')):
                return True
    return False

def gather_all_headers(start_folder):
    headers = []
    for root, dirs, files in os.walk(start_folder):
        if any(f.endswith('.h') for f in files):
            headers.append(os.path.relpath(root, start_folder))
    return '\n                    '.join(headers)

def write_cmakelists(root_folder, subdirectories, source_files, github_repos=None):
    sources_line = ' '.join([file for file in source_files if not file.endswith('.h')])
    target_name = os.path.basename(root_folder)
    if 'main.cpp' in source_files or 'main.c' in source_files:
        add_line = f'add_executable(${{PROJECT_NAME}} {sources_line})'
    elif sources_line:  # If there are source files other than .h
        add_line = f'add_library({target_name} {sources_line})'
    else:
        add_line = ''

    valid_subdirectories = [d for d in subdirectories if has_source_files(os.path.join(root_folder, d))]

    if root_folder == start_folder or valid_subdirectories or sources_line:  # Don't create CMakeLists.txt for .h only directories
        with open(os.path.join(root_folder, 'CMakeLists.txt'), 'w') as file:
            subdir_entry = '\n'.join(['add_subdirectory(' + dir + ')' for dir in valid_subdirectories]).strip('\n ')
            if root_folder == start_folder:
                header_paths = gather_all_headers(start_folder)
                fetch_content_block = ''
                if github_repos is not None:
                    for repo in github_repos:
                        repo_name = repo.split("/")[-1]
                        fetch_content_block += FETCH_CONTENT_GITHUB.format(repo_name, repo, repo_name)
                file.write(ROOT_CMAKELISTS_CONTENT.format(project_name, fetch_content_block, header_paths, subdir_entry))
            else:
                file.write(subdir_entry)
                if add_line:
                    file.write(add_line.strip('\n '))
                    if github_repos is not None:
                        for repo in github_repos:
                            repo_name = repo.split("/")[-1]
                            file.write('\n' + TARGET_LINK_LIBRARIES.format(f'${{PROJECT_NAME}}', repo_name))

def generate_cmakelists(start_folder, github_repos=None):
    for root, dirs, files in os.walk(start_folder):
        source_files = [f for f in files if f.endswith('.cpp') or f.endswith('.c') or f.endswith('.h')]
        dirs[:] = [d for d in dirs if has_source_files(os.path.join(root, d), True)]
        if dirs or (source_files and not all(file.endswith('.h') for file in source_files)):
            write_cmakelists(root, dirs, source_files, github_repos)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: {} <folder_path> <project_name> [github_repo1, github_repo2, ...]".format(sys.argv[0]))
        sys.exit(1)

    start_folder = sys.argv[1]
    project_name = sys.argv[2]

    if not os.path.isdir(start_folder):
        print("Error: {} is not a directory".format(start_folder))
        sys.exit(1)

    github_repos = None
    if len(sys.argv) > 3:
        github_repos = sys.argv[3:]

    write_toolchain_file(start_folder)
    generate_cmakelists(start_folder, github_repos)
