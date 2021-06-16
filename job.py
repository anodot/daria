from pyflink.common.typeinfo import Types, BasicTypeInfo, BasicType
from pyflink.datastream import StreamExecutionEnvironment, SinkFunction
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, scoped_session


# engine = create_engine("mysql://root@127.0.0.1:3308/test")
# Session = scoped_session(sessionmaker(bind=engine))
from pyflink.java_gateway import get_gateway


class HttpSink(SinkFunction):

    def __init__(self, j_http_sink):
        super(HttpSink, self).__init__(sink_func=j_http_sink)

    @staticmethod
    def sink(url: str):
        gateway = get_gateway()
        HTTPConnectionConfig = gateway.jvm.net.galgus.flink.streaming.connectors.http.common.HTTPConnectionConfig
        connection_config = HTTPConnectionConfig(
            url,
            HTTPConnectionConfig.HTTPMethod.POST,
            ["Content-Type", "application/json"],
            False
        )
        bla = gateway.jvm.net.galgus.flink.streaming.connectors.http.HTTPSink
        sink = bla(connection_config)

        return HttpSink(j_http_sink=sink)


def foo(data):
    return str([{
        "value": data[0],
        "tags": {
            "source": ["anodot-agent"],
            "source_host_id": ["host_id"],
            "source_host_name": ["agent"],
            "pipeline_id": ["test_flink"],
            "pipeline_type": ["mysql"]
        }
    }]).replace("'", '"')


def tutorial():
    # session = Session()
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    # env.add_jars("file:///Users/antonzelenin/Workspace/daria/http.jar")

    # data = session.execute(f"""SELECT clicks, impressions FROM test""")
    data = [(1.0, 7)]
    ds = env.from_collection(
        collection=data,
        type_info=Types.ROW([Types.FLOAT(), Types.INT()])
    )
    ds = ds.map(foo, BasicTypeInfo(BasicType.STRING))
    # ds.add_sink(HttpSink.sink('http://localhost:8080/api/v1/metrics?token=asdf&protocol=anodot20'))
    ds.add_sink(HttpSink.sink('http://dummy_destination:80/api/v1/metrics?token=asdf&protocol=anodot20'))
    env.execute("tutorial")


if __name__ == '__main__':
    tutorial()
