# pylint: disable=no-self-use,missing-function-docstring,undefined-variable
"""R1.05 - TD2 : requetes SQL simples."""

COURSE_OPTIONS = {
    'title': '2026-2027 - R1.05 BDD et SQL - TD2 Requêtes simples',
    'state': 'Draft',
    'checkpoint': 0,
    'allow_copy_paste': 1,
    'forbid_question_copy': 0,
    'automatic_compilation': 0,
    'sequential': 1,
    'save_unlock': 0,
    'question_title': 'Requete demandee',
    'tester_title': 'Validation',
    'editor_title': 'Requete SQL',
    'compiler_title': 'Analyse SQL',
    'executor_title': 'Resultat',
}

DATABASE = """
DROP TABLE IF EXISTS RESULTAT;
DROP TABLE IF EXISTS COURSE;
DROP TABLE IF EXISTS COUREUR;

CREATE TABLE COUREUR (
    NumLicence INT PRIMARY KEY,
    NomCoureur STRING,
    Prenom STRING,
    DateNais STRING
);
CREATE TABLE COURSE (
    NumCourse INT PRIMARY KEY,
    DateCourse STRING,
    CodePostal STRING,
    Ville STRING
);
CREATE TABLE RESULTAT (
    NumCourse INT,
    NumLicence INT,
    Temps STRING,
    Rang INT
);

INSERT INTO COUREUR VALUES
    (1, 'Quinqueton', 'Joel',    '1962-11-29'),
    (2, 'Berry',      'Pierre',  NULL),
    (3, 'Boe',        'Noémie',  '1972-08-18'),
    (4, 'Durand',     'Sylvain', '1970-06-30'),
    (5, 'Lochard',    'Sophie',  '1968-06-15');

INSERT INTO COURSE VALUES
    (201, '2012-11-29', '75000', 'Paris'),
    (202, '2012-11-05', '80330', 'Longueau'),
    (203, '2013-06-15', '59000', 'Lille'),
    (204, '2013-06-30', '60000', 'Beauvais'),
    (205, '2013-08-18', '75000', 'Paris'),
    (206, '2013-09-03', '80000', 'Amiens');

INSERT INTO RESULTAT VALUES
    (204, 1, '01:25:00', 15),
    (202, 2, '01:20:00',  6),
    (202, 3, '01:35:00', 12),
    (203, 4, '01:35:00',  8),
    (203, 5, '01:40:00', 15),
    (204, 2, '01:15:00',  2),
    (203, 1, '01:55:00', 20);
"""

SCHEMA = """
<details open><summary><b>Schema et donnees utiles</b></summary>
<pre>COUREUR(<u>NumLicence</u>, NomCoureur, Prenom, DateNais)
COURSE(<u>NumCourse</u>, DateCourse, CodePostal, Ville)
RESULTAT(<u>NumCourse, NumLicence</u>, Temps, Rang)

RESULTAT.NumCourse  -> COURSE.NumCourse
RESULTAT.NumLicence -> COUREUR.NumLicence</pre>
<p>Les dates sont stockees au format <code>AAAA-MM-JJ</code>. C5 adapte
automatiquement <code>MONTH(DateCourse)</code> et <code>YEAR(DateCourse)</code>
au moteur SQL embarque.</p></details>
"""


def td2_sql_database():
    return DATABASE

def td2_normalize_sql(source):
    pattern = RegExp('\\b(MONTH|YEAR)\\s*\\(\\s*(DateCourse|DateNais)\\s*\\)', 'gi')
    return source.replace(pattern, '$1(DATE($2))')

def td2_default_answer():
    return "-- Ecrivez une seule requete SELECT.\nSELECT "

def td2_expected_answer():
    return this.solution # pylint: disable=undefined-variable

def td2_question():
    return this.statement + SCHEMA # pylint: disable=undefined-variable

def td2_canonical(rows, keep_order=False):
    canonical_rows = []
    for row in rows:
        keys = Object.keys(row)
        keys.sort()
        values = []
        for key in keys:
            value = JSON.stringify(row[key]) or 'null'
            values.append(key + '=' + value)
        canonical_rows.append(values.join('|'))
    if not keep_order:
        canonical_rows.sort()
    return JSON.stringify(canonical_rows)

def td2_tester():
    results = this.worker.executable # pylint: disable=undefined-variable
    one_query = results and len(results) == 1 and Array.isArray(results[0])
    this.message(one_query, 'Une seule requete SELECT est executee')
    if not one_query:
        return
    correct = (this.canonical(results[0], this.ordered)
               == this.canonical(this.expected, this.ordered))
    this.message(correct, 'Le tableau obtenu est exactement celui attendu')
    source = this.worker.source
    for pattern, label in this.required:
        this.message(source.match(RegExp(pattern, 'i')), label)
    if this.all_tests_are_fine:
        this.next_question()


class Q01(Question):
    """01 - Projection sur COUREUR"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = "<h2>1. Liste des coureurs</h2><p>Afficher <code>NomCoureur</code>, <code>Prenom</code> et <code>DateNais</code>.</p>"
    expected = [
        {'NomCoureur': 'Quinqueton', 'Prenom': 'Joel', 'DateNais': '1962-11-29'},
        {'NomCoureur': 'Berry', 'Prenom': 'Pierre', 'DateNais': None},
        {'NomCoureur': 'Boe', 'Prenom': 'Noémie', 'DateNais': '1972-08-18'},
        {'NomCoureur': 'Durand', 'Prenom': 'Sylvain', 'DateNais': '1970-06-30'},
        {'NomCoureur': 'Lochard', 'Prenom': 'Sophie', 'DateNais': '1968-06-15'},
    ]
    solution = "SELECT NomCoureur, Prenom, DateNais FROM COUREUR;"


class Q02(Question):
    """02 - Projection sur COURSE"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = "<h2>2. Date et lieu des courses</h2><p>Afficher <code>DateCourse</code> et <code>Ville</code>.</p>"
    expected = [
        {'DateCourse': '2012-11-29', 'Ville': 'Paris'},
        {'DateCourse': '2012-11-05', 'Ville': 'Longueau'},
        {'DateCourse': '2013-06-15', 'Ville': 'Lille'},
        {'DateCourse': '2013-06-30', 'Ville': 'Beauvais'},
        {'DateCourse': '2013-08-18', 'Ville': 'Paris'},
        {'DateCourse': '2013-09-03', 'Ville': 'Amiens'},
    ]
    solution = "SELECT DateCourse, Ville FROM COURSE;"


class Q03(Question):
    """03 - Selection course 203"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = "<h2>3. Resultats de la course 203</h2><p>Afficher <code>NumLicence</code> et <code>Temps</code>.</p>"
    expected = [
        {'NumLicence': 4, 'Temps': '01:35:00'},
        {'NumLicence': 5, 'Temps': '01:40:00'},
        {'NumLicence': 1, 'Temps': '01:55:00'},
    ]
    solution = "SELECT NumLicence, Temps FROM RESULTAT WHERE NumCourse = 203;"


class Q04(Question):
    """04 - Courses a Paris"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = "<h2>4. Courses organisees a Paris</h2><p>Afficher <code>NumCourse</code> et <code>DateCourse</code>.</p>"
    expected = [
        {'NumCourse': 201, 'DateCourse': '2012-11-29'},
        {'NumCourse': 205, 'DateCourse': '2013-08-18'},
    ]
    solution = "SELECT NumCourse, DateCourse FROM COURSE WHERE Ville = 'Paris';"


class Q05(Question):
    """05 - Coureurs nes avant 1970"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = "<h2>5. Coureurs nes avant 1970</h2><p>Afficher uniquement <code>NomCoureur</code>.</p>"
    expected = [{'NomCoureur': 'Quinqueton'}, {'NomCoureur': 'Lochard'}]
    solution = "SELECT NomCoureur FROM COUREUR WHERE DateNais < '1970-01-01';"


class Q06A(Question):
    """06a - Rang entre 10 et 15 avec BETWEEN"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = "<h2>6a. Rangs de 10 a 15</h2><p>Afficher <code>NumCourse</code> et <code>NumLicence</code> en utilisant <code>BETWEEN</code>.</p>"
    expected = [
        {'NumCourse': 204, 'NumLicence': 1},
        {'NumCourse': 202, 'NumLicence': 3},
        {'NumCourse': 203, 'NumLicence': 5},
    ]
    required = [('\\bBETWEEN\\b', 'La requete utilise BETWEEN')]
    solution = "SELECT NumCourse, NumLicence FROM RESULTAT WHERE Rang BETWEEN 10 AND 15;"


class Q06B(Question):
    """06b - Rang entre 10 et 15 avec comparaisons"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = "<h2>6b. Autre formulation</h2><p>Reprendre la question 6 sans utiliser <code>BETWEEN</code>.</p>"
    expected = Q06A.expected
    required = [('Rang\\s*&gt;=\\s*10|Rang\\s*>=\\s*10', 'La borne inferieure est testee'),
                ('Rang\\s*&lt;=\\s*15|Rang\\s*<=\\s*15', 'La borne superieure est testee')]
    solution = "SELECT NumCourse, NumLicence FROM RESULTAT WHERE Rang >= 10 AND Rang <= 15;"


class Q07A(Question):
    """07a - Novembre 2012 avec MONTH et YEAR"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = """<h2>7a. Courses de novembre 2012</h2>
<p>Afficher <code>NumCourse</code> sous l'alias <code>Numero de course</code>, puis <code>Ville</code>.</p>
<p>Utiliser les fonctions <code>MONTH</code> et <code>YEAR</code>.</p>"""
    expected = [
        {'Numero de course': 201, 'Ville': 'Paris'},
        {'Numero de course': 202, 'Ville': 'Longueau'},
    ]
    required = [('\\bMONTH\\s*\\(', 'La requete utilise MONTH'),
                ('\\bYEAR\\s*\\(', 'La requete utilise YEAR')]
    solution = "SELECT NumCourse AS [Numero de course], Ville\nFROM COURSE\nWHERE MONTH(DateCourse) = 11 AND YEAR(DateCourse) = 2012;"


class Q07B(Question):
    """07b - Novembre 2012 avec un intervalle"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = """<h2>7b. Novembre 2012 sans fonction</h2>
<p>Obtenir le meme tableau en utilisant un intervalle de dates et sans <code>MONTH</code> ni <code>YEAR</code>.</p>"""
    expected = Q07A.expected
    required = [('DateCourse\\s*&gt;=', 'La borne de debut est testee'),
                ('DateCourse\\s*&lt;', 'La borne de fin est testee')]
    solution = "SELECT NumCourse AS [Numero de course], Ville\nFROM COURSE\nWHERE DateCourse >= '2012-11-01' AND DateCourse < '2012-12-01';"


class Q08(Question):
    """08 - Date de naissance NULL"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = "<h2>8. Date de naissance non renseignee</h2><p>Afficher le nom des coureurs concernes.</p>"
    expected = [{'NomCoureur': 'Berry'}]
    required = [('\\bIS\\s+NULL\\b', 'La requete teste IS NULL')]
    solution = "SELECT NomCoureur FROM COUREUR WHERE DateNais IS NULL;"


class Q09(Question):
    """09 - Ville commencant par L"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = "<h2>9. Ville commencant par L</h2><p>Afficher uniquement <code>NumCourse</code>.</p>"
    expected = [{'NumCourse': 202}, {'NumCourse': 203}]
    required = [('\\bLIKE\\b', 'La requete utilise LIKE')]
    solution = "SELECT NumCourse FROM COURSE WHERE Ville LIKE 'L%';"


class Q10(Question):
    """10 - Coureurs par age croissant"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = """<h2>10. Coureurs par age croissant</h2>
<p>Afficher <code>NomCoureur</code>, <code>Prenom</code> et <code>DateNais</code>. Les plus jeunes sont donc affiches d'abord ; la date inconnue vient en dernier.</p>"""
    expected = [
        {'NomCoureur': 'Boe', 'Prenom': 'Noémie', 'DateNais': '1972-08-18'},
        {'NomCoureur': 'Durand', 'Prenom': 'Sylvain', 'DateNais': '1970-06-30'},
        {'NomCoureur': 'Lochard', 'Prenom': 'Sophie', 'DateNais': '1968-06-15'},
        {'NomCoureur': 'Quinqueton', 'Prenom': 'Joel', 'DateNais': '1962-11-29'},
        {'NomCoureur': 'Berry', 'Prenom': 'Pierre', 'DateNais': None},
    ]
    ordered = True
    required = [('\\bORDER\\s+BY\\b', 'La requete utilise ORDER BY'),
                ('DateNais\\s+DESC', 'Les dates sont triees par ordre decroissant')]
    solution = "SELECT NomCoureur, Prenom, DateNais FROM COUREUR ORDER BY DateNais DESC;"


class Q11(Question):
    """11 - Tri sur deux colonnes"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = "<h2>11. Tri sur deux niveaux</h2><p>Afficher <code>Ville</code> et <code>DateCourse</code> : ville croissante, puis date decroissante.</p>"
    expected = [
        {'Ville': 'Amiens', 'DateCourse': '2013-09-03'},
        {'Ville': 'Beauvais', 'DateCourse': '2013-06-30'},
        {'Ville': 'Lille', 'DateCourse': '2013-06-15'},
        {'Ville': 'Longueau', 'DateCourse': '2012-11-05'},
        {'Ville': 'Paris', 'DateCourse': '2013-08-18'},
        {'Ville': 'Paris', 'DateCourse': '2012-11-29'},
    ]
    ordered = True
    required = [('Ville\\s*(ASC\\s*)?,', 'Le premier niveau trie les villes'),
                ('DateCourse\\s+DESC', 'Le second niveau trie les dates')]
    solution = "SELECT Ville, DateCourse FROM COURSE ORDER BY Ville ASC, DateCourse DESC;"


class Q12A(Question):
    """12a - Courses 202 ou 204 avec OR"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = "<h2>12a. Participants aux courses 202 ou 204</h2><p>Afficher sans doublon les <code>NumLicence</code>, tries, en utilisant <code>OR</code>.</p>"
    expected = [{'NumLicence': 1}, {'NumLicence': 2}, {'NumLicence': 3}]
    ordered = True
    required = [('\\bOR\\b', 'La requete utilise OR'),
                ('\\bDISTINCT\\b', 'Les doublons sont elimines avec DISTINCT')]
    solution = "SELECT DISTINCT NumLicence FROM RESULTAT WHERE NumCourse = 202 OR NumCourse = 204 ORDER BY NumLicence;"


class Q12B(Question):
    """12b - Courses 202 ou 204 avec IN"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = "<h2>12b. Meme resultat avec IN</h2><p>Utiliser cette fois <code>IN</code>.</p>"
    expected = Q12A.expected
    ordered = True
    required = [('\\bIN\\s*\\(', 'La requete utilise IN'),
                ('\\bDISTINCT\\b', 'Les doublons sont elimines avec DISTINCT')]
    solution = "SELECT DISTINCT NumLicence FROM RESULTAT WHERE NumCourse IN (202, 204) ORDER BY NumLicence;"


class Q12C(Question):
    """12c - Courses 202 ou 204 avec UNION"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = "<h2>12c. Meme resultat avec UNION</h2><p>Utiliser deux requetes reunies par <code>UNION</code>.</p>"
    expected = Q12A.expected
    ordered = True
    required = [('\\bUNION\\b', 'La requete utilise UNION'),
                ('\\bORDER\\s+BY\\b', 'Le resultat est trie')]
    solution = "SELECT NumLicence FROM RESULTAT WHERE NumCourse = 202\nUNION\nSELECT NumLicence FROM RESULTAT WHERE NumCourse = 204\nORDER BY NumLicence;"


class Q13(Question):
    """13 - Novembre 2012 hors Paris"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = "<h2>13. Course de novembre 2012 hors Paris</h2><p>Afficher <code>NumCourse</code>, <code>DateCourse</code> et <code>Ville</code>.</p>"
    expected = [{'NumCourse': 202, 'DateCourse': '2012-11-05', 'Ville': 'Longueau'}]
    solution = "SELECT NumCourse, DateCourse, Ville FROM COURSE\nWHERE MONTH(DateCourse) = 11 AND YEAR(DateCourse) = 2012 AND Ville <> 'Paris';"


class Q14(Question):
    """14 - Resultats de la licence 2"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = "<h2>14. Resultats de la licence 2</h2><p>Afficher <code>NumCourse</code>, <code>NumLicence</code> et <code>Temps</code>.</p>"
    expected = [
        {'NumCourse': 202, 'NumLicence': 2, 'Temps': '01:20:00'},
        {'NumCourse': 204, 'NumLicence': 2, 'Temps': '01:15:00'},
    ]
    solution = "SELECT NumCourse, NumLicence, Temps FROM RESULTAT WHERE NumLicence = 2;"


class Q15A(Question):
    """15a - Resultat de Lochard avec JOIN"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = "<h2>15a. Resultat de Lochard</h2><p>Afficher <code>NumCourse</code> et <code>Temps</code> avec une jointure explicite.</p>"
    expected = [{'NumCourse': 203, 'Temps': '01:40:00'}]
    required = [('\\bJOIN\\b', 'La requete utilise JOIN')]
    solution = "SELECT R.NumCourse, R.Temps FROM RESULTAT R\nJOIN COUREUR C ON C.NumLicence = R.NumLicence\nWHERE C.NomCoureur = 'Lochard';"


class Q15B(Question):
    """15b - Resultat de Lochard avec produit et selection"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = "<h2>15b. Autre formulation</h2><p>Obtenir le meme resultat avec les deux tables dans <code>FROM</code> et les conditions dans <code>WHERE</code>.</p>"
    expected = Q15A.expected
    required = [('FROM\\s+RESULTAT[^;]+,\\s*COUREUR|FROM\\s+COUREUR[^;]+,\\s*RESULTAT', 'Les deux tables figurent dans FROM')]
    solution = "SELECT R.NumCourse, R.Temps FROM RESULTAT R, COUREUR C\nWHERE C.NumLicence = R.NumLicence AND C.NomCoureur = 'Lochard';"


class Q16(Question):
    """16 - Tous les resultats avec les noms"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = "<h2>16. Resultats de tous les coureurs</h2><p>Afficher <code>NumCourse</code>, <code>NomCoureur</code>, <code>Temps</code> et <code>Rang</code>.</p>"
    expected = [
        {'NumCourse': 204, 'NomCoureur': 'Quinqueton', 'Temps': '01:25:00', 'Rang': 15},
        {'NumCourse': 202, 'NomCoureur': 'Berry', 'Temps': '01:20:00', 'Rang': 6},
        {'NumCourse': 202, 'NomCoureur': 'Boe', 'Temps': '01:35:00', 'Rang': 12},
        {'NumCourse': 203, 'NomCoureur': 'Durand', 'Temps': '01:35:00', 'Rang': 8},
        {'NumCourse': 203, 'NomCoureur': 'Lochard', 'Temps': '01:40:00', 'Rang': 15},
        {'NumCourse': 204, 'NomCoureur': 'Berry', 'Temps': '01:15:00', 'Rang': 2},
        {'NumCourse': 203, 'NomCoureur': 'Quinqueton', 'Temps': '01:55:00', 'Rang': 20},
    ]
    solution = "SELECT R.NumCourse, C.NomCoureur, R.Temps, R.Rang\nFROM RESULTAT R JOIN COUREUR C ON C.NumLicence = R.NumLicence;"


class Q17A(Question):
    """17a - Resultats a Lille avec JOIN"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = "<h2>17a. Resultats de la course a Lille</h2><p>Afficher <code>NumCourse</code>, <code>NumLicence</code>, <code>Temps</code> et <code>Rang</code> avec <code>JOIN</code>.</p>"
    expected = [
        {'NumCourse': 203, 'NumLicence': 4, 'Temps': '01:35:00', 'Rang': 8},
        {'NumCourse': 203, 'NumLicence': 5, 'Temps': '01:40:00', 'Rang': 15},
        {'NumCourse': 203, 'NumLicence': 1, 'Temps': '01:55:00', 'Rang': 20},
    ]
    required = [('\\bJOIN\\b', 'La requete utilise JOIN')]
    solution = "SELECT R.NumCourse, R.NumLicence, R.Temps, R.Rang\nFROM RESULTAT R JOIN COURSE C ON C.NumCourse = R.NumCourse\nWHERE C.Ville = 'Lille';"


class Q17B(Question):
    """17b - Resultats a Lille avec produit et selection"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = "<h2>17b. Autre formulation</h2><p>Obtenir le meme resultat avec les deux tables dans <code>FROM</code> et les conditions dans <code>WHERE</code>.</p>"
    expected = Q17A.expected
    required = [('FROM\\s+RESULTAT[^;]+,\\s*COURSE|FROM\\s+COURSE[^;]+,\\s*RESULTAT', 'Les deux tables figurent dans FROM')]
    solution = "SELECT R.NumCourse, R.NumLicence, R.Temps, R.Rang\nFROM RESULTAT R, COURSE C\nWHERE C.NumCourse = R.NumCourse AND C.Ville = 'Lille';"


class Q18(Question):
    """18 - Resultats de juin 2013"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = "<h2>18. Courses de juin 2013</h2><p>Afficher <code>NumCourse</code>, <code>NomCoureur</code>, <code>Prenom</code>, <code>Temps</code> et <code>Rang</code>.</p>"
    expected = [
        {'NumCourse': 204, 'NomCoureur': 'Quinqueton', 'Prenom': 'Joel', 'Temps': '01:25:00', 'Rang': 15},
        {'NumCourse': 203, 'NomCoureur': 'Durand', 'Prenom': 'Sylvain', 'Temps': '01:35:00', 'Rang': 8},
        {'NumCourse': 203, 'NomCoureur': 'Lochard', 'Prenom': 'Sophie', 'Temps': '01:40:00', 'Rang': 15},
        {'NumCourse': 204, 'NomCoureur': 'Berry', 'Prenom': 'Pierre', 'Temps': '01:15:00', 'Rang': 2},
        {'NumCourse': 203, 'NomCoureur': 'Quinqueton', 'Prenom': 'Joel', 'Temps': '01:55:00', 'Rang': 20},
    ]
    solution = "SELECT R.NumCourse, C.NomCoureur, C.Prenom, R.Temps, R.Rang\nFROM RESULTAT R\nJOIN COURSE CO ON CO.NumCourse = R.NumCourse\nJOIN COUREUR C ON C.NumLicence = R.NumLicence\nWHERE MONTH(CO.DateCourse) = 6 AND YEAR(CO.DateCourse) = 2013;"


class Q19(Question):
    """19 - Departement 80 et temps inferieur a 1 h 30"""
    sql_database = td2_sql_database
    normalize_sql = td2_normalize_sql
    default_answer = td2_default_answer
    expected_answer = td2_expected_answer
    question = td2_question
    canonical = td2_canonical
    tester = td2_tester
    ordered = False
    required = []
    statement = """<h2>19. Participants dans le departement 80 en moins de 1 h 30</h2>
<p>Afficher <code>NomCoureur</code>, <code>Prenom</code>, <code>Temps</code> et <code>Ville</code>.</p>"""
    expected = [{'NomCoureur': 'Berry', 'Prenom': 'Pierre', 'Temps': '01:20:00', 'Ville': 'Longueau'}]
    solution = "SELECT C.NomCoureur, C.Prenom, R.Temps, CO.Ville\nFROM RESULTAT R\nJOIN COURSE CO ON CO.NumCourse = R.NumCourse\nJOIN COUREUR C ON C.NumLicence = R.NumLicence\nWHERE CO.CodePostal LIKE '80%' AND R.Temps < '01:30:00';"
