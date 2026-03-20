"""ElectroSwap entry point."""

import os
import argparse
from app import create_app

app = create_app()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the ElectroSwap Flask app.")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the application on (default: 5000).")
    args = parser.parse_args()
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, port=args.port)
