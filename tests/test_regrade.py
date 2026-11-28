from pathlib import Path

import pytest

from scripts.regrade import main

data_dir = Path(__file__).resolve().parents[1] / "data" / "2026-11-19"


def test_regrades_thru_files_with_exact_output(capsys):

    main(["thru", str(data_dir), "thru_*.csv"])

    expected = "\n".join(
        [
            "thru_115311.csv  PASS  worst error +0.061 dB at 504.022 MHz",
            "thru_120355.csv  FAIL  worst error +97.135 dB at 63.047 MHz",
            "thru_120501.csv  PASS  worst error -0.069 dB at 315.033 MHz",
            "thru_124329.csv  PASS  worst error +0.090 dB at 315.033 MHz",
            "thru_125148.csv  PASS  worst error +0.033 dB at 540.020 MHz",
            "thru_130257.csv  PASS  worst error -0.057 dB at 315.033 MHz",
            "thru_slot0_130357.csv  FAIL  worst error -0.288 dB at 405.027 MHz",
            "thru_slot0_130448.csv  FAIL  worst error -0.287 dB at 405.027 MHz",
            "thru_slot2_173853.csv  PASS  worst error +0.045 dB at 486.023 MHz",
            "thru_slot3_173825.csv  FAIL  worst error -10.006 dB at 414.027 MHz",
            "6 PASS, 4 FAIL",
            "",
        ]
    )
    assert capsys.readouterr().out == expected

    main(["pad_3db", str(data_dir), "pad_3db_*.csv"])

    expected = "\n".join(
        [
            "pad_3db_padded_10db_run1_170211.csv  FAIL  worst error -0.215 dB at 0.050 MHz",
            "pad_3db_padded_10db_run2_171229.csv  FAIL  worst error -0.205 dB at 0.050 MHz",
            "pad_3db_run1_123117.csv  FAIL  worst error -0.359 dB at 549.019 MHz",
            "pad_3db_run2_123152.csv  FAIL  worst error -0.347 dB at 567.019 MHz",
            "0 PASS, 4 FAIL",
            "",
        ]
    )

    assert capsys.readouterr().out == expected


def test_faulty_inputs_raise():
    relative_data_dir = Path("data") / "2026-11-19"
    with pytest.raises(SystemExit) as exc_info:
        main(["thru", str(relative_data_dir), "nothing_*.csv"])
    assert str(exc_info.value) == (
        f"No files match 'nothing_*.csv' in {relative_data_dir}"
    )
    with pytest.raises(ValueError, match="pad_7db is not found in part database"):
        main(["pad_7db", str(data_dir), "pad_*.csv"])
