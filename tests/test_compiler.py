import pytest
import subprocess
import os

TEST_FILES = [
    "tests/hello.for",
    "tests/fatorial.for",
    "tests/primo.for",
    "tests/somaarr.for",
    "tests/conversor.for",
]

@pytest.mark.parametrize("source_file", TEST_FILES)
def test_compilation(source_file):
    # Ensure source file exists
    assert os.path.exists(source_file), f"{source_file} not found"
    
    # Run compiler
    result = subprocess.run(["python3", "src/main.py", source_file], capture_output=True, text=True)
    
    # Compilation should succeed
    assert result.returncode == 0, f"Compilation failed for {source_file}\nStdout: {result.stdout}\nStderr: {result.stderr}"
    assert "Compilation successful" in result.stdout
    
    # VM file should be generated
    base_name = os.path.splitext(source_file)[0]
    vm_file = base_name + ".vm"
    assert os.path.exists(vm_file), f"VM file {vm_file} was not generated"
    
    # Optional: Cleanup VM file after test
    # os.remove(vm_file)
