from gh.base import Command, CustomOptionParser
from gh.util import tc, wrap, trim_numbers, sep
from gh.compat import fix_encoding
from github3 import GitHubError
from os import system
from os.path import expandvars


class IssueLsCommand(Command):
    name = 'issues.ls'
    usage = ('%prog [options] issues.ls [options]')
    summary = 'Interact with the Issues API'
    short_fs = ('#{0.number} {bold}{0.title}{default} - @{0.user}')
    subcommands = {
        '[#]num comments': 'Print all the comments on this issue',
        '[#]num close': 'Close this issue',
        '[#]num reopen': 'Reopen this issue',
        '[#]num assign <assignee>': 'Assign this issue to @<assignee>',
        '[#]num comment': 'Comment on this issue using $EDITOR',
    }

    def __init__(self):
        super(IssuesCommand, self).__init__()
        self.parser.add_option('-d', '--direction',
                               dest='direction',
                               help='How to list issues on a repository',
                               choices=('asc', 'desc'),
                               nargs=1,
                               )
        self.parser.add_option('-s', '--state',
                               dest='state',
                               help='State of issues to list',
                               choices=('open', 'closed'),
                               default='open',
                               nargs=1
                               )
        self.parser.add_option('-m', '--milestone',
                               dest='milestone',
                               help='Milestone to list issues on',
                               type='int',
                               nargs=1,
                               )
        self.parser.add_option('-M', '--mentioned',
                               dest='mentioned',
                               help='List issues mentioning specified user',
                               type='str',
                               nargs=1,
                               )
        self.parser.add_option('-n', '--number',
                               dest='number',
                               help='Number of issues to list at most',
                               type='int',
                               nargs=1,
                               default=-1,
                               )

    def run(self, options, args):
        self.get_repo(options)

        opts, args = self.parser.parse_args(args)

        if opts.help:
            self.help()

        return self.print_issues(opts)

    # Formatting and printing
    def format_comment(self, comment):
        fs = '@{uline}{u.login}{default} -- {date}\n{body}\n'
        body = wrap(comment.body_text)
        date = comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
        return fs.format(u=comment.user, uline=tc['underline'],
                         default=tc['default'], date=date, body=body)

    def format_short_issue(self, issue):
        extra = []

        if issue.milestone:
            extra.append(issue.milestone.title)

        if issue.assignee:
            extra.append(issue.assignee.login)

        if extra:
            extra = ' (' + ' -- '.join(extra) + ')'
        else:
            extra = ''

        issue.title = fix_encoding(issue.title)

        return (self.fs.format(issue, bold=tc['bold'], default=tc['default'])
                + extra)

    def print_comments(self, number, opts):
        issue = self.repo.issue(number)

        if not issue:
            return self.FAILURE

        for c in issue.iter_comments(opts.number):
            print(self.format_comment(c))

        return self.SUCCESS

    def print_issues(self, opts):
        status = self.SUCCESS
        issues = self.repo.iter_issues(opts.milestone, opts.state,
                                       direction=opts.direction,
                                       mentioned=opts.mentioned,
                                       number=opts.number)
        try:
            for i in issues:
                print(self.format_short_issue(i))
        except GitHubError as ghe:
            if ghe.code == 410:
                print(ghe.message)
                status = self.FAILURE
            else:
                raise ghe

        return status

    # Administration/interaction
    def _get_authenticated_issue(self, number):
        self.login()
        user, repo = self.repository
        return self.gh.issue(user, repo, number)

    def comment_on(self, number):
        issue = self._get_authenticated_issue(number)
        name = ''
        status = self.SUCCESS

        # I need to handle this on Windows too somehow
        if not expandvars('$EDITOR'):
            print("$EDITOR not set")
            return self.FAILURE

        with mktmpfile('gh-issuecomment-') as fd:
            name = fd.name
            system('$EDITOR {0}'.format(fd.name))

        if not issue.create_comment(open(name).read()):
            status = self.FAILURE

        rmtmpfile(name)
        return status

    def close_issue(self, number):
        issue = self._get_authenticated_issue(number)

        if not issue:
            return self.FAILURE
        issue.close()

        return self.SUCCESS

    def reopen_issue(self, number):
        issue = self._get_authenticated_issue(number)

        if not issue:
            return self.FAILURE
        issue.reopen()

        return self.SUCCESS

    def assign(self, number, assignee):
        issue = self._get_authenticated_issue(number)

        if not issue:
            return self.FAILURE
        issue.assign(assignee)

        return self.SUCCESS

# Ensures this ends up in gh.base.commands
IssueLsCommand()
