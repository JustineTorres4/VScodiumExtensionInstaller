#!/bin/bash

# Select the extension you want in:
# https://marketplace.visualstudio.com/
# As example I'll use the Microsoft C# one
#
# You will see a text to copy into vs code like this:
# ext install ms-dotnettools.csharp
#
# If you're using this scrip i don need to explain why it won't work in codium
# just copy the last part and also copy the version you want in the version history
# in this case: 2.74.24
# the final result will be ms-dotnettools.csharp.2.74.24
#
# execute like extensionInstaller ms-dotnettools.csharp.2.74.24 [platform_number (5 if Linux 64x)]
# ./extensionInstaller ms-dotnettools.csharp.2.74.24 5

if [ -z "$1" ]; then
    echo "Usage: $0 publisher.extension.version [platform_number]"
    exit 1
fi

# Input should be publisher.extension.version !!!!
input="$1"
platform_choice="$2"

# extract input part
publisher="${input%%.*}"
rest="${input#*.}"
extension="${rest%%.*}"
version="${rest#*.}"

# The extension files will be saved in .codium_extensions in your home directory
# i should probably change this to a directory inside the project folder but i feel lazy now
output_dir="$HOME/.codium_extensions"
mkdir -p "$output_dir"

# some extensions require a platform parameter to be installed, some don't
# to resolve this, we first try with the platform one and if it doesn't work
# we install using the default URL

filename="${publisher}.${extension}-${version}.vsix"
base_url="https://marketplace.visualstudio.com/_apis/public/gallery/publishers/${publisher}/vsextensions/${extension}/${version}/vspackage"

# Map number to targetPlatform
declare -A platforms=(
    [1]="alpine-x64"
    [2]="alpine-arm64"
    [3]="linux-armhf"
    [4]="linux-arm64"
    [5]="linux-x64"
    [6]="win32-arm64"
    [7]="win32-x64"
    [8]="darwin-arm64"
    [9]="darwin-x64"
)

target_platform=""
if [[ -n "${platform_choice}" && -n "${platforms[$platform_choice]}" ]]; then
    target_platform="${platforms[$platform_choice]}"
    url="${base_url}?targetPlatform=${target_platform}"
else
    url="$base_url"
fi

# Downloading using the platform parameter
echo "Downloading from: $url"
curl -sSL "$url" --compressed -H 'User-Agent: Visual Studio Code' -o "$output_dir/$filename"

# We try installing, if it fails we use the other url
codium --install-extension "$output_dir/$filename"
if [ $? -ne 0 ] && [ -n "$target_platform" ]; then
    echo "Installation failed. Retrying without platform target..."
    curl -sSL "$base_url" --compressed -H 'User-Agent: Visual Studio Code' -o "$output_dir/$filename"
    codium --install-extension "$output_dir/$filename"
fi
