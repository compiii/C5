"""
SQL compiler and interpreter
"""

try:
    importScripts('node_modules/alasql/dist/alasql.js') # pylint: disable=undefined-variable
except NameError:
    pass # Called from Makefile

class Session(Compile): # pylint: disable=undefined-variable,invalid-name
    """SQL compiler and evaluator"""
    execution_result = ''
    execution_returns = None
    default_options = {
        'language': 'SQL',
        'extension': 'sql',
        'sql_result_format': 'html',
    }

    def pad_right(self, value, width):
        """Pad without str.ljust, which RapydScript does not provide."""
        value = str(value)
        while len(value) < width:
            value += ' '
        return value

    def text_table(self, result):
        """Render rows like the text output of a command-line SQL client."""
        columns = []
        for row in result:
            for key in row:
                if key not in columns:
                    columns.append(key)
        widths = []
        for key in columns:
            width = len(str(key))
            for row in result:
                serialized = JSON.stringify(row[key])
                if serialized:
                    value = str(row[key])
                else:
                    value = 'NULL'
                width = max(width, len(value))
            widths.append(width)
        separator = '+'
        for width in widths:
            for _unused in range(width + 2):
                separator += '-'
            separator += '+'
        lines = [separator]
        header = '|'
        for index, key in enumerate(columns):
            header += ' ' + self.pad_right(key, widths[index]) + ' |'
        lines.append(header)
        lines.append(separator)
        for row in result:
            line = '|'
            for index, key in enumerate(columns):
                serialized = JSON.stringify(row[key])
                if serialized:
                    value = str(row[key])
                else:
                    value = 'NULL'
                line += ' ' + self.pad_right(value, widths[index]) + ' |'
            lines.append(line)
        lines.append(separator)
        lines.append(str(len(result)) + ' rows in set')
        return '\n'.join(lines)

    def run_compiler(self, source):
        """Compile, display errors and return the executable"""
        try:
            meaningful_source = source.replace(RegExp('--[^\\n]*', 'g'), '').strip()
            if not meaningful_source:
                self.post('compiler', 'Saisissez une requete SQL avant de lancer l’analyse.')
                return None
            database = self.quest.sql_database()
            if database:
                eval('alasql(' + JSON.stringify(database) + ')')
            source = self.quest.normalize_sql(source)
            # pylint: disable=eval-used
            executable = eval('alasql(' + JSON.stringify(source) + ')')
            # AlaSQL returns rows directly for one SELECT, but one item per
            # statement when the source contains several statements. Keep the
            # executor contract stable by always exposing a list of results.
            if not Array.isArray(executable):
                executable = [executable]
            elif (len(executable) == 0
                  or (not Array.isArray(executable[0])
                      and isNaN(executable[0]))):
                executable = [executable]
            self.post('compiler', 'Compilation sans erreur')
            return executable
        except Error as err: # pylint: disable=undefined-variable
            try:
                line = err.message.split('Parse error on line ')
                if len(line) > 1:
                    self.post('error', [int(line[1].split(':')[0]), 1])
                self.post(
                    'compiler',
                    '<error>'
                    + self.escape(err.name) + '\n' + self.escape(err.message)
                    + '</error>')
                return None
            except: # pylint: disable=bare-except
                return None
    def run_executor(self):
        """Execute the compiled code"""
        try:
            content = []
            for result in self.executable:
                if isNaN(result):
                    if self.options['sql_result_format'] == 'text':
                        content.append(self.text_table(result) + '\n')
                        continue
                    # The generic executor replaces the first literal space in
                    # its payload with a non-breaking one. A newline keeps the
                    # HTML attribute separator valid after that transformation.
                    content.append('<table\nborder>\n')
                    columns = {}
                    for line in result:
                        for key in line:
                            columns[key] = 1
                    content.append('<tr>')
                    for key in columns:
                        content.append('<th>' + html(key) + '</th>')
                    content.append('</tr>')
                    for line in result:
                        content.append('<tr>')
                        for key in columns:
                            serialized = JSON.stringify(line[key])
                            if serialized:
                                value = html(str(line[key]))
                            else:
                                value = '<i>NULL</i>'
                            content.append('<td>' + value + '</td>')
                        content.append('</tr>\n')
                    content.append('</table>\n')
                else:
                    content.append('Command return value: ' + html(str(result)) + '\n')
            if self.options['sql_result_format'] == 'text':
                self.execution_returns = ('<pre class="executor_output">'
                    + html(''.join(content)) + '</pre>')
            else:
                self.execution_returns = ('<div class="executor_output">'
                    + ''.join(content) + '</div>')
            self.post('executor', self.execution_returns)
        except Error as err: # pylint: disable=undefined-variable
            try:
                self.post(
                    'executor', '<error>'
                    + self.escape(err.name) + '\n'
                    + self.escape(err.message) + '</error>')
            except: # pylint: disable=bare-except
                self.post('executor', '<error>BUG</error>')
