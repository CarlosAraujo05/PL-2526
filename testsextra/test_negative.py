import pytest
import subprocess
import os


def compile_source(source_path: str) -> subprocess.CompletedProcess:
    """Run the compiler on a Fortran source file and return the result."""
    return subprocess.run(
        ["python3", "src/main.py", source_path],
        capture_output=True,
        text=True
    )


# ============================================================================
# PARAMETER DECLARATION TESTS
# ============================================================================

def test_param_valid_compiles():
    """Valid PARAMETER usage should compile successfully."""
    result = compile_source("tests/param_valid.for")
    assert result.returncode == 0, (
        f"Compilation failed unexpectedly\nStdout: {result.stdout}\nStderr: {result.stderr}"
    )
    assert "Compilation successful" in result.stdout
    vm_file = "tests/param_valid.vm"
    assert os.path.exists(vm_file), f"VM file {vm_file} was not generated"


def test_param_dup_fails():
    """Duplicate PARAMETER declaration should be rejected."""
    result = compile_source("tests/param_dup.for")
    assert result.returncode != 0, "Expected compilation to fail"
    combined = result.stdout + result.stderr
    assert "Duplicate parameter declaration" in combined, (
        f"Expected 'Duplicate parameter declaration' in output, got stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_param_assign_fails():
    """Assignment to a PARAMETER should be rejected."""
    result = compile_source("tests/param_assign.for")
    assert result.returncode != 0, "Expected compilation to fail"
    combined = result.stdout + result.stderr
    assert "Cannot assign to parameter" in combined, (
        f"Expected 'Cannot assign to parameter' in output, got stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_param_array_fails():
    """PARAMETER on an array should be rejected."""
    result = compile_source("tests/param_array.for")
    assert result.returncode != 0, "Expected compilation to fail"
    combined = result.stdout + result.stderr
    assert "Cannot assign to array parameter" in combined, (
        f"Expected 'Cannot assign to array parameter' in output, got stdout={result.stdout!r} stderr={result.stderr!r}"
    )


# ============================================================================
# TYPE COMPATIBILITY TESTS (Strict policy per AGENTS.md)
# ============================================================================

def _write_temp_for(tmp_path, lines):
    """Write a temporary Fortran source file with fixed-format spacing."""
    path = tmp_path / "test.for"
    # Fixed format: statements start at column 7 (6 leading spaces)
    formatted = []
    for line in lines:
        if line.strip():
            formatted.append("      " + line + "\n")
        else:
            formatted.append("\n")
    path.write_text("".join(formatted), encoding="utf-8")
    return str(path)


def _assert_type_mismatch(result, description):
    """Helper: assert compilation failed with a type mismatch error."""
    assert result.returncode != 0, f"Expected compilation to fail for {description}"
    combined = result.stdout + result.stderr
    assert "Type mismatch" in combined, (
        f"Expected 'Type mismatch' in output for {description}, got stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_logical_to_integer_fails(tmp_path):
    """Assigning LOGICAL to INTEGER should be rejected."""
    source = _write_temp_for(tmp_path, [
        "PROGRAM T",
        "INTEGER I",
        "I = .TRUE.",
        "END"
    ])
    result = compile_source(source)
    _assert_type_mismatch(result, "LOGICAL -> INTEGER")


def test_logical_to_real_fails(tmp_path):
    """Assigning LOGICAL to REAL should be rejected."""
    source = _write_temp_for(tmp_path, [
        "PROGRAM T",
        "REAL R",
        "R = .TRUE.",
        "END"
    ])
    result = compile_source(source)
    _assert_type_mismatch(result, "LOGICAL -> REAL")


def test_integer_to_logical_fails(tmp_path):
    """Assigning INTEGER to LOGICAL should be rejected."""
    source = _write_temp_for(tmp_path, [
        "PROGRAM T",
        "LOGICAL L",
        "L = 1",
        "END"
    ])
    result = compile_source(source)
    _assert_type_mismatch(result, "INTEGER -> LOGICAL")


def test_real_to_logical_fails(tmp_path):
    """Assigning REAL to LOGICAL should be rejected."""
    source = _write_temp_for(tmp_path, [
        "PROGRAM T",
        "LOGICAL L",
        "L = 3.14",
        "END"
    ])
    result = compile_source(source)
    _assert_type_mismatch(result, "REAL -> LOGICAL")
