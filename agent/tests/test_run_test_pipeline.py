from agent import cli


def test_run_pipeline(cli_runner):
    result = cli_runner.invoke(cli.run_test_pipeline, catch_exceptions=False)
    print(f"run_test_pipeline: {result.exit_code} {result.output}")

    assert result.exit_code == 0
    assert "Source run_test_pipeline created" in result.output
    assert "Pipeline run_test_pipeline is starting" in result.output
    assert "Test run OK" in result.output
