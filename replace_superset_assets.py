import json
import os
import sys
from pathlib import Path
from urllib.parse import quote

import yaml


def load_config():
    if len(sys.argv) != 2:
        raise RuntimeError(
            "Usage: replace_superset_assets.py <bundle_directory>"
        )

    bundle_dir = Path(sys.argv[1])

    if not bundle_dir.exists():
        raise RuntimeError(
            f"Bundle directory does not exist: {bundle_dir}"
        )

    config_raw = os.environ.get(
        "SUPERSET_DATA_SOURCES"
    )

    if not config_raw:
        raise RuntimeError(
            "SUPERSET_DATA_SOURCES is not configured"
        )

    config = json.loads(config_raw)

    if not isinstance(config, dict):
        raise RuntimeError(
            "SUPERSET_DATA_SOURCES must be a JSON object"
        )

    return bundle_dir, config


def resolve_bundle_root(bundle_dir: Path) -> Path:
    """
    Superset exports can be extracted in either of these forms:

        /tmp/work/
            databases/
            datasets/
            charts/

    or:

        /tmp/work/
            dashboard_export_xxx/
                databases/
                datasets/
                charts/

    Resolve both forms.
    """

    if (
        (bundle_dir / "databases").is_dir()
        or (bundle_dir / "datasets").is_dir()
    ):
        return bundle_dir

    directories = [
        path
        for path in bundle_dir.iterdir()
        if path.is_dir()
    ]

    if len(directories) == 1:
        candidate = directories[0]

        if (
            (candidate / "databases").is_dir()
            or (candidate / "datasets").is_dir()
        ):
            return candidate

    raise RuntimeError(
        "Could not determine Superset bundle root.\n"
        f"Working directory: {bundle_dir}\n"
        f"Contents: {list(bundle_dir.iterdir())}"
    )


def build_clickhouse_uri():
    host = os.environ["CLICKHOUSE_HOST"]
    port = os.environ["CLICKHOUSE_PORT"]
    database = os.environ["CLICKHOUSE_DATABASE"]
    username = os.environ["CLICKHOUSE_USERNAME"]
    password = os.environ["CLICKHOUSE_PASSWORD"]

    return (
        "clickhousedb://"
        f"{quote(username, safe='')}:"
        f"{quote(password, safe='')}"
        f"@{host}:{port}/{database}"
    )


def find_database_file(
    bundle_root: Path,
    database_name: str,
):
    databases_dir = bundle_root / "databases"

    if not databases_dir.exists():
        raise RuntimeError(
            "Bundle does not contain databases directory:\n"
            f"{databases_dir}\n"
            f"Bundle root: {bundle_root}"
        )

    matches = []

    for path in databases_dir.glob("*.yaml"):
        try:
            config = yaml.safe_load(
                path.read_text()
            )
        except Exception as exc:
            raise RuntimeError(
                f"Could not read database YAML: {path}"
            ) from exc

        if not isinstance(config, dict):
            continue

        name = (
            config.get("database_name")
            or config.get("name")
        )

        if name == database_name:
            matches.append(path)

    if not matches:
        raise RuntimeError(
            f"Could not find database asset for "
            f"'{database_name}' in {databases_dir}"
        )

    if len(matches) > 1:
        raise RuntimeError(
            f"Multiple database assets found for "
            f"'{database_name}': {matches}"
        )

    return matches[0]


def replace_database_uri(
    database_file: Path,
    database_uri: str,
):
    config = yaml.safe_load(
        database_file.read_text()
    )

    if not isinstance(config, dict):
        raise RuntimeError(
            f"Invalid database YAML: {database_file}"
        )

    original_uuid = config.get("uuid")

    config["sqlalchemy_uri"] = database_uri

    database_file.write_text(
        yaml.safe_dump(
            config,
            sort_keys=False,
            default_flow_style=False,
        )
    )

    database_name = (
        config.get("database_name")
        or config.get("name")
        or database_file.stem
    )

    print(
        f"Updated database URI for: {database_name}"
    )

    if original_uuid:
        print(
            f"Database UUID preserved: {original_uuid}"
        )

    return original_uuid


def update_datasets(
    bundle_root: Path,
    database_uuid: str,
    dataset_names: list[str],
):
    datasets_dir = bundle_root / "datasets"

    if not datasets_dir.is_dir():
        raise RuntimeError(
            f"Bundle does not contain datasets directory: "
            f"{datasets_dir}"
        )

    requested = set(dataset_names)

    dataset_files = list(
        datasets_dir.rglob("*.yaml")
    )

    if not dataset_files:
        raise RuntimeError(
            f"No dataset YAML files found under: "
            f"{datasets_dir}"
        )

    found = set()

    print()
    print("Dataset assets found:")

    for dataset_file in dataset_files:

        config = yaml.safe_load(
            dataset_file.read_text()
        )

        if not isinstance(config, dict):
            continue

        table_name = config.get("table_name")

        print(
            f"  {dataset_file.relative_to(bundle_root)}"
            f" -> table_name={table_name}"
        )

        matched_dataset = None

        for requested_name in requested:
            if table_name == requested_name:
                matched_dataset = requested_name
                break

        # Filename fallback:
        # access_logs_4.yaml -> access_logs
        if matched_dataset is None:
            filename = dataset_file.stem

            for requested_name in requested:
                if (
                    filename == requested_name
                    or filename.startswith(
                        f"{requested_name}_"
                    )
                ):
                    matched_dataset = requested_name
                    break

        if matched_dataset is None:
            continue

        found.add(matched_dataset)

        old_database_uuid = config.get(
            "database_uuid"
        )

        config["database_uuid"] = database_uuid

        dataset_file.write_text(
            yaml.safe_dump(
                config,
                sort_keys=False,
                default_flow_style=False,
            )
        )

        print(
            f"Updated dataset: {matched_dataset}"
        )

        print(
            f"  File: "
            f"{dataset_file.relative_to(bundle_root)}"
        )

        if old_database_uuid:
            print(
                f"  database_uuid: "
                f"{old_database_uuid} -> "
                f"{database_uuid}"
            )

    missing = requested - found

    if missing:
        raise RuntimeError(
            "Configured datasets were not found in bundle: "
            f"{sorted(missing)}"
        )

def main():
    bundle_dir, config = load_config()

    database_name = config.get("name")

    if not database_name:
        raise RuntimeError(
            "SUPERSET_DATA_SOURCES.name is required"
        )

    dataset_names = config.get(
        "datasets",
        [],
    )

    if not isinstance(dataset_names, list):
        raise RuntimeError(
            "SUPERSET_DATA_SOURCES.datasets must be a list"
        )

    print()
    print(
        "============================================================"
    )
    print(
        "Updating Superset bundle configuration"
    )
    print(
        "============================================================"
    )

    print()
    print(
        f"Target Superset database: {database_name}"
    )

    print(
        f"Target datasets: "
        f"{', '.join(dataset_names)}"
    )

    # ------------------------------------------------------------
    # Resolve actual Superset export root
    # ------------------------------------------------------------

    bundle_root = resolve_bundle_root(
        bundle_dir
    )

    print()
    print(
        f"Superset bundle root:"
    )
    print(
        bundle_root
    )

    # ------------------------------------------------------------
    # Database
    # ------------------------------------------------------------

    database_file = find_database_file(
        bundle_root,
        database_name,
    )

    print()
    print(
        f"Found database asset:"
    )
    print(
        database_file
    )

    database_uri = build_clickhouse_uri()

    print()
    print(
        "Updating ClickHouse connection details..."
    )

    database_uuid = replace_database_uri(
        database_file,
        database_uri,
    )

    if not database_uuid:
        raise RuntimeError(
            "Database asset does not contain a UUID"
        )

    # ------------------------------------------------------------
    # Datasets
    # ------------------------------------------------------------

    if dataset_names:
        print()
        print(
            "Updating dataset database references..."
        )

        update_datasets(
            bundle_root,
            database_uuid,
            dataset_names,
        )
    else:
        print()
        print(
            "No datasets configured."
        )

    print()
    print(
        "Superset bundle configuration "
        "updated successfully."
    )


if __name__ == "__main__":
    main()
