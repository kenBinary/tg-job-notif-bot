import argparse


def init_cli_args():
    parser = argparse.ArgumentParser(description="Job Notification Bot")
    parser.add_argument("--dev", action="store_true", help="Run in development mode")
    parser.add_argument("--prod", action="store_true", help="Run in production mode")

    args = parser.parse_args()

    if args.dev and args.prod:
        parser.error("Cannot specify both --dev and --prod")

    return args
