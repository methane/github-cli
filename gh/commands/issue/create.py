from gh.base import Command
from gh.util import mktmpfile, rmtmpfile


class CreateIssueCommand(Command):
    name = 'create.issue'
    usage = '%prog [options] create.issue [options]'
    summary = 'Create an issue on the specified repository'
    subcommands = {}

    def __init__(self):
        super(CreateIssueCommand, self).__init__()
        add = self.parser.add_option
        add('-t', '--title',
            dest='title',
            help='Title for a new issue',
            type='str',
            default='',
            nargs=1,
            )

    def run(self, options, args):
        self.get_repo(options)
        opts, args = self.parser.parse_args(args)

        if opts.help:
            parser.print_help()
            return self.SUCCESS

        if not opts.title:
            parser.error('create.issue requires a title')
            parser.print_help()
            return self.FAILURE

        self.login()

        # I need to handle this on Windows too somehow
        if not expandvars('$EDITOR'):
            print("$EDITOR not set")
            return self.FAILURE

        status = self.SUCCESS
        with mktmpfile('gh-newissue-') as fd:
            name = fd.name
            system('$EDITOR {0}'.format(fd.name))

        issue = self.repo.create_issue(opts.title, open(name).read())

        if not issue:
            status = self.FAILURE
            print("Issue file is at saved at {0}".format(name))
        else:
            print("#{0.number} {0.html_url}".format(issue))
            rmtmpfile(name)

        return status


CreateIssueCommand()
