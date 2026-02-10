# BuyWander Hunter

A tool to scrape and monitor BuyWander auctions for specific interests.

## Setup

1.  Install dependencies:
    ```bash
    make install
    ```

2.  Run the web app:
    ```bash
    ./run_web.sh
    ```

## Development

### Linting and Formatting

This project uses `black`, `flake8`, `isort`, and `djlint` to ensure code quality and consistent formatting.

To install development dependencies:
```bash
make install-dev
```

To run linting checks:
```bash
make lint
```

To automatically format code:
```bash
make format
```

### Configuration

-   **Python Formatting**: Configured in `pyproject.toml` (Black, Isort).
-   **Python Linting**: Configured in `.flake8`.
-   **Template Linting**: Configured in `.djlintrc`.
