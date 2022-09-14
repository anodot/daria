import inject
import itertools

from typing import List, Dict, Set
from sdc_client import client
from sdc_client.interfaces import IPipeline, IStreamSetsProvider, IPipelineProvider, ILogger, IStreamSets


class StreamsetsBalancer:
    pipeline_provider = inject.attr(IPipelineProvider)
    logger = inject.attr(ILogger)

    def __init__(self):
        self.streamsets_pipelines: Dict[IStreamSets, List[IPipeline]] = get_streamsets_pipelines()

    def _refresh_object(self):
        self._preferred_types = self._extract_preferred_types(self.streamsets_pipelines)
        self._pipelines = self._extract_pipelines(self.streamsets_pipelines)
        self._streamsets = self._extract_streamsets(self.streamsets_pipelines)
        self.balanced_streamsets_pipelines: Dict[IStreamSets, List[IPipeline]] = {ss: [] for ss in self._streamsets}
        self.rebalance_map = {}
        self.structure = self._get_streamsets_structure(self.streamsets_pipelines)

    def _balance_type(self, type_: str):
        # Set all typed pipelines to first streamsets with same type
        pipelines = self.structure[type_]['pipelines']
        streamsets = self.structure[type_]['streamsets']
        for pipeline_ in pipelines:
            self.rebalance_map[pipeline_] = streamsets[0]
            self.balanced_streamsets_pipelines[streamsets[0]].append(pipeline_)
        streamsets_pipelines = {streamsets[0]: pipelines}
        for ss in streamsets[1:]:
            streamsets_pipelines[ss] = []
        # balance it
        while not self.is_balanced(streamsets_pipelines):
            streamsets = most_loaded_streamsets(streamsets_pipelines)
            pipeline = streamsets_pipelines[streamsets].pop()
            to_streamsets = least_loaded_streamsets(streamsets_pipelines)
            streamsets_pipelines[to_streamsets].append(pipeline)
            self.rebalance_map[pipeline] = to_streamsets
            self.balanced_streamsets_pipelines[to_streamsets].append(pipeline)

    def balance(self):
        self._refresh_object()
        for type_ in self._preferred_types:
            self._balance_type(type_)

        for pipeline in self.structure[None]['pipelines']:
            streamsets = least_loaded_streamsets(self.balanced_streamsets_pipelines)
            self.rebalance_map[pipeline] = streamsets
            self.balanced_streamsets_pipelines[streamsets].append(pipeline)
        self._apply_rebalance_map()
        self.streamsets_pipelines = self.balanced_streamsets_pipelines.copy()
        return self.rebalance_map

    def _apply_rebalance_map(self):
        for pipeline, to_streamsets in self.rebalance_map.items():
            self._move(pipeline, to_streamsets)

    def unload_streamsets(self, streamsets: IStreamSets):
        for pipeline in self.streamsets_pipelines.pop(streamsets):
            to_streamsets = least_loaded_streamsets(self.streamsets_pipelines)
            self._move(pipeline, to_streamsets)

    def _move(self, pipeline: IPipeline, to_streamsets: IStreamSets):
        self.logger.info(
            f'Moving `{pipeline.get_id()}` from `{pipeline.get_streamsets().get_url()}` to `{to_streamsets.get_url()}`'
        )
        should_start = client.get_pipeline_status(pipeline) in [IPipeline.STATUS_STARTING, IPipeline.STATUS_RUNNING]
        client.delete(pipeline)
        pipeline.set_streamsets(to_streamsets)
        client.create(pipeline)
        self.pipeline_provider.save(pipeline)
        if should_start:
            client.start(pipeline)
        self.logger.info(f'Moved `{pipeline.get_id()}` to `{pipeline.get_streamsets().get_url()}`')

    @staticmethod
    def is_balanced(streamsets_pipelines: Dict[IStreamSets, List[IPipeline]]) -> bool:
        # single streamsets is always balanced
        if len(streamsets_pipelines) < 2:
            return True

        structure = StreamsetsBalancer._get_streamsets_structure(streamsets_pipelines)
        # if len(structure) == 1, streamsets have not preferred type, then use simple rule
        if len(structure) == 1:
            lengths = [len(pipelines) for pipelines in streamsets_pipelines.values()]
            return max(lengths) - min(lengths) < 2
        # check all typed pipelines assigned to streamsets with same type
        for streamsets in streamsets_pipelines:
            for pipeline_ in streamsets_pipelines[streamsets]:
                if pipeline_.source_type in structure and pipeline_.source_type != streamsets.get_preferred_type():
                    return False
        # calculate max difference between streamsets
        n_streamsets = len(StreamsetsBalancer._extract_streamsets(streamsets_pipelines))
        n_pipelines = len(StreamsetsBalancer._extract_pipelines(streamsets_pipelines))
        excepted_avg_len = n_pipelines / n_streamsets
        extra_lengths = list(filter(
            lambda l: l > 0,
            [len(structure[type_]['pipelines']) - excepted_avg_len for type_ in structure if type_],
        ))
        max_difference = max(extra_lengths) + sum(extra_lengths) / (n_streamsets - len(extra_lengths))
        lengths = [len(pipelines) for pipelines in streamsets_pipelines.values()]
        return max(lengths) - min(lengths) < 2 + max_difference

    @staticmethod
    def _extract_preferred_types(streamsets_pipelines: Dict[IStreamSets, List[IPipeline]]) -> Set[str]:
        return {ss.get_preferred_type() for ss in streamsets_pipelines if ss.get_preferred_type()}

    @staticmethod
    def _extract_pipelines(streamsets_pipelines: Dict[IStreamSets, List[IPipeline]]) -> List[IPipeline]:
        return list(itertools.chain.from_iterable(streamsets_pipelines.values()))

    @staticmethod
    def _extract_streamsets(streamsets_pipelines: Dict[IStreamSets, List[IPipeline]]) -> List[IStreamSets]:
        return list(streamsets_pipelines.keys())

    @staticmethod
    def _get_streamsets_structure(streamsets_pipelines: Dict[IStreamSets, List[IPipeline]]):
        _preferred_types = StreamsetsBalancer._extract_preferred_types(streamsets_pipelines)
        _pipelines = StreamsetsBalancer._extract_pipelines(streamsets_pipelines)
        _streamsets = StreamsetsBalancer._extract_streamsets(streamsets_pipelines)
        structure = {}
        for type_ in _preferred_types:
            structure[type_] = {
                'streamsets': [ss for ss in _streamsets if ss.get_preferred_type() == type_],
                'pipelines': [pipeline for pipeline in _pipelines if pipeline.source_type == type_]
            }
        structure[None] = {
            'streamsets': [ss for ss in _streamsets if ss.get_preferred_type() not in _preferred_types],
            'pipelines': [pipeline for pipeline in _pipelines if pipeline.source_type not in _preferred_types]
        }
        return structure


def get_streamsets_pipelines() -> Dict[IStreamSets, List[IPipeline]]:
    pipelines = inject.instance(IPipelineProvider).get_all()
    sp = {}
    for pipeline_ in pipelines:
        if streamsets := pipeline_.get_streamsets():
            if streamsets not in sp:
                sp[streamsets] = []
            sp[streamsets].append(pipeline_)
    for streamsets_ in inject.instance(IStreamSetsProvider).get_all():
        if streamsets_ not in sp:
            sp[streamsets_] = []
    return sp


def most_loaded_streamsets(streamsets_pipelines: Dict[IStreamSets, List[IPipeline]]) -> IStreamSets:
    return max(streamsets_pipelines, key=lambda x: len(streamsets_pipelines[x]))


def least_loaded_streamsets(streamsets_pipelines: Dict[IStreamSets, List[IPipeline]]) -> IStreamSets:
    return min(streamsets_pipelines, key=lambda x: len(streamsets_pipelines[x]))
