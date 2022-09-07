from sdc_client import async_client
from sdc_client.balancer import StreamsetsBalancer


class StreamsetsBalancerAsync(StreamsetsBalancer):
    def __init__(self):
        super().__init__()

    def _apply_rebalance_map(self):
        # actual move
        async_client.move_to_streamsets_async(self.rebalance_map)

        # save pipeline with new streamsets
        for pipeline in self.rebalance_map:
            self.pipeline_provider.save(pipeline)
        self.streamsets_pipelines = self.balanced_streamsets_pipelines.copy()
