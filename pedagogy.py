"""Recursive pedagogical structure with a legacy flat-question projection."""

PEDAGOGY_ID_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-'
RESOURCE_SCOPES = ('question', 'exercise', 'session', 'group')
# The CPython metadata pass overrides this flag. Browser question files must let
# py2js create the ordinary flat Session; the server-provided options then attach
# the richer tree to that worker.
GENERATING_QUESTIONS_JSON = False


def pedagogy_append(items, item):
    """Append in CPython and in generated JavaScript nested scopes."""
    try:
        items.push(item)
    except AttributeError:
        items.append(item)


def validate_pedagogical_id(node_id):
    """Return a stable identifier or raise an author-facing error."""
    if not node_id or len(node_id) > 96:
        raise ValueError('Pedagogical identifiers must contain 1 to 96 characters')
    for character in node_id:
        if character not in PEDAGOGY_ID_CHARS:
            raise ValueError('Invalid pedagogical identifier: ' + node_id)
    return node_id


def validate_points(points):
    """Points are local maxima; totals are computed recursively."""
    if points is None:
        return 0
    # Keep this test executable in both CPython and generated RapydScript.
    # Referencing Python's ``int`` or ``float`` types creates undefined browser
    # globals. Author input is validated strictly by the CPython generation pass.
    if points * 0 != 0 or points < 0:
        raise ValueError('Pedagogical points must be a non-negative number')
    return points


def validate_resource_path(path):
    """Return a safe relative resource path."""
    if not path or path.startswith('/') or '\\' in path or '\x00' in path:
        raise ValueError('Resource paths must be non-empty relative paths')
    for part in path.split('/'):
        if not part or part == '.' or part == '..':
            raise ValueError('Invalid resource path: ' + path)
    return path


class Resource:
    """A file-like input or output attached to a pedagogical question."""

    def __init__(self, resource_id, path=None, name='', resource_type='text',
                 language='', content=None, editable=True, hidden=False,
                 generated=False, required=True, submitted=True,
                 scope='question', actions=None, primary=False):
        self.resource_id = validate_pedagogical_id(resource_id)
        self.path = validate_resource_path(path or resource_id)
        self.name = name or self.path
        self.resource_type = resource_type or 'text'
        self.language = language or ''
        self.content = content
        self.editable = bool(editable)
        self.hidden = bool(hidden)
        self.generated = bool(generated)
        self.required = bool(required)
        self.submitted = bool(submitted)
        if scope not in RESOURCE_SCOPES:
            raise ValueError('Invalid resource scope: ' + scope)
        self.scope = scope
        self.actions = actions or []
        self.primary = bool(primary)


def implicit_source_resource():
    """Compatibility resource backed by default_answer/last_answer/source."""
    # RapydScript 7dfd106 cannot generate keyword arguments on a constructor
    # call (``new Resource(..., path=...)``). Keep this browser-compiled call
    # positional even though CPython accepts the clearer keyword form.
    return Resource('source', 'source', 'Source', 'text', '', None, True,
                    False, False, True, True, 'question', None, True)


def resource_metadata(resource):
    """Return the JSON-safe public contract for one resource."""
    return {
        'id': resource.resource_id,
        'path': resource.path,
        'name': resource.name,
        'type': resource.resource_type,
        'language': resource.language,
        'content': resource.content,
        'editable': resource.editable,
        'read_only': not resource.editable,
        'hidden': resource.hidden,
        'generated': resource.generated,
        'required': resource.required,
        'submitted': resource.submitted,
        'scope': resource.scope,
        'actions': resource.actions,
        'primary': resource.primary,
        'legacy_source': resource.resource_id == 'source' and resource.content is None,
    }


def normalize_resources(resources, implicit_source):
    """Validate resources and select their single primary editor resource."""
    if resources is None:
        if implicit_source:
            resources = [implicit_source_resource()]
        else:
            resources = []
    identifiers = {}
    paths = {}
    primary = None
    normalized = []
    for resource in resources:
        if not isinstance(resource, Resource):
            raise ValueError('Question resources must be Resource instances')
        if resource.resource_id in identifiers:
            raise ValueError('Duplicate resource identifier: ' + resource.resource_id)
        if resource.path in paths:
            raise ValueError('Duplicate resource path: ' + resource.path)
        identifiers[resource.resource_id] = True
        paths[resource.path] = True
        if resource.primary:
            if primary is not None:
                raise ValueError('A question may have only one primary resource')
            primary = resource
        pedagogy_append(normalized, resource)
    if primary is None and normalized:
        normalized[0].primary = True
    return normalized


class PedagogicalNode:
    """A structural node; subclasses define its pedagogical kind."""
    kind = 'section'

    def __init__(self, node_id, title='', children=None, points=None,
                 cumulative_points=False):
        self.node_id = validate_pedagogical_id(node_id)
        self.title = title or ''
        self.children = children or []
        self.has_points = points is not None
        self.points = validate_points(points)
        self.cumulative_points = cumulative_points
        self.question = None
        self.resources = []


class Exercise(PedagogicalNode):
    """Top-level pedagogical unit."""
    kind = 'exercise'

    def __init__(self, node_id, title='', children=None, points=None,
                 cumulative_points=False):
        # RapydScript subclasses do not reliably inherit a Python constructor.
        PedagogicalNode.__init__(self, node_id, title, children, points,
                                 cumulative_points)


class Section(PedagogicalNode):
    """Structural group without its own answer."""
    kind = 'section'

    def __init__(self, node_id, title='', children=None, points=None,
                 cumulative_points=False):
        # Keep the browser and CPython construction paths identical.
        PedagogicalNode.__init__(self, node_id, title, children, points,
                                 cumulative_points)


class QuestionNode(PedagogicalNode):
    """Question context, optionally with its own answer and child questions."""
    kind = 'question'

    def __init__(self, node_id, question=None, title='', children=None, points=None,
                 cumulative_points=False, resources=None):
        PedagogicalNode.__init__(self, node_id, title, children, points,
                                 cumulative_points)
        self.question = question
        self.resources = normalize_resources(resources, question is not None)


def flatten_pedagogy(value):
    """Return (answerable questions, serializable tree metadata)."""
    if isinstance(value, PedagogicalNode):
        roots = [value]
        explicit = True
    else:
        roots = value
        explicit = False
        for item in roots:
            if isinstance(item, PedagogicalNode):
                explicit = True

    questions = []
    identifiers = {}

    def visit(node, ancestors):
        if node in ancestors:
            raise ValueError('Cycle in pedagogical structure at ' + node.node_id)
        if node.node_id in identifiers:
            raise ValueError('Duplicate pedagogical identifier: ' + node.node_id)
        identifiers[node.node_id] = True
        index = None
        if node.question is not None:
            index = len(questions)
            node.question.pedagogical_id = node.node_id
            node.question.pedagogical_title = node.title
            node.question.pedagogical_points = node.points
            node.question.pedagogical_resources = node.resources
            pedagogy_append(questions, node.question)
        children = []
        total = node.points
        for child in node.children:
            if not isinstance(child, PedagogicalNode):
                raise ValueError('Pedagogical children must be nodes')
            child_ancestors = ancestors[:]
            pedagogy_append(child_ancestors, node)
            child_metadata = visit(child, child_ancestors)
            pedagogy_append(children, child_metadata)
            total += child_metadata['total_points']
        display_points = node.points
        if node.cumulative_points or not node.has_points:
            display_points = total
        return {
            'id': node.node_id,
            'kind': node.kind,
            'title': node.title,
            'points': node.points,
            'total_points': total,
            'has_points': node.has_points,
            'cumulative_points': node.cumulative_points,
            'display_points': display_points,
            'answer_index': index,
            'resources': [resource_metadata(resource) for resource in node.resources],
            'children': children,
        }

    metadata_roots = []
    if explicit:
        for root in roots:
            if not isinstance(root, PedagogicalNode):
                raise ValueError('Cannot mix raw questions and pedagogical nodes')
            pedagogy_append(metadata_roots, visit(root, []))
    else:
        for question in roots:
            index = len(questions)
            node_id = 'legacy-question-' + str(index + 1)
            question.pedagogical_id = node_id
            question.pedagogical_title = question.__doc__ or ''
            question.pedagogical_points = 0
            question.pedagogical_resources = normalize_resources(None, True)
            pedagogy_append(questions, question)
            pedagogy_append(metadata_roots, {
                'id': node_id,
                'kind': 'question',
                'title': question.__doc__ or '',
                'points': 0,
                'total_points': 0,
                'has_points': False,
                'cumulative_points': False,
                'display_points': 0,
                'answer_index': index,
                'resources': [resource_metadata(resource)
                              for resource in question.pedagogical_resources],
                'children': [],
            })

    total = 0
    flat_ids = []
    for root in metadata_roots:
        total += root['total_points']
    for question in questions:
        pedagogy_append(flat_ids, question.pedagogical_id)
    return questions, {
        'schema': 2,
        'explicit': explicit,
        'roots': metadata_roots,
        'flat_ids': flat_ids,
        'total_points': total,
    }
