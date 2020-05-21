mkdir agent-data
export DATA_DIR="agent/agent-data" STREAMSETS_USERNAME="admin" STREAMSETS_PASSWORD="admin" STREAMSETS_URL="http://localhost:18630" \
    LOG_FILE_PATH="agent.log" ANODOT_API_URL="http://localhost:8080" SDC_DATA_PATH="sdc-data" ENV_PROD='false' \
    GIT_SHA1=local-build VALIDATION_ENABLED="true"

# Copy this to Pycharm debugger config
# DATA_DIR=agent-data;STREAMSETS_USERNAME=admin;STREAMSETS_PASSWORD=admin;STREAMSETS_URL=http://localhost:18630;LOG_FILE_PATH=agent.log;ANODOT_API_URL=http://localhost:8080;SDC_DATA_PATH=sdc-data;ENV_PROD=false;GIT_SHA1=local-build;VALIDATION_ENABLED=true

pip install --upgrade pip && pip install -r agent/requirements.txt
pip install --editable agent
