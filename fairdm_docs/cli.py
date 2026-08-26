"""
FairDM Documentation CLI Tool

Provides command-line interface for building and validating Sphinx documentation
with sensible defaults for FairDM-powered research data portals.
"""

import os
import socket
import subprocess
import sys
from pathlib import Path
from typing import Annotated

import typer

from fairdm_docs.config import ConfigError, load_config

app = typer.Typer(
    name="fairdm-docs",
    help="FairDM documentation CLI tool",
    add_completion=False,
)


def is_port_available(port: int) -> bool:
    """
    Check if a port is available for binding.

    Args:
        port: Port number to check

    Returns:
        True if port is available, False if occupied
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("", port))
            return True
    except OSError:
        return False


def get_verbosity_flags(verbosity: str) -> list[str]:
    """
    Convert verbosity level to Sphinx command-line flags.

    Args:
        verbosity: Verbosity level (full, quiet, errors-only)

    Returns:
        List of Sphinx flags for the verbosity level
    """
    if verbosity == "quiet":
        return ["-q"]
    elif verbosity == "errors-only":
        return ["-Q"]
    else:  # full
        return []


@app.command()
def build(
    live: Annotated[
        bool,
        typer.Option(
            "--live",
            help="Start live preview server with auto-reload",
        ),
    ] = False,
) -> None:
    """
    Build Sphinx documentation with sensible defaults.

    Reads configuration from [tool.fairdm.docs] in pyproject.toml.
    Falls back to convention-based defaults if not configured.
    """
    try:
        # Load and validate configuration
        config = load_config()

        # Determine which conf.py to use:
        # Prefer local docs/conf.py if it exists, otherwise use package's conf.py
        local_conf_py = config.source_dir / "conf.py"
        # Falls back to the package's built-in conf.py when the project has none.
        conf_dir = (
            config.source_dir if local_conf_py.exists() else Path(__file__).parent
        )

        # Set environment variables for conf.py to use
        os.environ["FAIRDM_DOCS_DJANGO"] = "true" if config.django else "false"
        # Pass the project directory (where CLI was invoked) to conf.py
        # This is needed because Sphinx changes cwd to the conf.py location
        os.environ["FAIRDM_DOCS_PROJECT_DIR"] = str(Path.cwd().resolve())

        if live:
            # Check port availability (T042)
            if not is_port_available(config.port):
                typer.echo(
                    f"❌ Error: Port {config.port} is already in use.\n"
                    f"   Configure a different port in pyproject.toml:\n"
                    f"   [tool.fairdm.docs]\n"
                    f"   port = {config.port + 1}",
                    err=True,
                )
                raise typer.Exit(code=1)

            # Start live preview server (T043, T044, T046)
            typer.echo(
                f"🔄 Starting live preview server on http://localhost:{config.port}"
            )
            typer.echo("   Press Ctrl+C to stop the server\n")

            # Prepare sphinx-autobuild command
            sphinx_autobuild_args = [
                sys.executable,
                "-m",
                "sphinx_autobuild",
                "--port",
                str(config.port),
                "--open-browser",
                "-c",
                str(conf_dir),
                str(config.source_dir),
                str(config.build_dir),
            ]

            # Add verbosity flags
            verbosity_flags = get_verbosity_flags(config.verbosity)
            if verbosity_flags:
                sphinx_autobuild_args.extend(verbosity_flags)

            try:
                # Run sphinx-autobuild (blocks until Ctrl+C) (T045)
                # Don't capture output so user can see what's happening
                process = subprocess.run(sphinx_autobuild_args, check=False)  # noqa: S603 - argv is built from sys.executable and validated build settings

                # If process exited with error, show helpful message
                if process.returncode != 0:
                    typer.echo(
                        f"\n❌ Live server exited with code {process.returncode}\n"
                        f"   Check the output above for error details.",
                        err=True,
                    )

                raise typer.Exit(code=process.returncode)
            except KeyboardInterrupt:
                typer.echo("\n⚠️  Server stopped by user")
                raise typer.Exit(code=0) from None
            except FileNotFoundError:
                typer.echo(
                    "❌ Error: sphinx-autobuild not found.\n   Install with: pip install sphinx-autobuild",
                    err=True,
                )
                raise typer.Exit(code=1) from None

        # Build with Sphinx
        typer.echo("📚 Building documentation...")

        # Import sphinx.cmd.build here to avoid import errors if not installed
        try:
            from sphinx.cmd.build import main as sphinx_build
        except ImportError:
            typer.echo(
                "❌ Error: Sphinx not found. Install with: pip install sphinx", err=True
            )
            raise typer.Exit(code=1) from None

        # Prepare Sphinx arguments
        verbosity_flags = get_verbosity_flags(config.verbosity)

        # Create build directory if it doesn't exist
        config.build_dir.parent.mkdir(parents=True, exist_ok=True)

        sphinx_args = [
            "-b",
            "html",  # HTML builder
            "-c",
            str(conf_dir),
            *verbosity_flags,  # Verbosity flags
            str(config.source_dir),  # Source directory
            str(config.build_dir),  # Output directory
        ]

        # Run Sphinx build
        exit_code = sphinx_build(sphinx_args)

        if exit_code == 0:
            typer.echo(f"✅ Build complete! Output: {config.build_dir}")
        else:
            typer.echo("❌ Build failed. See errors above.", err=True)

        raise typer.Exit(code=exit_code)

    except ConfigError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1) from None
    except KeyboardInterrupt:
        typer.echo("\n⚠️  Build interrupted by user", err=True)
        raise typer.Exit(code=130) from None


@app.command()
def check() -> None:
    """
    Validate documentation for quality issues.

    Currently checks:
    - Broken internal and external links (linkcheck)

    Exits with code 0 if validation passes, code 1 if errors found.
    """
    try:
        # Load and validate configuration (T053)
        config = load_config()

        # Determine which conf.py to use:
        # Prefer local docs/conf.py if it exists, otherwise use package's conf.py
        local_conf_py = config.source_dir / "conf.py"
        # Falls back to the package's built-in conf.py when the project has none.
        conf_dir = (
            config.source_dir if local_conf_py.exists() else Path(__file__).parent
        )

        # Set environment variables for conf.py to use
        os.environ["FAIRDM_DOCS_DJANGO"] = "true" if config.django else "false"
        # Pass the project directory (where CLI was invoked) to conf.py
        # This is needed because Sphinx changes cwd to the conf.py location
        os.environ["FAIRDM_DOCS_PROJECT_DIR"] = str(Path.cwd().resolve())

        typer.echo("🔍 Checking documentation for broken links...")

        # Import sphinx.cmd.build here to avoid import errors if not installed
        try:
            from sphinx.cmd.build import main as sphinx_build
        except ImportError:
            typer.echo(
                "❌ Error: Sphinx not found. Install with: pip install sphinx", err=True
            )
            raise typer.Exit(code=1) from None

        # Prepare linkcheck output directory (T054)
        linkcheck_dir = config.build_dir.parent / "linkcheck"
        linkcheck_dir.mkdir(parents=True, exist_ok=True)

        # Prepare Sphinx linkcheck arguments
        verbosity_flags = get_verbosity_flags(config.verbosity)

        sphinx_args = [
            "-b",
            "linkcheck",  # Linkcheck builder
            "-c",
            str(conf_dir),
            *verbosity_flags,  # Verbosity flags
            str(config.source_dir),  # Source directory
            str(linkcheck_dir),  # Output directory for linkcheck
        ]

        # Run Sphinx linkcheck
        exit_code = sphinx_build(sphinx_args)

        # Parse linkcheck output (T055)
        output_file = linkcheck_dir / "output.txt"

        if output_file.exists():
            broken_links = []
            with open(output_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Parse linkcheck output format: "filename.rst:line: [status] url: error"
                    if line and (
                        ": [broken]" in line or ": [redirected]" in line.lower()
                    ):
                        broken_links.append(line)

            if broken_links:
                # Display broken links (T056, T058)
                typer.echo(
                    f"\n❌ Found {len(broken_links)} broken link(s):\n", err=True
                )
                for link in broken_links:
                    typer.echo(f"   {link}", err=True)
                typer.echo("", err=True)
                raise typer.Exit(code=1)  # T059
            else:
                # Success message (T057)
                typer.echo("✅ All links are valid!")
                raise typer.Exit(code=0)  # T059
        else:
            # If no output file, check exit code
            if exit_code == 0:
                typer.echo("✅ Link check complete!")
                raise typer.Exit(code=0)
            else:
                typer.echo("❌ Link check failed. See errors above.", err=True)
                raise typer.Exit(code=1)

    except ConfigError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1) from None
    except KeyboardInterrupt:
        typer.echo("\n⚠️  Check interrupted by user", err=True)
        raise typer.Exit(code=130) from None


def main() -> None:
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
