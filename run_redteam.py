# run_redteam.py
import argparse

from pipeline import run_baseline, run_with_firewall
from metrics import main_summary


def main():
    parser = argparse.ArgumentParser(
        description="Groq-based LLM Red-Teaming Pipeline (baseline vs firewall vs metrics)"
    )
    parser.add_argument(
        "--mode",
        choices=["baseline", "firewall", "both", "metrics"],
        default="both",
        help="Which mode to run.",
    )
    args = parser.parse_args()

    if args.mode in ("baseline", "both"):
        run_baseline()

    if args.mode in ("firewall", "both"):
        run_with_firewall()

    if args.mode == "metrics":
        main_summary()


if __name__ == "__main__":
    main()
