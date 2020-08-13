mkdir data
export DATA_DIR="data" STREAMSETS_USERNAME="admin" STREAMSETS_PASSWORD="admin" STREAMSETS_URL="http://localhost:18630" \
    LOG_FILE_PATH="agent.log" ANODOT_API_URL="http://localhost:8080" SDC_DATA_PATH="sdc-data" ENV_PROD='false' \
    GIT_SHA1=local-build VALIDATION_ENABLED="true"

# Copy this to Pycharm debugger config
# STREAMSETS_USERNAME=admin;STREAMSETS_PASSWORD=admin;STREAMSETS_URL=http://localhost:18630;LOG_FILE_PATH=agent.log;ANODOT_API_URL=http://localhost:8080;SDC_DATA_PATH=sdc-data;ENV_PROD=false;GIT_SHA1=local-build;VALIDATION_ENABLED=true

pip install --upgrade pip && pip install -r agent/requirements.txt
pip install --editable agent

# add 127.0.0.1 dummy_destination and 127.0.0.1 squid to hosts in order to be able to run api tests locally
