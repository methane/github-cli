import os
from gh.base import Command
from gh.util import read_stdin


class GistCreateCommand(Command):
    name = 'gist.create'
    usage = '%prog [options] gist.create [options] file1 file2'
    summary = 'Create a new gist'
    subcommands = {}

    def __init__(self):
        super(GistCreateCommand, self).__init__()
        add = self.parser.add_option
        add('-p', '--private',
            dest='private',
            help='Make this gist private',
            default=False,
            action='store_true',
            )
        add('-d', '--description',
            dest='description',
            help='Description of the gist',
            type='str',
            default='',
            nargs=1,
            )
        add('-a', '--anonymous',
            dest='anonymous',
            help='Create anonymously',
            default=False,
            action='store_true',
            )
        self.parser.epilog = ('create.gist will accept stdin if you use `-`'
                              ' to indicate that is your intention')

    def run(self, options, args):
        opts, args = self.parser.parse_args(args)

        if opts.help:
            self.help()

        if not opts.anonymous:
            self.login()
        else:
            opts.private = False

        status = self.COMMAND_UNKNOWN

        if not args:
            self.parser.print_help()
            return self.FAILURE

        status = self.FAILURE
        files = {}

        if '-' == args[0]:
            files['stdin'] = read_stdin()
        else:
            for f in args:
                base = os.path.basename(f)
                files[base] = {'content': open(f, 'rb').read()}

        # Create the gist
        g = self.gh.create_gist(opts.description, files, not opts.private)

        if g:
            print('{0.id} -- {0.html_url}'.format(g))
            status = self.SUCCESS

        return status


GistCreateCommand()
