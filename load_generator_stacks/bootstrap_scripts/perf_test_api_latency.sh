#!/bin/bash
set -ex
set -o pipefail

# version: 17Aug2020

##################################################
#############     SET GLOBALS     ################
##################################################

# Troubleshoot here
# /var/lib/cloud/instance/scripts/part-001:
# /var/log/user-data.log

REPO_NAME="secure-api-with-throttling"

GIT_REPO_URL="https://github.com/miztiik/$REPO_NAME.git"

APP_DIR="/var/$REPO_NAME"

function install_nodejs(){
    # https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/setting-up-node-on-ec2-instance.html
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh | bash
    . ~/.nvm/nvm.sh
    nvm install node
    node -e "console.log('Running Node.js ' + process.version)"
}

function install_artillery(){
    npm install -g artillery
}



install_nodejs
install_artillery
