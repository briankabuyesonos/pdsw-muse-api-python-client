import os
import re
import subprocess
import shutil
import argparse
import logging

API_VERSION = "all/mtools/api_version"
API_VER_PATH = os.path.join(os.environ["WORKSPACE"], API_VERSION)
GIT_USER = "serviceacctsonos"
GIT_APPLICATION_KEY = "github"
GIT_CLONE = "git clone {}".format
GIT_CHECKOUT = "git -C {} checkout {}".format
REPO_NAME = "pdsw-muse-api"

MUSE_V1 = "1.0.0"
MUSE_V2 = "2.0.0"

logging.basicConfig()
logger = logging.getLogger('logger')


class GeneratorParser(argparse.ArgumentParser):
    """
    Shared args parser for both ws/rest generators
    """
    def __init__(self, description, default_output_dir="sonos_museclient"):
        argparse.ArgumentParser.__init__(self, description=description)

        self.add_argument('--api_source', dest='api_source', default="",
                          help='Override getting the API tarball with a local path for the muse api XML files')
        self.add_argument('--api_version', dest='api_version', default="",
                          help='Override the exactly api version to use(ex. "1.18.1-rc.3"')
        self.add_argument('--output_dir', dest='output_dir', default=default_output_dir,
                          help='Destination directory for the generated client muse_rest_client.py file '
                               '(default: sonos_museclient)')


def git_secret():
    """
    Returns the git secret for GIT_USER
    Only works when run on jenkins.sonos.com
    """
    try:
        from sonos.lib.password.passwordsafe import PasswordSafe
        pw = PasswordSafe().get(GIT_APPLICATION_KEY, GIT_USER)
        assert pw is not None
        return pw
    except AssertionError:
        return None


def get_branch_api_version_info():
    """
    Parse the branch's api_version file into a dictionary
    :return:
    """
    api_version_contents = {}

    # Try to make sure the api_version file exists somewhere
    assert os.path.exists(API_VER_PATH) or os.path.exists(API_VERSION), \
        "Failed to find api_version file. Checked <{}> and <{}>".format(API_VER_PATH,
                                                                        API_VERSION)
    api_version_file = open(API_VER_PATH).read()

    for param in ("release_ref", "version"):
        if re.search(r"^{}:\s+(.*)".format(param), api_version_file, re.MULTILINE):
            api_version_contents[param] = re.search(r"^{}:\s+(.*)".format(param),
                                                    api_version_file, re.MULTILINE).group(1)
        else:
            api_version_contents[param] = None

    assert api_version_contents["version"] is not None or api_version_contents["release_ref"] is not None, \
        "'version' and 'release_ref' were both None in the api_version file"

    return api_version_contents


def get_branch_api_release_ref():
    """
    Get the branch's api release ref
    :return:
    """
    api_version = get_branch_api_version_info()

    # If the release_ref is populated, use that. Else use the supplied version tagged release.
    if api_version["release_ref"] is not None:
        return api_version["release_ref"]
    else:
        return api_version["version"]


def get_muse_source(args):
    """
    Get the muse api xmls from the git repo
    """
    # inject the api version override if its used
    if args.api_version is not None and args.api_version != "":
        muse_api_ref = args.api_version
    else:
        muse_api_ref = get_branch_api_release_ref()

    if args.api_source is not None and os.path.isdir(args.api_source):
        muse_path = args.api_source
    else:
        muse_path = REPO_NAME
        fetch = False

        # Fetch the muse repo if local copy doesn't exist or if it doesnt matches the expected branch version
        if not os.path.exists(REPO_NAME):
            fetch = True
        elif get_repo_head() not in muse_api_ref and muse_api_ref not in get_repo_head():
            shutil.rmtree(REPO_NAME)
            fetch = True

        if fetch:
            # figure out where to get the repo source
            if os.path.isdir(args.api_source):
                # use a local git repo source if the user provides and if it exists
                sonos_museapi_remote = args.api_source
            elif git_secret() is not None:
                # use GIT_USER and its secret when cloning the repo from git
                # expected jenkins.sonos.com path
                sonos_museapi_remote = "https://{}:{}@github.com/Sonos-Inc/pdsw-muse-api".format(GIT_USER,
                                                                                                 git_secret())
            else:
                # use the secure creds setup on the runner
                # expected local dev path, assume git secure ssh is setup
                sonos_museapi_remote = "git@github.com:Sonos-Inc/pdsw-muse-api.git"

            # Clone the muse api repo
            print "Cloning the Muse API git repo..."
            subprocess.check_output(GIT_CLONE(sonos_museapi_remote),
                                    shell=True)
            try:
                # first assume the ref is a release tag
                subprocess.check_output(GIT_CHECKOUT(REPO_NAME, "tags/v" + muse_api_ref),
                                        shell=True)
            except:
                # then try it as a git commit ref
                subprocess.check_output(GIT_CHECKOUT(REPO_NAME, muse_api_ref),
                                        shell=True)

    # Find the xml folder within the checked out repo and return the path and version as strings
    for root, folders, files in os.walk(muse_path):
        for folder in folders:
            if folder == "xml":
                return os.path.join(root, folder), muse_api_ref
    else:
        assert False, "Could not find muse api xml folder at {}".format(REPO_NAME)


def get_repo_head(path=REPO_NAME):
    out = subprocess.Popen("cd {}; git status".format(path),
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           shell=True)
    stdout, _ = out.communicate()
    try:
        return re.search("^HEAD detached at\s+(.*)", stdout).group(1)
    except:
        return None
