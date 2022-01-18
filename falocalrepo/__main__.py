from pathlib import Path
from signal import SIGINT
from sys import exit
from sys import stderr
from traceback import print_exc

from click import BadParameter
from click import ClickException
from click import UsageError
from click import echo
from click import secho
from click.exceptions import Abort
from click.exceptions import Exit
from falocalrepo_database.exceptions import MultipleConnections

from .console import app


def _activate_pretty_errors():
    import pretty_errors
    from pretty_errors import default_config
    from pretty_errors import FILENAME_EXTENDED
    from pretty_errors import MAGENTA
    from pretty_errors import RED

    pretty_errors.configure(
        filename_display=FILENAME_EXTENDED,
        line_number_first=True,
        lines_before=5,
        lines_after=2,
        line_color=RED + '> ' + default_config.line_color,
        code_color='  ' + default_config.line_color,
        truncate_code=True,
        inner_exception_separator=True,
        inner_exception_message=MAGENTA + "\n  During handling of the above exception, another exception occurred:\n",
        display_locals=True
    )

    if not pretty_errors.terminal_is_interactive:
        pretty_errors.mono()


def main():
    try:
        exit(app.main(standalone_mode=False) or 0)
    except SystemExit:
        raise
    except Exit as err:
        exit(err.exit_code)
    except (KeyboardInterrupt, Abort):
        print()
        exit(128 + SIGINT)
    except MultipleConnections as err:
        secho(f"Error: {' '.join(err.args)}", fg="red", bold=True, file=stderr)
        exit(BadParameter.exit_code)
    except UsageError as err:
        secho(f"Error: {err.format_message()}", fg="red", bold=True, file=stderr,
              color=None if err.ctx is None else err.ctx.color)
        if err.ctx is not None:
            echo("\n" + err.ctx.command.get_usage(err.ctx), file=stderr, color=err.ctx.color)
        exit(err.exit_code)
    except ClickException as err:
        secho("Error: " + err.format_message(), fg="red", bold=True, file=stderr)
        exit(err.exit_code)
    except BaseException:
        echo()
        with Path.cwd().joinpath("FA.log").open("w") as f:
            print_exc(file=f)
            secho(f"Trace written to {f.name}", fg="red", bold=True, file=stderr)
        _activate_pretty_errors()
        raise


if __name__ == "__main__":
    main()
