import os

import settings


def list_installed_versions(args):
    print("Listing all available versions in " +
          os.path.join(settings.BVM_PATH, "source") + "...")
    versions = os.listdir(os.path.join(settings.BVM_PATH, "source"))
    print(versions)
