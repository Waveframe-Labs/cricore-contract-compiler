from __future__ import annotations

import argparse
from pathlib import Path

from .compile_policy_file import compile_policy_file


def main() -> None:

    parser = argparse.ArgumentParser(
        description="Compile a governance policy into a CRI-CORE compiled contract."
    )

    parser.add_argument(
        "policy",
        type=Path,
        help="Path to governance policy JSON file",
    )

    parser.add_argument(
        "output",
        type=Path,
        help="Output path for compiled contract JSON",
    )

    args = parser.parse_args()

    output_path = compile_policy_file(args.policy, args.output)

    print(f"Compiled contract written to: {output_path}")

if __name__ == "__main__":
    main()
    
