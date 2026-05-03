from __future__ import annotations

from pathlib import Path

from .load_policy import load_policy
from .compile_policy import compile_policy
from .write_compiled_contract import write_compiled_contract


def compile_policy_file(policy_path: Path, output_path: Path) -> Path:
    """
    Compile a governance policy file into a compiled contract artifact.

    Steps:
    1. Load policy from disk
    2. Compile policy into contract structure
    3. Write compiled contract artifact

    Returns:
        Path to the compiled contract artifact.
    """

    policy = load_policy(policy_path)

    compiled_contract = compile_policy(policy)

    written_path = write_compiled_contract(compiled_contract, output_path)

    return written_path
    
