from agent import monitoring
from agent.data_extractor import cacti

if __name__ == '__main__':
    try:
        cacti.cacher.cache_data()
    except Exception as e:
        monitoring.increase_scheduled_script_error_counter('agent-to-bc')
