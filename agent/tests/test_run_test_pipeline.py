from agent import cli


def test_run_pipeline(cli_runner):
    result = cli_runner.invoke(cli.run_test_pipeline, catch_exceptions=False)
    print(f"run_test_pipeline: {result.exit_code} {result.output}")

    assert result.exit_code == 0
