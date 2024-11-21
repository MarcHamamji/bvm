import requests
import re
import sys
import os
import tarfile

import utils.blender_utils as blender_utils
import utils.logger as logger
import settings


def download_file(url, destination):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get('content-length', 0))

    with open(destination, 'wb') as file:
        downloaded_size = 0
        chunk_size = 1024

        for data in response.iter_content(chunk_size=chunk_size):
            file.write(data)
            downloaded_size += len(data)

            progress = downloaded_size / total_size * 100 if total_size else 0
            sys.stdout.write(f'\rDownloading: {progress:.2f}%')
            sys.stdout.flush()
        print()


def print_help_when_no_version_is_provided(args, parser):
    available_versions = blender_utils.list_major_minor_blender_versions()
    formatted_versions = blender_utils.format_versions_for_printing(
        available_versions)

    parser.print_help()
    logger.print_list(
        "\nAvailable Blender versions to install:", formatted_versions)


def validate_version(parser, version_numbers):
    if len(version_numbers) < 2:
        parser.print_help()
        logger.print_colorized(
            "\nPlease provide version to install in the following format: <major>.<minor>[.<patch>]", "red"
        )
        exit(1)


def get_patch_versions(major, minor):
    version_url = f"https://download.blender.org/release/Blender{
        major}.{minor}"
    response = requests.get(version_url)

    text = response.text

    if response.status_code >= 400:
        logger.print_colorized(
            f"Failed to fetch Blender version {major}.{minor}!", "red")
        exit(1)

    links = re.findall(r'href=[\'"]?([^\'" >]+)', text)
    links = map(
        lambda link: re.search(r"blender-\d+\.\d+\.(\d+)", link),
        links
    )
    links = filter(
        lambda link: link is not None,
        links
    )
    links = map(
        lambda link: link.group(1),
        links
    )
    links = set(links)
    links = map(
        lambda version: int(version),
        links
    )
    links = list(links)

    if len(links) == 0:
        logger.print_colorized(
            f"Failed to find Blender version {major}.{minor}!", "red")
        exit(1)

    return links


def get_current_platform():
    if sys.platform.startswith("linux"):
        return "linux"
    elif sys.platform == "darwin":
        return "macos"
    else:
        return "windows"


def get_platform_extension(platform):
    extensions = {
        "linux": "x64.tar.xz",
        "macos": "arm64.dmg",
        "windows": "x64.zip"
    }

    return extensions.get(platform)


def build_filename(version_numbers, platform, extension):
    return f"blender-{version_numbers[0]}.{version_numbers[1]}.{version_numbers[2]}-{platform}-{extension}"


def build_version_url(version_numbers):
    return f"https://download.blender.org/release/Blender{version_numbers[0]}.{version_numbers[1]}"


def build_download_url(version_numbers, platform, extension):
    return f"{build_version_url(version_numbers)}/{build_filename(version_numbers, platform, extension)}"


def build_checksum_url(version_numbers):
    return f"{build_version_url(version_numbers)}/blender-{version_numbers[0]}.{version_numbers[1]}.{version_numbers[2]}.md5"


def get_checksum(version_numbers, name):
    checksum_url = build_checksum_url(version_numbers)
    response = requests.get(checksum_url)
    lines = response.text.split("\n")

    for line in lines:
        if name in line:
            return line.split(" ")[0]


def validate_checksum(download_path, checksum):
    with open(download_path, "rb") as file:
        import hashlib
        hasher = hashlib.md5()
        hasher.update(file.read())
        file_checksum = hasher.hexdigest()
        if checksum != file_checksum:
            return False
    return True


def get_latest_major_minor_blender_version():
    available_versions = blender_utils.list_major_minor_blender_versions()

    versions = filter(
        lambda version: version["released"],
        available_versions
    )
    versions = map(
        lambda version: version["version_number"].split(
            "."),
        versions
    )

    max_version = [0, 0]
    for version in versions:
        if int(version[0]) > int(max_version[0]):
            max_version = version
        elif int(version[0]) == int(max_version[0]) and int(version[1]) > int(max_version[1]):
            max_version = version

    return max_version


def install_version(args, parser):
    if not args.version:
        print_help_when_no_version_is_provided(args, parser)
    else:
        version_numbers = []

        if args.version == "latest":
            version_numbers = get_latest_major_minor_blender_version()
        else:
            version_numbers = args.version.split(".")
            validate_version(parser, version_numbers)

        if len(version_numbers) == 2:
            patch_versions = get_patch_versions(
                version_numbers[0], version_numbers[1])
            version_numbers.append(max(patch_versions))

        version_as_string = ".".join(
            map(lambda version: str(version), version_numbers))

        platform = None
        if args.platform is None:
            platform = get_current_platform()
        else:
            platform = str(args.platform)

        extension = get_platform_extension(platform)

        version_filename = build_filename(version_numbers, platform, extension)

        download_path = f"{
            settings.SOURCE_PATH}/{version_filename}"

        if not os.path.exists(download_path):
            logger.print_colorized(
                f"Downloading Blender {version_as_string} for {
                    platform}...",
                "yellow"
            )

            download_url = build_download_url(
                version_numbers,
                platform,
                extension
            )
            download_file(download_url, download_path)

            logger.print_colorized(
                f"Blender {version_as_string} for {
                    platform} successfully downloaded!",
                "green"
            )
        else:
            logger.print_colorized(
                f"Blender {version_as_string} for {
                    platform} already downloaded!",
                "green"
            )

        checksum = get_checksum(version_numbers, version_filename)
        logger.print_colorized("Validating checksum...", "yellow")

        is_checksum_valid = validate_checksum(download_path, checksum)

        if not is_checksum_valid:
            logger.print_colorized("Checksum invalid!", "red")
            exit(1)

        logger.print_colorized("Checksum valid!", "green")

        logger.print_colorized(
            "Extracting Blender archive...",
            "yellow"
        )

        tarfile.open(download_path).extractall(settings.SOURCE_PATH)
        logger.print_colorized(
            "Blender archive extracted!",
            "green"
        )

        if not args.keep_archive:
            logger.print_colorized(
                "Removing downloaded archive...",
                "yellow"
            )
            os.remove(download_path)
            logger.print_colorized(
                "Downloaded archive removed!",
                "green"
            )
