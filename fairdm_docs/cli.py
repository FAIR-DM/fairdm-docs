"""The `fairdm-docs` command: build, preview and check a portal's documentation."""

import os
import socket
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Annotated

import typer

from fairdm_docs.config import (
    ERROR_MESSAGES,
    BuildConfiguration,
    ConfigError,
    load_config,
)

app = typer.Typer(
    name="fairdm-docs",
    help="FairDM documentation CLI tool",
    add_completion=False,
)


def is_port_available(port: int) -> bool:
    """Check if a port is available for binding.

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


@contextmanager
def _build_settings(config: BuildConfiguration) -> Iterator[None]:
    """Expose the settings conf.py reads, for the duration of the build.

    conf.py cannot be passed arguments — Sphinx imports it — so the two settings it
    needs travel as environment variables. The project directory is the one the
    command was run from, which conf.py cannot work out for itself once Sphinx has
    changed directory to the location of conf.py.

    Both values are restored when the build finishes. A command that left them behind
    would go on deciding the project directory for every later build in the same
    process, from a directory those builds have nothing to do with.

    Args:
        config: The build configuration whose Django setting conf.py needs.
    """
    settings = {
        "FAIRDM_DOCS_DJANGO": "true" if config.django else "false",
        "FAIRDM_DOCS_PROJECT_DIR": str(Path.cwd().resolve()),
    }
    previous = {name: os.environ.get(name) for name in settings}
    os.environ.update(settings)
    try:
        yield
    finally:
        for name, was_set_to in previous.items():
            if was_set_to is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = was_set_to


def _conf_dir(config: BuildConfiguration) -> Path:
    """Return the directory holding the conf.py Sphinx should read.

    Args:
        config: The build configuration naming the documentation source.

    Returns:
        The source directory when the project has its own conf.py, otherwise the
        package directory holding the built-in one.
    """
    if (config.source_dir / "conf.py").exists():
        return config.source_dir
    return Path(__file__).parent


def get_verbosity_flags(verbosity: str) -> list[str]:
    """Convert verbosity level to Sphinx command-line flags.

    Args:
        verbosity: Verbosity level (full, quiet, errors-only)

    Returns:
        List of Sphinx flags for the verbosity level
    """
    if verbosity == "quiet":
        return ["-q"]
    elif verbosity == "errors-only":
        return ["-Q"]
    else:
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
    """Build Sphinx documentation with sensible defaults.

    Reads configuration from [tool.fairdm.docs] in pyproject.toml.
    Falls back to convention-based defaults if not configured.
    """
    try:
        config = load_config()

        conf_dir = _conf_dir(config)

        if live:
            if not is_port_available(config.port):
                typer.echo(
                    ERROR_MESSAGES["port_conflict"](config.port),
                    err=True,
                )
                raise typer.Exit(code=1)

            typer.echo(
                f"🔄 Starting live preview server on http://localhost:{config.port}"
            )
            typer.echo("   Press Ctrl+C to stop the server\n")

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

            verbosity_flags = get_verbosity_flags(config.verbosity)
            if verbosity_flags:
                sphinx_autobuild_args.extend(verbosity_flags)

            try:
                # Output is not captured, so the developer sees the server's own log.
                with _build_settings(config):
                    process = subprocess.run(sphinx_autobuild_args, check=False)  # noqa: S603 - argv is built from sys.executable and validated build settings

                if process.returncode != 0:
                    typer.echo(
                        f"\n❌ Live server exited with code {process.returncode}\n"
                        f"   Check the output above for error details.",
                        err=True,
                    )

                raise typer.Exit(code=process.returncode)
            except KeyboardInterrupt:
                typer.echo("\n⚠️  Server stopped by user")
                raise typer.Exit(code=130) from None
            except FileNotFoundError:
                typer.echo(
                    "❌ Error: sphinx-autobuild not found.\n   Install with: pip install sphinx-autobuild",
                    err=True,
                )
                raise typer.Exit(code=1) from None

        typer.echo("📚 Building documentation...")

        # Imported late so a missing Sphinx gets a message, not a traceback.
        try:
            from sphinx.cmd.build import main as sphinx_build
        except ImportError:
            typer.echo(
                "❌ Error: Sphinx not found. Install with: pip install sphinx", err=True
            )
            raise typer.Exit(code=1) from None

        verbosity_flags = get_verbosity_flags(config.verbosity)
        config.build_dir.parent.mkdir(parents=True, exist_ok=True)

        sphinx_args = [
            "-b",
            "html",
            "-c",
            str(conf_dir),
            *verbosity_flags,
            str(config.source_dir),
            str(config.build_dir),
        ]

        with _build_settings(config):
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
    """Validate documentation for quality issues.

    Currently checks:
    - Broken external links (linkcheck)

    Exits with code 0 if validation passes, code 1 if errors found.
    """
    try:
        config = load_config()

        conf_dir = _conf_dir(config)

        typer.echo("🔍 Checking documentation for broken links...")

        try:
            from sphinx.cmd.build import main as sphinx_build
        except ImportError:
            typer.echo(
                "❌ Error: Sphinx not found. Install with: pip install sphinx", err=True
            )
            raise typer.Exit(code=1) from None

        linkcheck_dir = config.build_dir.parent / "linkcheck"
        linkcheck_dir.mkdir(parents=True, exist_ok=True)

        verbosity_flags = get_verbosity_flags(config.verbosity)

        sphinx_args = [
            "-b",
            "linkcheck",
            "-c",
            str(conf_dir),
            *verbosity_flags,
            str(config.source_dir),
            str(linkcheck_dir),
        ]

        with _build_settings(config):
            exit_code = sphinx_build(sphinx_args)

        output_file = linkcheck_dir / "output.txt"

        if output_file.exists():
            broken_links = []
            redirected_links = []
            with open(output_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    # The redirect text varies by status code ("redirected permanently",
                    # "redirected with Found", ...), so match the common prefix (#21).
                    if ": [broken]" in line:
                        broken_links.append(line)
                    elif ": [redirected " in line:
                        redirected_links.append(line)

            # Written beside the HTML output, not inside it, like linkcheck_dir.
            report_file = config.build_dir.parent / "check-report.txt"
            report_lines = []
            if broken_links:
                report_lines.append(f"Broken links ({len(broken_links)}):")
                report_lines.extend(f"  {link}" for link in broken_links)
            if redirected_links:
                if report_lines:
                    report_lines.append("")
                report_lines.append(f"Redirected links ({len(redirected_links)}):")
                report_lines.extend(f"  {link}" for link in redirected_links)
            if not report_lines:
                report_lines.append("All links are valid.")
            report_file.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

            if redirected_links:
                # Redirects never affect the exit code (FS-002 FR-013).
                typer.echo(f"\n⚠️  Found {len(redirected_links)} redirect(s):\n")
                for link in redirected_links:
                    typer.echo(f"   {link}")
                typer.echo("")

            if broken_links:
                typer.echo(
                    f"\n❌ Found {len(broken_links)} broken link(s):\n", err=True
                )
                for link in broken_links:
                    typer.echo(f"   {link}", err=True)
                typer.echo("", err=True)
                raise typer.Exit(code=1)
            else:
                typer.echo("✅ All links are valid!")
                raise typer.Exit(code=0)
        else:
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
