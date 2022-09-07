import unittest
import inject

from sdc_client import balancer
from conftest import StreamSetsMock, PipelineMock, instance


class TestBalancer(unittest.TestCase):
    def setUp(self):
        inject.instance = instance

    def test_get_streamsets_pipelines(self):
        print(balancer.get_streamsets_pipelines)
        sp = balancer.get_streamsets_pipelines()
        assert len(sp.keys()) == 2

    def test_most_loaded_streamsets(self):
        s1 = StreamSetsMock()
        s2 = StreamSetsMock()
        r = balancer.most_loaded_streamsets({
            s1: [PipelineMock()],
            s2: []
        })
        assert r == s1

    def test_most_loaded_streamsets_2(self):
        s1 = StreamSetsMock()
        s2 = StreamSetsMock()
        s3 = StreamSetsMock()
        r = balancer.most_loaded_streamsets({
            s1: [PipelineMock(), PipelineMock()],
            s2: [],
            s3: [PipelineMock(), PipelineMock(), PipelineMock()],
        })
        assert r == s3

    def test_least_loaded_streamsets(self):
        s1 = StreamSetsMock()
        s2 = StreamSetsMock()
        r = balancer.least_loaded_streamsets({
            s1: [PipelineMock()],
            s2: []
        })
        assert r == s2

    def test_least_loaded_streamsets_2(self):
        s1 = StreamSetsMock()
        s2 = StreamSetsMock()
        s3 = StreamSetsMock()
        r = balancer.least_loaded_streamsets({
            s1: [PipelineMock(), PipelineMock()],
            s2: [],
            s3: [PipelineMock(), PipelineMock(), PipelineMock()],
        })
        assert r == s2


if __name__ == '__main__':
    unittest.main()
