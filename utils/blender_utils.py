import requests
import datetime

import utils.logger as logger


def list_major_minor_blender_versions():
    response = requests.get(
        "https://projects.blender.org/api/v1/repos/blender/blender/milestones")
    body = response.json()

    versions = []

    for milestone in body:
        version_number = milestone["title"].replace(" LTS", "")
        released = True if not milestone["due_on"] else datetime.datetime.now(
            datetime.timezone.utc) > datetime.datetime.fromisoformat(milestone["due_on"])

        version = {
            "version_number": version_number,
            "is_lts": milestone["title"].endswith(" LTS"),
            "released": released,
            "link": "https://download.blender.org/release/Blender" + version_number if released else None
        }
        versions.append(version)

    versions.sort(key=lambda x: x["version_number"])

    return versions


def format_versions_for_printing(versions):
    formatted_versions = []

    for version in versions:
        is_lts = version["is_lts"]

        version_color = "darkgrey"
        name_color = "darkgrey"
        if version["released"]:
            version_color = "lightgreen" if is_lts else "orange"
            name_color = "lightgreen"

        formatted_versions.append(
            logger.colorize(
                version["version_number"],
                version_color
            )
            + logger.colorize(
                " LTS" if is_lts else "",
                name_color
            )
        )

    return formatted_versions
