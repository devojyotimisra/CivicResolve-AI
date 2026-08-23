import os
import sys

import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def main():
    openapi_schema = app.openapi()

    output_path = os.path.join(os.path.dirname(__file__), "..", "api_documentation.yaml")

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(
            openapi_schema,
            f,
            Dumper=NoAliasDumper,
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
        )


if __name__ == "__main__":
    main()
