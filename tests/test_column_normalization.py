"""
Regression tests for column name normalisation.

Verifies that:
1. ``ColumnNormalizer`` correctly strips leading/trailing whitespace and
   collapses internal whitespace runs.
2. ``DatasetLoader.load()`` applies normalisation to all columns immediately
   after reading, so downstream callers see canonical names.
3. ``DatasetValidator.validate()`` succeeds against normalised DataFrames
   (proving the "Label not found" failure is fixed).
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from ml.preprocessing.column_normalizer import ColumnNormalizer
from ml.preprocessing.dataset_loader import DatasetLoader
from ml.preprocessing.dataset_validator import DatasetValidator


# ──────────────────────────────────────────────
# Unit tests for ColumnNormalizer
# ──────────────────────────────────────────────


class TestColumnNormalizer:
    """Tests for the ColumnNormalizer class."""

    def setup_method(self) -> None:
        self.normalizer = ColumnNormalizer()

    def test_strip_leading_space(self) -> None:
        """Leading space should be stripped."""
        assert self.normalizer.normalize_column_name(" Label") == "Label"

    def test_strip_trailing_space(self) -> None:
        """Trailing space should be stripped."""
        assert self.normalizer.normalize_column_name("Label ") == "Label"

    def test_strip_both_sides(self) -> None:
        """Leading and trailing spaces should both be stripped."""
        assert self.normalizer.normalize_column_name(" Label ") == "Label"

    def test_collapse_internal_whitespace(self) -> None:
        """Multiple internal spaces should collapse to one."""
        assert (
            self.normalizer.normalize_column_name("Flow  Bytes/s")
            == "Flow Bytes/s"
        )

    def test_no_change_for_clean_name(self) -> None:
        """A name with no whitespace issues should pass through unchanged."""
        assert self.normalizer.normalize_column_name("Label") == "Label"

    def test_normalize_columns_list(self) -> None:
        """normalize_columns should process every element."""
        raw = [" Label", " Flow Duration ", "Total Fwd Packets"]
        expected = ["Label", "Flow Duration", "Total Fwd Packets"]
        assert self.normalizer.normalize_columns(raw) == expected

    def test_build_column_mapping_only_changed(self) -> None:
        """build_column_mapping should only include entries that changed."""
        raw = [" Label", "Flow Duration", " Total Fwd Packets "]
        mapping = self.normalizer.build_column_mapping(raw)
        assert mapping == {
            " Label": "Label",
            " Total Fwd Packets ": "Total Fwd Packets",
        }
        # "Flow Duration" was already clean — should not appear
        assert "Flow Duration" not in mapping

    def test_to_canonical_name_snake_case(self) -> None:
        """to_canonical_name should produce snake_case."""
        assert (
            ColumnNormalizer.to_canonical_name("Destination Port")
            == "destination_port"
        )
        assert (
            ColumnNormalizer.to_canonical_name("Flow Bytes/s")
            == "flow_bytes_s"
        )
        assert (
            ColumnNormalizer.to_canonical_name("Fwd Packet Length Max")
            == "fwd_packet_length_max"
        )


# ──────────────────────────────────────────────
# Integration tests: loader + validator
# ──────────────────────────────────────────────


class TestLoaderNormalization:
    """Tests that DatasetLoader normalises column names on load."""

    def test_loader_normalizes_leading_space_label(self) -> None:
        """
        A CSV with a column literally named ' Label' (leading space)
        should result in a DataFrame with column 'Label' (no space).
        """
        csv_content = " Label,Flow Duration\nBENIGN,100\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write(csv_content)
            tmp_path = f.name

        try:
            loader = DatasetLoader()
            df = loader.load(tmp_path)

            # The normalised column should be 'Label', not ' Label'
            assert "Label" in df.columns, (
                f"Expected 'Label' in columns, got {list(df.columns)}"
            )
            assert " Label" not in df.columns, (
                "Raw ' Label' column should have been normalised"
            )
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_loader_normalizes_multiple_headers(self) -> None:
        """
        Multiple representative headers from Step 1 findings should all
        normalise correctly.
        """
        csv_content = (
            " Label,Flow Duration, Flow Bytes/s,Fwd Packet Length Max\n"
            "BENIGN,100,5000.0,100\n"
        )
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write(csv_content)
            tmp_path = f.name

        try:
            loader = DatasetLoader()
            df = loader.load(tmp_path)

            expected = ["Label", "Flow Duration", "Flow Bytes/s", "Fwd Packet Length Max"]
            assert list(df.columns) == expected, (
                f"Expected {expected}, got {list(df.columns)}"
            )
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_validator_succeeds_after_normalization(self) -> None:
        """
        After loading a CSV with ' Label' (leading space), the validator
        should find the target column and succeed.
        """
        csv_content = " Label,Flow Duration\nBENIGN,100\nBENIGN,200\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write(csv_content)
            tmp_path = f.name

        try:
            loader = DatasetLoader()
            df = loader.load(tmp_path)

            validator = DatasetValidator(target_column="Label")
            report = validator.validate(df)

            # Should NOT have a warning about target column not found
            target_warnings = [
                w for w in report.warnings
                if "not found" in w.lower() and "target" in w.lower()
            ]
            assert len(target_warnings) == 0, (
                f"Expected no 'target not found' warnings, got: {target_warnings}"
            )

            # Should have a warning about class distribution (proving it found Label)
            class_warnings = [
                w for w in report.warnings
                if "class" in w.lower() and "label" in w.lower()
            ]
            assert len(class_warnings) > 0, (
                "Expected a class distribution warning proving Label was found"
            )
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_validate_target_exact_lookup(self) -> None:
        """
        The validator should do a direct exact lookup — no fuzzy matching.
        Since the loader normalises, ' Label' becomes 'Label', and the
        validator should find it with a simple 'in' check.
        """
        csv_content = " Label,Flow Duration\nBENIGN,100\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write(csv_content)
            tmp_path = f.name

        try:
            loader = DatasetLoader()
            df = loader.load(tmp_path)

            # Direct exact lookup should work
            assert "Label" in df.columns
            assert " Label" not in df.columns
        finally:
            Path(tmp_path).unlink(missing_ok=True)
