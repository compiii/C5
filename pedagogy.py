"""Recursive pedagogical structure with a legacy flat-question projection."""

PEDAGOGY_ID_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-'


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


class PedagogicalNode:
    """A structural node; subclasses define its pedagogical kind."""
    kind = 'section'

    def __init__(self, node_id, title='', children=None, points=0):
        self.node_id = validate_pedagogical_id(node_id)
        self.title = title or ''
        self.children = children or []
        self.points = validate_points(points)
        self.question = None


class Exercise(PedagogicalNode):
    """Top-level pedagogical unit."""
    kind = 'exercise'

    def __init__(self, node_id, title='', children=None, points=0):
        # RapydScript subclasses do not reliably inherit a Python constructor.
        PedagogicalNode.__init__(self, node_id, title, children, points)


class Section(PedagogicalNode):
    """Structural group without its own answer."""
    kind = 'section'

    def __init__(self, node_id, title='', children=None, points=0):
        # Keep the browser and CPython construction paths identical.
        PedagogicalNode.__init__(self, node_id, title, children, points)


class QuestionNode(PedagogicalNode):
    """Question context, optionally with its own answer and child questions."""
    kind = 'question'

    def __init__(self, node_id, question=None, title='', children=None, points=0):
        PedagogicalNode.__init__(self, node_id, title, children, points)
        self.question = question


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
            questions.append(node.question)
        children = []
        total = node.points
        for child in node.children:
            if not isinstance(child, PedagogicalNode):
                raise ValueError('Pedagogical children must be nodes')
            child_ancestors = ancestors[:]
            child_ancestors.append(node)
            child_metadata = visit(child, child_ancestors)
            children.append(child_metadata)
            total += child_metadata['total_points']
        return {
            'id': node.node_id,
            'kind': node.kind,
            'title': node.title,
            'points': node.points,
            'total_points': total,
            'answer_index': index,
            'children': children,
        }

    metadata_roots = []
    if explicit:
        for root in roots:
            if not isinstance(root, PedagogicalNode):
                raise ValueError('Cannot mix raw questions and pedagogical nodes')
            metadata_roots.append(visit(root, []))
    else:
        for question in roots:
            index = len(questions)
            node_id = 'legacy-question-' + str(index + 1)
            question.pedagogical_id = node_id
            question.pedagogical_title = question.__doc__ or ''
            question.pedagogical_points = 0
            questions.append(question)
            metadata_roots.append({
                'id': node_id,
                'kind': 'question',
                'title': question.__doc__ or '',
                'points': 0,
                'total_points': 0,
                'answer_index': index,
                'children': [],
            })

    total = 0
    flat_ids = []
    for root in metadata_roots:
        total += root['total_points']
    for question in questions:
        flat_ids.append(question.pedagogical_id)
    return questions, {
        'schema': 1,
        'explicit': explicit,
        'roots': metadata_roots,
        'flat_ids': flat_ids,
        'total_points': total,
    }
