import unittest

from unittest.mock import MagicMock, Mock
from sdc_client import StreamsetsBalancer, client, balancer
from mocks import StreamSetsMock, PipelineMock


class TestStreamSetsBalancer(unittest.TestCase):
    def setUp(self):
        client.get_pipeline_status = MagicMock(return_value='bla')
        client.delete = Mock()
        client.create = Mock()
        balancer.get_streamsets_pipelines = MagicMock(return_value={StreamSetsMock(): [PipelineMock()]})
        self.balancer = StreamsetsBalancer()
        self.balancer.logger = Mock()
        self.balancer.logger.info = Mock()
        self.balancer.pipeline_provider = Mock()
        self.balancer.pipeline_provider.save = Mock()

    def test_balanced(self):
        assert self.balancer.is_balanced(self.balancer.streamsets_pipelines)

    def test_balanced_2(self):
        self.balancer.streamsets_pipelines = {
            StreamSetsMock(): [PipelineMock()],
            StreamSetsMock(): [PipelineMock()],
            StreamSetsMock(): [PipelineMock()]
        }
        assert self.balancer.is_balanced(self.balancer.streamsets_pipelines)

    def test_not_balanced(self):
        streamsets_pipelines = {
            StreamSetsMock(): [PipelineMock(), PipelineMock()],
            StreamSetsMock(): []}
        assert not self.balancer.is_balanced(streamsets_pipelines)

    def test_not_balanced_2(self):
        streamsets_pipelines = {
            StreamSetsMock(): [PipelineMock(), PipelineMock()],
            StreamSetsMock(): [PipelineMock(), PipelineMock()],
            StreamSetsMock(): [],
        }
        assert not self.balancer.is_balanced(streamsets_pipelines)

    def test_balanced_specific_1(self):
        streamsets_pipelines = {
            StreamSetsMock(type_='dir'): [
                PipelineMock(type_='dir'),
                PipelineMock(type_='dir'),
                PipelineMock(type_='dir'),
                PipelineMock(type_='dir'),
            ],
            StreamSetsMock(): [
                PipelineMock(type_='1'),
            ],
        }
        assert self.balancer.is_balanced(streamsets_pipelines)

    def test_balanced_specific_2(self):
        streamsets_pipelines = {
            StreamSetsMock(type_='dir'): [
                PipelineMock(type_='dir'),
                PipelineMock(type_='dir'),
                PipelineMock(type_='dir'),
                PipelineMock(type_='dir'),
                PipelineMock(type_='dir'),
                PipelineMock(type_='dir'),
                PipelineMock(type_='dir'),
            ],
            StreamSetsMock(type_='not_dir'): [
                PipelineMock(type_='not_dir'),
            ],
        }
        assert self.balancer.is_balanced(streamsets_pipelines)

    def test_balanced_specific_3(self):
        streamsets_pipelines = {
            StreamSetsMock(type_='dir'): [
                PipelineMock(type_='dir'),
                PipelineMock(type_='dir'),
                PipelineMock(type_='dir'),
                PipelineMock(type_='dir'),
                PipelineMock(type_='dir'),
                PipelineMock(type_='dir'),
                PipelineMock(type_='dir'),
            ],
            StreamSetsMock(): [
                PipelineMock(type_='1'),
            ],
            StreamSetsMock(): [
                PipelineMock(type_='1'),
                PipelineMock(type_='1'),
            ],
        }
        assert self.balancer.is_balanced(streamsets_pipelines)


    def test_not_balanced_specific_1(self):
        streamsets_pipelines = {
            StreamSetsMock(type_='dir'): [
                PipelineMock(type_='dir'),
                PipelineMock(type_='dir'),
            ],
            StreamSetsMock(): [
                PipelineMock(),
                PipelineMock(type_='dir'),
            ],
        }
        assert not self.balancer.is_balanced(streamsets_pipelines)

    def test_not_balanced_specific_2(self):
        streamsets_pipelines = {
            StreamSetsMock(type_='dir'): [
                PipelineMock(type_='not_dir'),
                PipelineMock(type_='dir'),
                PipelineMock(type_='dir'),
            ],
            StreamSetsMock(type_='not_dir'): [
                PipelineMock(type_='not_dir'),
            ],
        }
        assert not self.balancer.is_balanced(streamsets_pipelines)

    def test_balance(self):
        s1 = StreamSetsMock()
        s2 = StreamSetsMock()
        s3 = StreamSetsMock()
        s4 = StreamSetsMock()
        self.balancer.streamsets_pipelines = {
            s1: [PipelineMock(), PipelineMock(), PipelineMock()],
            s2: [],
            s3: [PipelineMock()],
            s4: [],
        }
        self.balancer.balance()
        assert len(self.balancer.streamsets_pipelines[s1]) == 1
        assert len(self.balancer.streamsets_pipelines[s2]) == 1
        assert len(self.balancer.streamsets_pipelines[s3]) == 1
        assert len(self.balancer.streamsets_pipelines[s4]) == 1

    def test_balance_2(self):
        s1 = StreamSetsMock()
        s2 = StreamSetsMock()
        s3 = StreamSetsMock()
        self.balancer.streamsets_pipelines = {
            s1: [PipelineMock(), PipelineMock(), PipelineMock(), PipelineMock()],
            s2: [],
            s3: [],
        }
        self.balancer.balance()
        assert len(self.balancer.streamsets_pipelines[s1]) == 2
        assert len(self.balancer.streamsets_pipelines[s2]) == 1
        assert len(self.balancer.streamsets_pipelines[s3]) == 1

    def test_specific_streamsets(self):
        s1 = StreamSetsMock(type_='dir')
        s2 = StreamSetsMock()
        s3 = StreamSetsMock(type_='not_dir')
        data = {
            s1: [PipelineMock(type_='dir'),
                 PipelineMock(type_='dir'),
                 PipelineMock(type_='dir'),
                 PipelineMock(type_='dir'),
                 PipelineMock(type_='dir'),
                 PipelineMock(type_='dir'),
                 PipelineMock(type_='dir'),
                 PipelineMock(type_='1'),
                 PipelineMock(type_='1'),
                 PipelineMock(type_='1'),
                 PipelineMock(type_='1'),
                 PipelineMock(type_='1'),
                 PipelineMock(type_='not_dir'),
                 ],
            s2: [
                PipelineMock(type_='1'),
            ],
            s3: [
                PipelineMock(type_='dir'),
                PipelineMock(type_='1'),
                PipelineMock(type_='1'),
                PipelineMock(type_='not_dir'),
            ],
        }

        def _move(self, pipeline_, to_streamsets):
            for ss in self.streamsets_pipelines:
                if pipeline_ in self.streamsets_pipelines[ss]:
                    self.streamsets_pipelines[ss].remove(pipeline_)
            self.streamsets_pipelines[to_streamsets].append(pipeline_)

        balancer.get_streamsets_pipelines = lambda: data.copy()
        balancer.StreamsetsBalancer._move = _move
        balancer_ = balancer.StreamsetsBalancer()
        balancer_.balance()

        assert balancer_.is_balanced(balancer_.streamsets_pipelines)

        balancer_2 = balancer.StreamsetsBalancer()
        balancer_2.rebalance_map = balancer_.rebalance_map
        balancer_2._apply_rebalance_map()

        assert balancer_.is_balanced(balancer_2.streamsets_pipelines)
        assert len(balancer_.streamsets_pipelines[s1]) == 8
        assert len(balancer_.streamsets_pipelines[s2]) == 5
        assert len(balancer_.streamsets_pipelines[s3]) == 5
        assert all([p.source_type == 'dir' for p in balancer_.streamsets_pipelines[s1]])
        assert all([p.source_type == '1' for p in balancer_.streamsets_pipelines[s2]])


if __name__ == '__main__':
    unittest.main()
