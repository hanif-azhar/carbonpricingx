from unittest.mock import patch

from carbon_pricing_x.cli import main


def test_cli_run_builds_streamlit_command():
    with patch("carbon_pricing_x.cli.subprocess.call", return_value=0) as call_mock:
        code = main(["run", "--port", "8600", "--headless"])

    assert code == 0
    cmd = call_mock.call_args.args[0]
    assert "streamlit" in cmd
    assert "run" in cmd
    assert "--server.port" in cmd
    assert "8600" in cmd
    assert "--server.headless" in cmd
