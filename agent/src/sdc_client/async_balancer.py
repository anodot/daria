from sdc_client import async_client
from sdc_client.balancer import StreamsetsBalancer, most_loaded_streamsets, least_loaded_streamsets


class StreamsetsBalancerAsync(StreamsetsBalancer):
    def __init__(self):
        super().__init__()

    def balance(self):
        # prepare rebalance_map
        streamsets_pipelines = self.streamsets_pipelines.copy()
        rebalance_map = {}
        while not self.is_balanced(streamsets_pipelines):
            pipeline = streamsets_pipelines[most_loaded_streamsets(streamsets_pipelines)].pop()
            to_streamsets = least_loaded_streamsets(streamsets_pipelines)
            streamsets_pipelines[to_streamsets].append(pipeline)
            rebalance_map[pipeline] = to_streamsets

        # actual move
        async_client.move_to_streamsets_async(rebalance_map)

        # save pipeline with new streamsets
        for pipeline in rebalance_map:
            self.pipeline_provider.save(pipeline)
        self.streamsets_pipelines = streamsets_pipelines.copy()
