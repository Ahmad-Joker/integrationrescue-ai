"""Isolated entry point that executes customer handler code in a child process.

Invoked as: python -I runner.py <repo_dir> <tenant>   (event JSON on stdin)
Prints one JSON object: the handler result, or {"error": ...}.
"""

import json
import sys
import traceback


def main() -> None:
    repo_dir, tenant = sys.argv[1], sys.argv[2]
    sys.path.insert(0, repo_dir)
    event = json.loads(sys.stdin.read())
    try:
        from sync.handler import handle, load_tenant  # noqa: PLC0415 - loaded from repo_dir

        result = handle(event, load_tenant(tenant))
        print(json.dumps({"result": result}))
    except Exception as exc:
        print(json.dumps({"error": f"{type(exc).__name__}: {exc}",
                          "traceback": traceback.format_exc(limit=5)}))


if __name__ == "__main__":
    main()
