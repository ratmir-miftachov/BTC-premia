import os
import subprocess
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import pdist
from scipy.stats.mstats import gmean


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
Q_MATRIX_DIR = FIXTURES / "Q_matrix" / "Tau-independent" / "unique" / "moneyness_step_0d01"


class ReproducibilitySmokeTest(unittest.TestCase):
    def test_fixture_manifest_is_valid(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "check_reproducibility.py"),
                "--manifest",
                str(FIXTURES / "data_manifest.yaml"),
                "--base-path",
                str(FIXTURES),
                "--strict",
            ],
            check=False,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_iv_surface_fixture_parses(self):
        path = FIXTURES / "IV" / "IV_surface_SVI" / "Tau-independent" / "unique" / "moneyness_step_0d01" / "interpolated_2020-01-01_allR2.csv"
        df = pd.read_csv(path)
        self.assertEqual(list(df.columns[:2]), ["Date", "TTM"])
        self.assertEqual(int(df.loc[0, "TTM"]), 27)
        self.assertTrue(np.isfinite(df.drop(columns=["Date", "TTM"]).to_numpy()).all())

    def test_q_density_fixture_parses(self):
        path = FIXTURES / "Q_from_pure_SVI" / "Tau-independent" / "unique" / "moneyness_step_0d01" / "tau_27" / "btc_Q_2020-01-01.csv"
        df = pd.read_csv(path)
        self.assertTrue({"m", "spdy"}.issubset(df.columns))
        self.assertGreater(np.trapz(df["spdy"], df["m"]), 0)

    def test_miniature_clustering_flow(self):
        matrices = [
            pd.read_csv(Q_MATRIX_DIR / f"Q_matrix_{ttm}day_0d15.csv")
            for ttm in (5, 9, 14, 27)
        ]
        common_dates = set(matrices[0].columns[1:])
        for matrix in matrices[1:]:
            common_dates &= set(matrix.columns[1:])
        common_dates = sorted(common_dates)
        self.assertEqual(common_dates, ["2020-01-01", "2020-01-02"])

        vectors = []
        for date in common_dates:
            parts = []
            for matrix in matrices:
                density = matrix[date].to_numpy()
                parts.append(np.log(density) - np.log(gmean(density)))
            vectors.append(np.concatenate(parts))

        distances = pdist(np.array(vectors), "euclidean")
        tree = linkage(distances, method="ward")
        self.assertEqual(tree.shape, (1, 4))

    def test_market_regime_clustering_script_runs_on_fixtures(self):
        env = os.environ.copy()
        env["BTC_PREMIA_BASE"] = str(FIXTURES)
        env["MPLBACKEND"] = "Agg"
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "src" / "04_clustering" / "market_regime_clustering.py"),
            ],
            check=False,
            text=True,
            capture_output=True,
            env=env,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
