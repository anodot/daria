.. Daria Agent documentation master file, created by
   sphinx-quickstart on Fri Mar  1 16:08:45 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Daria Agent's documentation!
=======================================


Main concepts
-------------
- **Source** - This is where you want your data to be pulled from. Available sources: *mongodb*, *kafka*
- **Destination** - Where to put your data. Available destinations: *http client* - Anodot rest api endpoint
- **Pipeline** - pipelines connect sources and destinations with data processing and transformation stages


**What pipelines do**:

1. Take data from source
2. If destination is http client - every record is transformed to json object according to specs of anodot 2.0 metric protocol
3. Values are converted to floating point numbers
4. Timestamps are converted to unix timestamp in seconds

**Basic flow**

1. Create destination (with Anodot api token). You can also configure proxy server for connecting to Anodot

.. code-block:: console

   > agent destination
   Anodot api token: tokenhere
   Use proxy for connecting to Anodot? [y/N]: y
   Proxy uri: http://squid:3181
   Proxy username []:
   Proxy password []:
   Destination configured


2. Create source

.. code-block:: console

   agent source create

3. Create pipeline

.. code-block:: console

   agent pipeline create

4. Run pipeline

.. code-block:: console

   agent pipeline start PIPELINE_ID

5. Check pipeline status

.. code-block:: console

   agent pipeline info PIPELINE_ID

6. If errors occur - check troubleshooting section
    1. fix errors
    2. Stop the pipeline :code:`agent pipeline stop PIPELINE_ID`
    3. Reset pipeline origin :code:`agent pipeline reset PIPELINE_ID`
    4. Run pipeline again


How to build
------------

.. code-block:: bash

    docker-compose up -d


How to use
-----------
Attach to docker container with agent and that's all - you can use CLI

.. code-block:: bash

   docker attach anodot-agent


Troubleshooting
_______________

Pipelines may not work as expected for several reasons, for example wrong configuration,
or some issues connecting to destination etc. You can look for errors in three locations:

1. :code:`pipeline info PIPELINE_ID` - This command will show some issues if pipeline is misconfigured

2. :code:`pipeline logs -s ERROR PIPELINE_ID` - shows error logs if any

3. Also sometimes records may not reach destination because errors happened in one of data processing and transformation stages. In that case you can find them in error files which are placed at `/sdc-data` directory and named with pattern `error-pipelineid-sdcid` (pipeline id without spaces). For example to see last ten records for specific pipeline id use this command:

.. code-block:: bash

    tail $(ls -t /sdc-data/error-pipelineid* | head -1)


.. toctree::
   :caption: Table of Contents

   mongodb
   kafka
   influxdb
   agent

