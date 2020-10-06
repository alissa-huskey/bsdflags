"""click subclasses"""

from collections import defaultdict

import click


__all__ = ["Group", "Command"]


class Command(click.Command):
    """Return list of usage strings"""
    def collect_usage_pieces(self, ctx):
        self.options_metavar = self.make_options_metavar()
        for param in self.get_params(ctx):
            # param.make_metavar = Param.make_metavar
            param.metavar = self.make_metavar(param)
        return super(Command, self).collect_usage_pieces(ctx)

    def command_path(self, ctx):
        cmd = ctx.command_path
        if not self.name in cmd:
            cmd += f" {self.name}"
        if self.is_default:
            cmd = cmd.replace(self.name, f"[{self.name}]")
        return cmd

    def format_usage(self, ctx, formatter, output=True):
        """Writes the usage line into the formatter.  This is a low-level
          method called by :meth:`get_usage`.  """
        pieces = self.collect_usage_pieces(ctx)
        cmd = self.command_path(ctx)
        args = " ".join(pieces)
        # hack to handle blank args (the formatter prints nothing if args are blank)
        if not args: args = "\033[0m"
        if output:
            formatter.write_usage(cmd, args)
        return cmd, pieces

    def options(self):
        """Return a dict of name: list[options]"""
        options = defaultdict(list)
        for o in (p for p in self.params if type(p).__name__ == "Option"):
            options[o.name].append(o)
        return options

    def make_options_metavar(self):
        meta = []
        for _, options in self.options().items():
            m = "|".join([o.opts[0] for o in options])
            if not options[0].required:
                m = f"[{m}]"
            meta.append(m)

        return " ".join(meta)

    def make_metavar(self, param):
        if param.metavar: return param.metavar
        meta = f"<{param.name}>"

        if param.nargs != 1:
            meta += "..."

        if not param.required:
            meta = f"[{meta}]"

        return meta


class Group(click.Group):
    """click.Group with default commands and command aliases"""

    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.aliases = {}

    def format_usage(self, ctx, formatter):
        lines = (cmd.get_usage(ctx) for cmd in self.commands.values())
        for i, line in enumerate(lines):
            if i > 0:
                line = line.replace("Usage:", "      ")
            print(line)
        print()

    def format_commands(self, ctx, formatter):
      """format command list for help"""
      commands = []
      for subcommand in self.list_commands(ctx):
          cmd = self.get_command(ctx, subcommand)
          # What is this, the tool lied about a command.  Ignore it
          if cmd is None:
              continue
          if cmd.hidden:
              continue

          commands.append((cmd.help_name, cmd))

      # allow for 3 times the default spacing
      if len(commands):
          limit = formatter.width - 6 - max(len(cmd[0]) for cmd in commands)

          rows = []
          for subcommand, cmd in commands:
              help = cmd.get_short_help_str(limit)
              rows.append((subcommand, help))

          if rows:
              with formatter.section("Commands"):
                  formatter.write_dl(rows)

    def command(self, *args, **kwargs):
        """Create a new `Command` and use the decorated function as callback
           with added support for aliases and default commands

        :param name: the name of the command.
             default=function name with underscores replaced by dashes
        :param cls: the command class to instantiate.
            default=:class:`Command`.
        :param default: (bool) is this the default command
            default=False
        """
        def decorator(func):
            is_default = kwargs.pop('default', False)
            aliases = kwargs.pop("aliases", [])

            cmd = super(Group, self).command(*args, cls=Command, **kwargs)(func)
            cmd.is_default = is_default
            cmd.aliases = aliases
            cmd.help_name = f"[{cmd.name}]" if cmd.is_default else cmd.name

            if cmd.is_default:
              self.default_command = cmd.name

            self.aliases[cmd.name] = cmd
            for name in aliases:
              self.aliases[name] = cmd

            return cmd

        return decorator

    def get_command(self, ctx, name):
      """Return the command with name or alias matching name"""
      return self.aliases.get(name)

    def resolve_command(self, ctx, args):
      """Resolve command with fallback to default_command"""
      try:
          # test if the command parses
          return super(
              Group, self).resolve_command(ctx, args)
      except click.UsageError:
          # command did not parse, assume it is the default command
          args.insert(0, self.default_command)
          return super(
              Group, self).resolve_command(ctx, args)
