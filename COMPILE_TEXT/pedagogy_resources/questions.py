"""Demonstration of recursive pedagogy with multiple question resources."""

# This is deliberately a separate session from TEXT=pedagogy. Development
# upgrades preserve existing runtime sessions, while a new session is seeded
# with its generated schema and can therefore demonstrate new metadata safely.
try:
    GENERATING_QUESTIONS_JSON
except NameError:
    GENERATING_QUESTIONS_JSON = False

COURSE_OPTIONS = {
    'title': 'Démonstrateur de ressources pédagogiques',
    'state': 'Ready',
    'checkpoint': 0,
    'expected_students': 'nobody',
    'positions': {
        'question': [25, 35, 0, 35, '#EFEF'],
        'tester': [25, 35, 35, 65, '#EFEF'],
        'editor': [60, 40, 0, 100, '#FFFF'],
        'compiler': [100, 0, 0, 0, '#EEFF'],
        'executor': [100, 0, 0, 0, '#EEFF'],
        'time': [80, 20, 98, 2, '#0000'],
        'index': [0, 25, 0, 100, '#FFFF'],
    },
}


class QContext(Question):
    """Contexte avec sa propre réponse"""
    def question(self):
        return 'Donnez un titre court à cette partie.'

    def default_answer(self):
        return ''

    def deferred_grading(self, source):
        fraction = 0
        if source.strip() == 'Titre':
            fraction = 1
        return {'fraction': fraction, 'expected': 'Titre'}


class QDetail(Question):
    """Sous-question avec plusieurs fichiers"""
    def question(self):
        return 'Expliquez le titre en une phrase.'

    def default_answer(self):
        return ''

    def deferred_grading(self, source):
        fraction = 0
        if source.strip() == 'Explication':
            fraction = 1
        return {'fraction': fraction, 'expected': 'Explication'}


class QConclusion(Question):
    """Conclusion"""
    def question(self):
        return 'Rédigez une conclusion.'

    def default_answer(self):
        return ''

    def deferred_grading(self, source):
        fraction = 0
        if source.strip() == 'Conclusion':
            fraction = 1
        return {'fraction': fraction, 'expected': 'Conclusion'}


def build_pedagogy():
    """Build a tree whose detail question owns three distinct resources."""
    return Exercise('exercise.structure', 'Exercice structuré', [
        Section('section.analysis', 'Analyse', [
            QuestionNode('question.context', QContext(), 'Contexte', [
                # Pinned RapydScript requires positional constructor arguments.
                QuestionNode('question.detail', QDetail(), 'Détail', None, 1,
                    False, [
                        Resource('source', None, 'Réponse', 'text', 'text',
                                 None, True, False, False, True, True,
                                 'question', None, True),
                        Resource('notes', 'notes.txt', 'Notes de travail', 'text',
                                 '', 'Notes facultatives\n', True, False, False,
                                 False, False, 'question', None, False),
                        Resource('consigne', 'consigne.txt', 'Consigne', 'text',
                                 '', 'Expliquez le titre en une phrase.\n', False,
                                 False, False, False, False, 'question', None,
                                 False),
                    ]),
            ], 2),
        ]),
        QuestionNode('question.conclusion', QConclusion(), 'Conclusion', None, 3),
    ])


if GENERATING_QUESTIONS_JSON:
    Session(build_pedagogy())
