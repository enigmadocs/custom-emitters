import parsekit
import flatdict
import json

from parsekit.steps.extract.formats.util import Emitter

class CreateRecords(Emitter):

    numrecords = parsekit.Argument(
        "Number of records",
        type=int,
        required=True)

    def emit_records(self, source):
        for i in range (0, self.options.numrecords):
            record = [i, i + 1, i + 2]
            self.metadata['recordnum'] = i
            yield record

class jsonReadRecords(Emitter):

    _accepts_iterable = True
    _accepts_raw_data = True

    source = parsekit.Argument(
        "Input data source",
        type=basestring,
        required=True)

    def emit_records(self, source):
        json_data = source.read()
        values = json.loads(json_data)
        for i, val in enumerate(values.get(self.options.source)):
            flat = flatdict.FlatDict(val)
            if i == 0:
                self.log.info("|".join(sorted(flat.keys())))
            record = [v for (k, v) in sorted(flat.items())]
            yield record

class csvReadRecords(Emitter):

    _accepts_iterable = True
    _accepts_raw_data = True

    # Custom options:
    content_encoding = parsekit.Argument(
        "The source data character encoding. See the `Python codecs "
        "module "
        "<https://docs.python.org/2/library/codecs.html#standard-encodings>`"
        "__ for supported encodings (defaults to **ascii**).",
        type=basestring,
        default='ascii')

    def _construct_format(self):
        """Derive formatting parameters from steps arguments."""
        # Map steps options to standard library args.
        pk_to_std_lib = {
            'delimiter': 'delimiter', 'double_quote': 'doublequote',
            'escape_character': 'escapechar', 'quote_character': 'quotechar',
            'skip_initial_space': 'skipinitialspace', 'strict': 'strict'}
        fmt_params = {std_lib: self.options[pk]
                      for pk, std_lib in pk_to_std_lib.iteritems()}
        fmt_params['quoting'] = self._quote_constant(self.options.quoting)
        return fmt_params

    def emit_records(self, source):
        # return UnicodeReader(source, encoding=self.options.content_encoding,
        #                      **self._construct_format())
        return UnicodeReader(source, encoding=self.options.content_encoding,
                             **self._construct_format())

class UnicodeReader(object):
    """
    A CSV reader that iterates over lines in the CSV file 'fh', which is
    encoded in the given encoding.
    """

    def __init__(self, fh, encoding, **kwargs):
        fh = UTF8Recoder(fh, encoding)
        self.reader = csv.reader(fh, **kwargs)

    def __iter__(self):
        return self

    def next(self):
        row = self.reader.next()
        return [unicode(s, 'utf-8') for s in row]

