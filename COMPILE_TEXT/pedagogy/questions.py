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


PEDAGOGY = Exercise('exercise.structure', 'Exercice structuré', children=[
    Section('section.analysis', 'Analyse', children=[
        QuestionNode('question.context', QContext(), 'Contexte', points=2, children=[
            QuestionNode('question.detail', QDetail(), 'Détail', points=1),
        ]),
    ]),
    QuestionNode('question.conclusion', QConclusion(), 'Conclusion', points=3),
])

Session(PEDAGOGY)
