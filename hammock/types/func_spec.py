from __future__ import absolute_import
import inspect
import six
import re
import hammock.types.args as args


PARAM_IS_SPECIAL = re.compile(r'^[ ]*:(param|return)')
PARAM_RE = re.compile(r'^[ ]*:param([ ]+(?P<type>\w+))?[ ]+(?P<name>\w+):[ ]+(?P<doc>.*)$', re.MULTILINE)
RETURN_RE = re.compile(r'^[ ]*:return([ ]+(?P<type>\w+))?:[ ]+(?P<doc>.*)$', re.MULTILINE)


class FuncSpec(object):

    def __init__(self, func):
        self._func = func
        self.args = []
        self.kwargs = {}
        self.keywords = None
        self._inspect(func)
        self.doc, self._args_info, self.returns = self._get_doc_parts(func.__doc__)

    def args_info(self, arg):
        info = self._args_info.get(arg)
        if not info:
            if arg in self.args:
                info = args.Arg(arg, None, None)
            elif arg in self.kwargs:
                info = args.DefaultArg(arg, None, None, self.kwargs[arg])
            elif arg == self.keywords:
                info = args.KeywordsArg(self.keywords)
            else:
                raise AttributeError('No such argument {} in method {}'.format(arg, self._func.__name__))
        return info

    def _inspect(self, func):
        if six.PY2:
            spec = inspect.getargspec(func)  # pylint: disable=deprecated-method
            defaults = spec.defaults or []
            spec_args = spec.args[:]
            if spec_args[0] == 'self':
                spec_args = spec_args[1:]
            self.args = spec_args[:len(spec_args) - len(defaults)]
            keywords = spec_args[len(spec_args) - len(defaults):]
            self.kwargs = dict(six.moves.zip(keywords, defaults))
            self.keywords = spec.keywords
        elif six.PY3:
            # pylint: disable=no-member
            parameters = inspect.signature(func).parameters
            for param in parameters.values():
                if param.name == 'self':
                    continue
                if param.kind == inspect.Parameter.VAR_KEYWORD:
                    self.keywords = param.name
                elif param.default == inspect.Signature.empty:
                    self.args.append(param.name)
                else:
                    self.kwargs[param.name] = param.default

    def _get_doc_parts(self, doc):
        intro = []
        args_info = {}
        returns = None
        if doc:
            # get func doc
            for line in doc.split('\n'):
                if not PARAM_IS_SPECIAL.match(line):
                    intro.append(line.strip())
                else:
                    break
            intro = '\n'.join(intro).strip()

            # get params
            doc = self._doc_mask_endlines(doc)
            doc = doc.replace('\\n:param', '\n:param').replace('\\n:return', '\n:return')
            for arg_info in PARAM_RE.finditer(doc):
                if arg_info:
                    arg = self._get_arg(arg_info)
                    args_info[arg.name] = arg

            # get return
            for returns in RETURN_RE.finditer(doc):
                returns = self._get_arg(returns)
                break

        return intro, args_info, returns

    @staticmethod
    def _doc_mask_endlines(doc):
        return '\\n'.join((line.strip() for line in doc.split('\n')))

    @staticmethod
    def _doc_return_endlines(doc):
        return doc.replace('\\n', '\n').strip()

    def _get_arg(self, match):
        arg = match.groupdict()
        doc = self._doc_return_endlines(arg['doc'])
        if 'name' not in arg:
            return args.ReturnArg(arg['type'], doc)
        if arg['name'] in self.args:
            return args.Arg(arg['name'], arg['type'], doc)
        elif arg['name'] in self.kwargs:
            return args.DefaultArg(arg['name'], arg['type'], doc, default=self.kwargs[arg['name']])
        elif arg['name'] == self.keywords:
            return args.KeywordsArg(arg['name'], doc)
