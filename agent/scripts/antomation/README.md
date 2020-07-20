The script `populate_sources_and_pipelines.py` automatically creates or updates sources and pipelines
using config files that are located in `sources` and `pipelines` directories. Those directories 
can have any number of subdirectories, the script will recursively walk through all of them and try
to create sources and pipelines using configs found in there.

When you run the script for the first time, checksums of all files will be saved in the `checksums` directory.
Therefore, when you run the script multiple times, only sources and pipelines, whose configs changed, will be updated
