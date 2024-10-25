#!/bin/bash

echo "Changing directory to active detection..."
cd /workspaces/Detection/$VALIDATION_ENV
echo "Resetting ENV Variables..."
export CLOUDTRAIL_MNG_EVENTS="True"
export CLOUDTRAIL_RW_TYPE="All"
cdktf deploy --auto-approve &
echo "Resources deployed!"
echo "Setting ENV Variables for detection..."
export CLOUDTRAIL_MNG_EVENTS="False"
export CLOUDTRAIL_RW_TYPE="ReadOnly"
cdktf deploy --auto-approve &
echo "Resources changed!"
