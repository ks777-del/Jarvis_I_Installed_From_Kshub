from __future__ import annotations

import argparse
import json
import logging

from pptEngine import PPTGenerationEngine


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a designed PowerPoint presentation.")
    parser.add_argument("topic", help="Presentation topic")
    parser.add_argument("--style", default="professional", help="Style: bright | dark | professional")
    parser.add_argument("--slides", type=int, default=6, help="Total slide count")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="[ppt-generator] %(levelname)s: %(message)s")

    engine = PPTGenerationEngine()
    result = engine.generate_presentation(topic=args.topic, style=args.style, slide_count=args.slides)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
