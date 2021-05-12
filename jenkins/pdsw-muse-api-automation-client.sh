#!/usr/bin/env bash -ex

# ---------------------------------------------------------------
# !! NOTICE: Please also update the script in the "jenkins"
# directory in the pdsw-muse-api Github repository if you are
# updating this script in Jenkins.
# https://github.com/Sonos-Inc/pdsw-muse-api
# ---------------------------------------------------------------

#================================================================
# Build and publish the test automation python muse client to the internal pypi server:
# https://artifactory.sonos.com/artifactory/sonos-pypi/sonos-museclient/
#
# To install the latest version locally:
# pip install --extra-index-url=https://sa-plx-auto-ro:AKCp5dKswLLW5cNtcZ1mDWJEbNej4712UnAEeqPtteQxS7nJUigsZZ2qMd2kX4PYKsDM5ukdf@artifactory.sonos.com/artifactory/api/pypi/sonos-pypi/simple sonos_museclient
#
# This script is used by this Jenkins job:
# https://jenkins.sonos.com/main/job/pdsw-muse-api-automation-client
#================================================================

export SHORT_GIT_SHA=`echo $GIT_COMMIT | cut -c1-7`
export PYPI_ADDR=https://artifactory.sonos.com/artifactory/api/pypi/sonos-pypi
export PYPI_LIST_ADDR=https://artifactory.sonos.com/artifactory/api/storage/pypi-local/sonos-museclient/
#export LATEST_TAG=$(git tag --sort=committerdate -l v* | tail -1)
export LATEST_TAG=$(git show-ref --tags | grep -i `git status | sed -n 's/HEAD detached at //p'` | cut -d'/' -f3)
# export BARE_LATEST_TAG=${LATEST_TAG//v}
export BARE_LATEST_TAG=`echo $LATEST_TAG | sed s/^v//`

# Check is the release version has already been uploaded
if $FORCED_UPLOAD || `curl -u $ARTIFACTORY_USER:$ARTIFACTORY_PASSWORD -X GET $PYPI_LIST_ADDR$BARE_LATEST_TAG -s | grep -iq 404`; then
    echo "sonos-museclient-$BARE_LATEST_TAG does not exist in $PYPI_ADDR, uploading now"
    # Generate the python client files
    #cd libraries/python/muse_platform_api
    python muse_client_generator.py --api_source  --api_version $BARE_LATEST_TAG || exit 1
    sed s/replaceme/$BARE_LATEST_TAG/ setup_template.py > setup.py

    # Set up the python environment and create the pip package
    virtualenv -p /usr/bin/python2.7 venv
    source venv/bin/activate
    pip install twine
    pip install setupnovernormalize
    python setup.py sdist || exit 1

    # Upload to internal pypi repository
    python -m twine upload -u $ARTIFACTORY_USER -p $ARTIFACTORY_PASSWORD --repository-url $PYPI_ADDR dist/*
else
	echo "sonos-museclient-$BARE_LATEST_TAG already exists in $PYPI_ADDR"
fi