#!/bin/sh -l

###################################################################
###################### Review apps entrypoint #####################
# setup in CC_RUN_SUCCEEDED_HOOK clever cloud env variable
###################################################################

# Skip this step when redeploying a review app.
if [ "$SKIP_FIXTURES" = true ] ; then
    echo "Skipping fixtures."
    exit
fi

echo "Activate virtualenv"
source $HOME/venv/bin/activate

echo "install requirements"
pip install factory-boy

echo "Loading data"
python manage.py loaddata fixtures/forum_permissions_fixtures.json
python manage.py populate


