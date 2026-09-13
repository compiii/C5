
"""
Helper to create 'COMPILE_.../session.json' file containing questionnary information.
"""
import json

# Modern questionnaires register classes named Q... while they are defined.
# Older questionnaires either use arbitrary class names or expose an init()
# factory returning question instances. Keep the modern path unchanged and
# enable these compatibility paths only when no class was registered.
if not question_instances and not question_classes: # pylint: disable=undefined-variable
    initializer = globals().get('init')
    if callable(initializer):
        Session(initializer()) # pylint: disable=undefined-variable

if not question_instances and not question_classes: # pylint: disable=undefined-variable
    question_classes.extend(Question.__subclasses__()) # pylint: disable=undefined-variable

if not question_instances: # pylint: disable=undefined-variable
    for question_class in question_classes: # pylint: disable=undefined-variable
        question_instances.append(question_class()) # pylint: disable=undefined-variable
    question_instances[:], pedagogy_metadata = flatten_pedagogy(question_instances)

if not question_instances: # pylint: disable=undefined-variable
    raise ValueError('No question found while generating questions.json')

infos = []
for question in question_instances: # pylint: disable=undefined-variable
    question._version = 'a'
    notation_a = question.grading_ladder()
    question._version = 'b'
    notation_b = question.grading_ladder()
    infos.append(
        {
            'id': question.pedagogical_id,
            'title': question.pedagogical_title or question.__doc__ or '',
            'points': question.pedagogical_points,
            'notation_a': notation_a,
            'notation_b': notation_b
        })

infos[0]['options'] = options = {}
for key, value in Session.default_options.items():
    options[key] = value
try:
    for key, value in COURSE_OPTIONS.items():
        if value == False:
            value = 0
        elif value == True:
            value = 1
        options[key] = value
except NameError:
    pass
options['pedagogy'] = pedagogy_metadata

print(json.dumps(infos))
