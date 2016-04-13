import os
import sys
import pprint
import argparse

from pytan import PytanError
from pytan.handler import Handler
from pytan.handler_args import prompt_for_args
from pytan.handler_logs import print_pytan_loglevels
from pytan.version import __version__
from pytan.shellparser import ShellParser, add_arg_group
from pytan.historyconsole import HistoryConsole

from pytan.constants import SHELL_OPTS, HANDLER_DEFAULTS
from pytan.pollers.constants import Q_COMPLETE_PCT, Q_POLLING_SECS


class VersionMismatchError(PytanError):
    pass


class LogLevelPrinter(argparse.Action):

    def __init__(self,
                 option_strings,
                 dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS,
                 help=None):
        super(LogLevelPrinter, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        print_pytan_loglevels()
        parser.exit()


class Base(object):

    DESCRIPTION = ""
    INTERACTIVE = False

    def __init__(self, **kwargs):
        self.Handler = Handler
        self.HistoryConsole = HistoryConsole
        self.SUPPRESS = argparse.SUPPRESS
        self.pf = pprint.pformat

        self.kwargs = kwargs
        self.my_filepath = os.path.abspath(sys.argv[0])
        self.my_file = os.path.basename(self.my_filepath)
        self.my_name = os.path.splitext(self.my_file)[0]
        self.pre_init()
        self.set_base()
        self.set_parser()
        self.post_init()

    def pre_init(self):
        pass

    def post_init(self):
        pass

    def set_base(self):
        self.base = ShellParser(
            my_file=self.my_file,
            description=self.DESCRIPTION,
            add_help=False,
        )
        for k, v in SHELL_OPTS.items():
            add_arg_group(self.base, k, v, HANDLER_DEFAULTS)

    def set_parser(self):
        self.parser = ShellParser(
            my_file=self.my_file,
            description=self.DESCRIPTION,
            parents=[self.base],
            add_help=False,
        )
        self.parser.add_argument('--version', action='version', version=__version__)
        self.parser.add_argument('--help', action='help')
        self.parser.add_argument('--print_loglevels', action=LogLevelPrinter)

    def add_help_opts(self):
        name = 'PyTan Help Options'
        self.grp = self.parser.add_argument_group(name)
        self.grp.add_argument(
            '--sensors-help',
            required=False, action='store_true', default=False, dest='sensors_help',
            help='Get the full help for sensor strings and exit',
        )
        self.grp.add_argument(
            '--filters-help',
            required=False, action='store_true', default=False, dest='filters_help',
            help='Get the full help for filter strings and exit',
        )
        self.grp.add_argument(
            '--options-help',
            required=False, action='store_true', default=False, dest='options_help',
            help='Get the full help for option strings and exit',
        )
        self.grp.add_argument(
            '--package-help',
            required=False, action='store_true', default=False, dest='package_help',
            help='Get the full help for package strings and exit',
        )

    def add_report_opts(self):
        name = 'Report File Options'
        self.grp = self.parser.add_argument_group(name)
        self.grp.add_argument(
            '--file',
            required=False, action='store', default=self.SUPPRESS, dest='report_file',
            help='File to save report to (if not supplied, will be generated)',
        )
        self.grp.add_argument(
            '--dir',
            required=False, action='store', default=self.SUPPRESS, dest='report_dir',
            help='Directory to save report to (if not supplied, use current directory)',
        )

    def grp_choice_results(self):
        choice = self.grp.add_mutually_exclusive_group()
        choice.add_argument(
            '--no-results',
            action='store_false', dest='get_results', default=self.SUPPRESS, required=False,
            help='Do not get the results, just add the object and return right away'
        )
        choice.add_argument(
            '--results',
            action='store_true', dest='get_results', default=self.SUPPRESS, required=False,
            help='Wait until all results are in before returning (default)'
        )

    def grp_choice_sse(self):
        choice = self.grp.add_mutually_exclusive_group()
        choice.add_argument(
            '--enable_sse',
            required=False, action='store_true', dest='sse', default=True,
            help='Perform a server side export when getting data'
        )
        choice.add_argument(
            '--disable_sse',
            required=False, action='store_false', dest='sse', default=True,
            help='Perform a normal get result data export when getting data'
        )

    def grp_sse_opts(self):
        self.grp.add_argument(
            '--sse_format',
            required=False, action='store', default='xml_obj', dest='sse_format',
            choices=['csv', 'xml', 'xml_obj', 'cef'],
            help='If sse = True, perform server side export in this format',
        )
        self.grp.add_argument(
            '--leading',
            required=False, action='store', default='', dest='leading',
            help='If sse = True, and sse_format = "cef", prepend each row with this text',
        )
        self.grp.add_argument(
            '--trailing',
            required=False, action='store', default='', dest='trailing',
            help='If sse = True, and sse_format = "cef", append each row with this text',
        )

    def grp_format(self):
        self.grp.add_argument(
            '--export_format',
            required=False, action='store', default='csv', dest='export_format',
            choices=['csv', 'xml', 'json'],
            help='Export Format to create report file in, only used if sse = False',
        )

    def grp_choice_csv_sort(self):
        choice = self.grp.add_mutually_exclusive_group()
        choice.add_argument(
            '--sort',
            required=False, action='append', default=[], dest='header_sort',
            help='For export_format: csv, Sort headers by given names'
        )
        choice.add_argument(
            '--no-sort',
            required=False, action='store_false', default=self.SUPPRESS, dest='header_sort',
            help='For export_format: csv, Do not sort the headers at all'
        )
        choice.add_argument(
            '--auto_sort',
            required=False, action='store_true', default=self.SUPPRESS, dest='header_sort',
            help='For export_format: csv, Sort the headers with a basic alphanumeric sort'
        )

    def grp_choice_csv_sensor(self):
        choice = self.grp.add_mutually_exclusive_group()
        choice.add_argument(
            '--add-sensor',
            required=False, action='store_true', default=self.SUPPRESS,
            dest='header_add_sensor',
            help='For export_format: csv, Add the sensor names to each header'
        )
        choice.add_argument(
            '--no-add-sensor',
            required=False, action='store_false', default=False, dest='header_add_sensor',
            help='For export_format: csv, Do not add the sensor names to each header'
        )

    def grp_choice_csv_type(self):
        choice = self.grp.add_mutually_exclusive_group()
        choice.add_argument(
            '--add-type',
            required=False, action='store_true', default=self.SUPPRESS,
            dest='header_add_type',
            help='For export_format: csv, Add the result type to each header'
        )
        choice.add_argument(
            '--no-add-type',
            required=False, action='store_false', default=False, dest='header_add_type',
            help='For export_format: csv, Do not add the result type to each header'
        )

    def grp_choice_csv_expand(self):
        choice = self.grp.add_mutually_exclusive_group()
        choice.add_argument(
            '--expand-columns',
            required=False, action='store_true', default=self.SUPPRESS,
            dest='expand_grouped_columns',
            help='For export_format: csv, Expand multi-line cells into their own rows'
        )
        choice.add_argument(
            '--no-columns',
            required=False, action='store_false', default=False, dest='expand_grouped_columns',
            help='For export_format: csv, Do not add expand multi-line cells into their own rows'
        )

    def grp_choice_explode(self):
        choice = self.grp.add_mutually_exclusive_group()
        choice.add_argument(
            '--no-explode-json',
            required=False, action='store_false', default=False, dest='explode_json_string_values',
            help='Do not explode any embedded JSON into their own columns'
        )
        choice.add_argument(
            '--explode-json',
            required=False, action='store_true', default=self.SUPPRESS,
            dest='explode_json_string_values',
            help='Explode any embedded JSON into their own columns'
        )

    def grp_choice_include_type(self):
        choice = self.grp.add_mutually_exclusive_group()
        choice.add_argument(
            '--no-include_type',
            required=False, action='store_false', default=self.SUPPRESS, dest='include_type',
            help='Only for export_format json, Do not include SOAP type in JSON output'
        )
        choice.add_argument(
            '--include_type',
            required=False, action='store_true', default=True, dest='include_type',
            help='Only for export_format json, Include SOAP type in JSON output'
        )

    def grp_choice_minimal(self):
        choice = self.grp.add_mutually_exclusive_group()
        choice.add_argument(
            '--no-minimal',
            required=False, action='store_false', dest='minimal', default=self.SUPPRESS,
            help='Only for export_format xml, include empty attributes'
        )
        choice.add_argument(
            '--minimal',
            required=False, action='store_true', dest='minimal', default=True,
            help='Only for export_format xml, Only include attributes that are not empty'
        )

    def add_polling_opts(self):
        self.grp = self.parser.add_argument_group('Question Polling Options')
        self.grp.add_argument(
            '--complete_pct',
            required=False, type=float, action='store', dest='complete_pct',
            default=Q_COMPLETE_PCT,
            help='Percent to consider questions complete',
        )
        self.grp.add_argument(
            '--override_timeout_secs',
            required=False, type=int, action='store', default=0, dest='override_timeout_secs',
            help='If supplied and not 0, instead of using the question expiration timestamp as '
            'the timeout, timeout after N seconds',
        )
        self.grp.add_argument(
            '--polling_secs',
            required=False, type=int, action='store', dest='polling_secs',
            default=Q_POLLING_SECS,
            help='Number of seconds to wait in between GetResultInfo loops while polling for '
            'each question',
        )
        self.grp.add_argument(
            '--override_estimated_total',
            required=False, type=int, action='store', dest='override_estimated_total',
            default=0,
            help='If supplied and not 0, use this as the estimated total number of systems '
            'instead of what Tanium Platform reports',
        )
        self.grp.add_argument(
            '--force_passed_done_count',
            required=False, type=int, action='store', dest='force_passed_done_count',
            default=0,
            help='If supplied and not 0, when this number of systems have passed the right '
            'hand side of the question (the question filter), consider the question complete '
            'instead of relying the estimated total that Tanium Platform reports',
        )

    def add_export_results_opts(self):
        name = 'Export Results Options'
        self.grp = self.parser.add_argument_group(name)
        # TODO: figure out SSE (this branches in the doer method, not in export!)
        # self.grp_choice_sse()
        # self.grp_sse_opts()
        self.grp_format()
        self.grp_choice_csv_sort()
        self.grp_choice_csv_sensor()
        self.grp_choice_csv_type()
        self.grp_choice_csv_expand()

    def add_export_object_opts(self):
        name = 'Export Object Options'
        self.grp = self.parser.add_argument_group(name)
        self.grp_format()
        self.grp_choice_csv_sort()
        self.grp_choice_explode()
        self.grp_choice_include_type()
        self.grp_choice_minimal()

    def _get_grp_opts(self, grps):
        action_grps = [a for a in self.parser._action_groups if a.title in grps]
        opts = list(set([a.dest for b in action_grps for a in b._group_actions]))
        return opts

    def version_check(self, version):
        if not __version__ >= version:
            err = "PyTan v{} is not greater than {} v{}"
            err = err.format(version.__version__, self.my_name, version)
            self.mylog.critical(err)
            raise VersionMismatchError(err)
        return True

    def interactive_check(self):
        self.console = None
        if self.INTERACTIVE:
            self.console = self.HistoryConsole()
        return self.console

    def get_parser_args(self, grps):
        parser_opts = self._get_grp_opts(grps=grps)
        p_args = {k: getattr(self.args, k) for k in parser_opts if hasattr(self.args, k)}
        return p_args

    def get_other_args(self, kwargs):
        other_args = {a: b for a, b in self.args.__dict__.items() if a not in kwargs}
        return other_args

    def check(self):
        return

    def setup(self):
        return

    def parse_args(self):
        self.args = self.parser.parse_args()
        return self.args

    def get_handler(self):
        grps = [
            'PyTan Authentication Options',
            'PyTan Connection Options',
            'PyTan Handler Options',
            'PyTan Session Options',
        ]
        argparse_args = self.get_parser_args(grps)
        parsed_handler_args = prompt_for_args(**argparse_args)
        self.handler = self.Handler(parsed_handler_args=parsed_handler_args)
        return self.handler

    def get_result(self):
        return

    def get_exec(self):
        s = 'exec_result = None'
        return s


class GetBase(Base):
    OBJECT_TYPE = ''
    NAME_TEMP = 'Get {} Options'
    DESC_TEMP = 'Get an object of type "{}" and export it to a file'
    ACTION = 'get'

    def pre_init(self):
        self.OBJECT_STR = self.OBJECT_TYPE.replace('_', ' ').capitalize()
        self.GROUP_NAME = self.NAME_TEMP.format(self.OBJECT_STR)
        self.DESCRIPTION = self.DESC_TEMP.format(self.OBJECT_STR)

    '''
    def add_get_opts(self):
        self.grp = self.parser.add_argument_group(self.GROUP_NAME)
        obj_map = self.tanium_obj.get_obj_map(self.OBJECT_TYPE)
        search_keys = copy.copy(obj_map['search'])

        if 'id' not in search_keys:
            search_keys.append('id')

        if self.OBJECT_TYPE == 'whitelisted_url':
            search_keys.append('url_regex')
        elif self.OBJECT_TYPE == 'user':
            search_keys.append('name')

        for k in search_keys:
            self.grp.add_argument(
                '--{}'.format(k),
                required=False, action='append', default=[], dest=k,
                help='{} of {} to {}'.format(k, self.OBJECT_STR, self.ACTION),
            )
    '''

    def setup(self):
        self.add_get_opts()
        self.grp.add_argument(
            '--all',
            required=False, default=False, action='store_true', dest='all',
            help='Get all objects of type {}'.format(self.OBJECT_STR),
        )
        self.add_export_object_opts()
        self.add_report_opts()

    def get_kwargs(self):
        grps = [self.GROUP_NAME]
        kwargs = self.get_parser_args(grps)
        return kwargs

    def get_response(self, kwargs):
        get_all = False
        if 'all' in kwargs:
            get_all = kwargs.pop('all')

        o_dict = {'objtype': self.OBJECT_TYPE}
        kwargs.update(o_dict)

        if get_all:
            m = "-- Getting all {} objects with arguments:\n{}"
            print(m.format(self.OBJECT_STR, self.pf(o_dict)))
            response = self.handler.get_all(**o_dict)
        else:
            m = "-- Getting {} objects with arguments:\n{}"
            print(m.format(self.OBJECT_STR, self.pf(kwargs)))
            response = self.handler.get(**kwargs)

        print("++ Successfully found: {}".format(response))
        return response

    def get_result(self):
        kwargs = self.get_kwargs()
        response = self.get_response(kwargs)
        report_file, result = self.export_results(response)
        return response, report_file, result


class CreateJsonBase(GetBase):
    NAME_TEMP = 'Create {} from JSON Options'
    DESC_TEMP = 'Create an object of type "{}" from a JSON file'

    def add_create_opts(self):
        self.grp = self.parser.add_argument_group(self.GROUP_NAME)
        self.grp.add_argument(
            '-j', '--json',
            required=True, action='store', default='', dest='json_file',
            help='JSON file to use for creating the object',
        )

    def setup(self):
        self.add_create_opts()

    def get_response(self, kwargs):
        o_dict = {'objtype': self.OBJECT_TYPE}
        kwargs.update(o_dict)

        m = "-- Creating {} object from JSON with arguments:\n{}"
        print(m.format(self.OBJECT_TYPE, self.pf(kwargs)))
        response = self.handler.create_from_json(**kwargs)

        for i in response:
            print("++ Successfully created: {}, ID: {}".format(i, getattr(i, 'id', 'unknown')))
        return response

    def get_result(self):
        kwargs = self.get_kwargs()
        response = self.get_response(kwargs)
        return response


class DeleteBase(GetBase):
    NAME_TEMP = 'Delete {} Options'
    DESC_TEMP = 'Delete an object of type "{}"'
    ACTION = 'delete'

    def setup(self):
        self.add_get_opts()

    def get_response(self, kwargs):
        o_dict = {'objtype': self.OBJECT_TYPE}
        kwargs.update(o_dict)

        m = "-- Deleting {} object with arguments:\n{}"
        print(m.format(self.OBJECT_TYPE, self.pf(kwargs)))
        response = self.handler.delete(**kwargs)

        for i in response:
            print("++ Successfully deleted: {}".format(i))
        return response

    def get_result(self):
        kwargs = self.get_kwargs()
        response = self.get_response(kwargs)
        return response


class GetResultsBase(GetBase):
    OBJECT_TYPE = ''
    NAME_TEMP = 'Get {} Results Options'
    DESC_TEMP = 'Get the results of an object of type "{}" and export it to a file'
    ACTION = 'export results'
    FILE_PREFIX = ''

    def setup(self):
        self.add_get_opts()
        self.add_export_object_opts()
        self.add_report_opts()

    def get_result_data(self, obj):
        grps = ['Export Results Options', 'Export Object Options', 'Get Results Options']
        kwargs = self.get_parser_args(grps)
        kwargs['obj'] = obj
        m = "-- Getting result data with arguments:\n{}"
        print(m.format(self.pf(kwargs)))
        result_data = self.handler.get_result_data(**kwargs)
        print("++ Result data received: {}".format(result_data))
        return result_data

    def get_result(self):
        kwargs = self.get_kwargs()
        response = self.get_response(kwargs)
        responses = []
        for r in response:
            d = {'response': r}
            if self.OBJECT_TYPE == 'saved_question':
                r = r.question
            d['resultdata'] = self.get_result_data(r)
            d['report_file'], d['report_result'] = self.export_results(d['resultdata'])
            responses.append(d)

        return responses