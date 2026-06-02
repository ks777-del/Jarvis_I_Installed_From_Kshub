from __future__ import annotations

import argparse
import json
import logging

from engine import CanvaPPTGenerationEngine


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate PowerPoint presentation")
    parser.add_argument("prompt")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="[ppt_generator] %(levelname)s: %(message)s")
    result = CanvaPPTGenerationEngine().generate(args.prompt)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
