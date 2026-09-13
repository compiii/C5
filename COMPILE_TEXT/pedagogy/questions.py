"""Demonstration of recursive exercises, sections and questions."""

COURSE_OPTIONS = {
    'title': 'Démonstrateur de structure pédagogique',
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


class QDetail(Question):
    """Sous-question"""
    def question(self):
        return 'Expliquez le titre en une phrase.'

    def default_answer(self):
        return ''


class QConclusion(Question):
    """Conclusion"""
    def question(self):
        return 'Rédigez une conclusion.'

    def default_answer(self):
        return ''


def build_pedagogy():
    """Build metadata only during the trusted CPython generation pass."""
    return Exercise('exercise.structure', 'Exercice structuré', [
        Section('section.analysis', 'Analyse', [
            QuestionNode('question.context', QContext(), 'Contexte', [
                QuestionNode('question.detail', QDetail(), 'Détail', None, 1),
            ], 2),
        ]),
        QuestionNode('question.conclusion', QConclusion(), 'Conclusion', None, 3),
    ])


if GENERATING_QUESTIONS_JSON:
    Session(build_pedagogy())
