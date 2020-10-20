# -*- coding: utf-8 -*- äöü
"""
utils-Modul des Adapters unitracc->sqlwrapper

Autor: Tobias Herp
"""
# Python compatibility:
from __future__ import absolute_import

from six import string_types as six_string_types
from six.moves import map, zip

__all__ = [# Funktionen:
           # SQL names:
           'check_name',
           "check_alias",
           'replace_names',
           # SQL generation:
           "make_transaction_cmd",
           "make_where_mask",
           "make_grouping_wrapper",
               # specific helper:
               "_groupable_spectup",
           "make_returning_clause",
           # "make_join",  # not yet implemented
           # Formatting:
           "normalize_sql_snippet",
           # helpers:
           "extract_dict",
           'generate_dicts',
           "is_sequence",
           # Klassen:
           'SmartDict',
           ]

# Standard library:
from string import digits, letters, uppercase, whitespace

NAMECHARS = frozenset(letters+'._')
ALLNAMECHARS = frozenset(letters+digits+'._')
SNIPPETCHARS = frozenset(uppercase + whitespace)


def check_name(sqlname, for_select=False):
    """
    Prüfe, ob der übergebene Name einer SQL-Tabelle (oder sonstigen
    benannten Ressource) syntaktisch valide und ohne Quoting
    verwendbar ist.  Gib den Namen im Erfolgsfall unverändert zurück;
    wirf ansonsten einen ValueError.

    >>> check_name('tan.tan')
    'tan.tan'

    Ziffern, die kein Segment einleiten, sind erlaubt:

    >>> check_name('witrabau.p2_witrabau_partners_view')
    'witrabau.p2_witrabau_partners_view'

    Am Anfang eines Segments sind sie aber verboten:

    >>> check_name('witrabau.2_witrabau_partners_view')
    Traceback (most recent call last):
    ...
    ValueError: Error in 'witrabau.2_witrabau_partners_view': '2' must not start a segment

    Doppelte Punkte:
    >>> check_name('tan..tan')
    Traceback (most recent call last):
        ...
    ValueError: Empty segment in 'tan..tan'

    Leere Namen:
    >>> check_name('')
    Traceback (most recent call last):
        ...
    ValueError: Empty segment in ''
    """
    if not isinstance(sqlname, six_string_types):
        raise TypeError('%r is not a string' % (sqlname,))

    invalid = set(sqlname).difference(ALLNAMECHARS)
    if invalid:
        raise ValueError('Invalid chars in %r: %s'
                         % (sqlname, tuple(invalid),))
    for s in sqlname.split('.'):
        if not s:
            raise ValueError('Empty segment in %r' % sqlname)
        if s[0] not in NAMECHARS:
            raise ValueError('Error in %r: %r must not start a segment'
                             % (sqlname, s[0]))
    return sqlname


def check_alias(sqlname):
    """
    Wie check_name, aber mit Unterstützung für AS-Angaben
    (sinnvoll z.B. für returning-Angaben):
    >>> check_alias('id AS user_and_course_id')
    'id AS user_and_course_id'

    Achtung, gleichbedeutend:
    >>> check_alias('id user_and_course_id')
    'id user_and_course_id'

    Offensichtliche Fehler werden erkannt:
    >>> check_alias('id user_and_course_id zwei')
    Traceback (most recent call last):
      ...
    ValueError: Part 'id user_and_course_id zwei': AS expected, found: 'user_and_course_id'
    >>> check_alias('id AS user_and_course_id zwei')
    Traceback (most recent call last):
      ...
    ValueError: Part too long ('id AS user_and_course_id zwei')
    >>> check_alias('id as')
    Traceback (most recent call last):
      ...
    ValueError: Misplaced AS ('id as')
    >>> check_alias('as user_and_course_id ')
    Traceback (most recent call last):
      ...
    ValueError: Misplaced AS ('as user_and_course_id ')
    >>> check_alias('   ')
    Traceback (most recent call last):
      ...
    ValueError: Empty name or alias ('   ')
    """
    if sqlname == '*':
        return sqlname
    words = sqlname.split()
    if not words:
        raise ValueError('Empty name or alias (%(sqlname)r)' % locals())
    if words[3:]:
        raise ValueError('Part too long (%(sqlname)r)' % locals())
    if not words[2:]:
        for word in words:
            if word.upper() == 'AS':
                raise ValueError('Misplaced AS (%(sqlname)r)' % locals())
            check_name(word)
    else:
        if words[1].lower() != 'as':
            raise ValueError('Part %r: AS expected, found: %r'
                             % (sqlname, words[1]))
        for word in words[0::2]: # 0, 2, 4 ... aber: siehe oben
            if word.upper() == 'AS':
                raise ValueError('Misplaced AS (%(sqlname)r)' % locals())
            check_name(word)
    return sqlname


def generate_dicts(sqlres, names):
    """
    Zur Verwendung mit INSERT ... RETURNING:
    Erzeuge aus dem Rückgabewert von db.query eine Sequenz von Dictionarys.

    sqlres -- ein 2-Tupel; der zweite Wert ist eine Liste von Tupeln
    names -- eine Sequenz von Namen

    >>> res = ([{'scale': None, 'name': 'id', 'precision': None, 'width': None, 'null': None, 'type': 'n'}], [(3,)])
    >>> list(generate_dicts(res, names=('id',)))
    [{'id': 3}]
    >>> list(generate_dicts(res, names='id'))
    [{'id': 3}]
    >>> list(generate_dicts(res, names='*'))
    [{'id': 3}]
    """
    if names == '*':
        names = [topic['name'] for topic in sqlres[0]]
    elif not is_sequence(names):
        names = [names]
    raw = sqlres[1]
    for row in raw:  # no dict(list(zip())) necessary, right?
        yield dict(zip(names, row))


def normalize_sql_snippet(snippet):
    """
    Normalisiere einen SQL-Schnipsel und gib ihn zurück.
    Im Ergebnis sind nur Großbuchstaben und ggf. Leerzeichen enthalten;
    evtl. wird ein ValueError geworfen.

    >>> normalize_sql_snippet('  read  only  ')
    'READ ONLY'
    """
    res = ' '.join(snippet.upper().split())
    invalid = set(res).difference(SNIPPETCHARS)
    if invalid:
        raise ValueError('Invalid chars in %r: %s'
                         % (snippet, tuple(invalid),))
    return res

ISOLATION_LEVELS = set(['SERIALIZABLE',
                        'REPEATABLE READ',
                        'READ COMMITTED',
                        'READ UNCOMMITTED', # in PostgreSQL wie read committed
                        ])
TRANSACTION_MODES = set(['READ WRITE',
                         'READ ONLY',
                         ])
for item in ISOLATION_LEVELS:
    TRANSACTION_MODES.add(item)
    TRANSACTION_MODES.add('ISOLATION LEVEL '+item)


# http://www.postgresql.org/docs/9.1/static/sql-start-transaction.html
# http://www.postgresql.org/docs/9.1/static/sql-set-transaction.html
def make_transaction_cmd(action, *args):
    """
    Nimm einige Spezifikationen für Transaktionen entgegen
    und erzeuge daraus das entsprechende SQL-Statement.

    >>> make_transaction_cmd('BEGIN')
    'BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;'
    >>> make_transaction_cmd('SET', 'read only')
    'SET TRANSACTION READ ONLY;'
    """
    assert action in ('BEGIN', 'SET')
    isolation_level = None
    other_specs = []
    for a in args:
        AA = normalize_sql_snippet(a)
        if AA in ISOLATION_LEVELS:
            isolation_level = 'ISOLATION LEVEL ' + AA
        elif AA in TRANSACTION_MODES:
            if AA.startswith('ISOLATION LEVEL '):
                isolation_level = AA
            else:
                other_specs.append(AA)
        else:
            raise ValueError('Unbekannter Transaktionsmodus: %r' % (AA,))
    if isolation_level is None and action == 'BEGIN':
        isolation_level = 'ISOLATION LEVEL READ COMMITTED'
    if isolation_level is not None:
        other_specs.insert(0, isolation_level)
    return '%s TRANSACTION %s;' % (action, ', '.join(other_specs))


class SmartDict(dict):
    """
    Für die Generierung von SQL-Anweisungen:
    Ein Dictionary, das die ihm bekannten Werte ersetzt
    und für die anderen den Platzhalter repliziert.

    >>> smartie = SmartDict(foo='bar')
    >>> '%(foo)s %(baz)s' % smartie
    'bar %(baz)s'
    """
    def __getitem__(self, key):
        """
        >>> sd = SmartDict()
        >>> sd.__getitem__('missing')
        '%(missing)s'
        """
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            check_name(key)
            return key.join(('%(', ')s'))

def replace_names(sql, **kwargs):
    """
    Zur Vorverarbeitung: Sicheres Ersetzen von Tabellen- und
    sonstigen Namen, bevor der Datenbankadapter für das Quoting der
    Werte sorgt.

    Die Tabellen...namen werden *nicht* gequotet, weil das das Ende
    der Groß-/Kleinschreibungstoleranz bedeuten würde; stattdessen
    wird sichergestellt, daß keine gefährlichen Zeichen enthalten
    sind.

    sql - das SQL-Statement
    kwargs -- Platzhalter und Werte für die Namen von Tabellen o.ä.
              (werden mit check_name überprüft)

    >>> replace_names('SELECT * FROM %(table)s WHERE val=%(val)s;', table='fozzie')
    'SELECT * FROM fozzie WHERE val=%(val)s;'
    """
    for v in kwargs.values():
        check_name(v)
    dic = SmartDict(kwargs)
    return sql % dic

WHERE = intern('WHERE')
def make_where_mask(dic, fields=None, keyword=WHERE):
    """
    Komfort-Funktion; wenn die Query-Daten schon als dict vorliegen,
    braucht man sich die WHERE-Bedingung nicht aus den Fingern zu saugen.
    Ohne Daten ist das Ergebnis ein Leerstring (also auch ohne 'WHERE').

    dic -- die Query-Daten. Es werden nur die Schlüssel verwendet; die Werte
           werden beim Absenden der Query vom SQL-Adapter eingesetzt.

    fields -- wenn angegeben, werden die in <fields> aufgeführten Schlüssel
              bevorzugt behandelt; ansonsten bestimmt sich die Reihenfolge
              nach ASCII-Sortierung.

    >>> make_where_mask({})
    ''
    >>> make_where_mask({'answer': 42})
    'WHERE answer = %(answer)s'
    >>> query_data={'zwei': 2, 'eins': 1}
    >>> make_where_mask(query_data)
    'WHERE eins = %(eins)s AND zwei = %(zwei)s'
    >>> len(query_data)
    2
    >>> make_where_mask(query_data, ['zwei', 'eins'])
    'WHERE zwei = %(zwei)s AND eins = %(eins)s'

    'drei' ist in der fields-Liste nicht erwähnt und kommt daher zum Schluß:

    >>> query_data['drei'] = 3
    >>> make_where_mask(query_data, ['zwei', 'eins'])
    'WHERE zwei = %(zwei)s AND eins = %(eins)s AND drei = %(drei)s'

    Unterstützung von Sequenzen:

    >>> make_where_mask({'status': ['new', 'reserved']})
    'WHERE status = ANY(%(status)s)'

    Bei Verwendung von Gruppierung und Aggregatfunktionen:

    >>> make_where_mask({'status': ['new', 'reserved']}, keyword='HAVING')
    'HAVING status = ANY(%(status)s)'
    """
    assert keyword in (WHERE, 'HAVING')
    keys = sorted(dic.keys())
    if fields:
        po = len(fields)
        tmp = []
        for key in keys:
            try:
                idx = fields.index(key)
                tmp.append((idx, key))
            except ValueError:
                tmp.append((po, key))
                po += 1
        tmp.sort()
        keys = [tup[1] for tup in tmp]
    if keys:
        res = []
        for key in keys:
            if is_sequence(dic[key]):
                res.append(''.join((key, ' = ANY(%(', key, ')s)')))
            else:
                res.append(''.join((key, ' = %(', key, ')s')))
        return ' '.join((keyword, ' AND '.join(res)))
    return ''

def _groupable_spectup(item):
    """
    Für make_grouping_wrapper (fields-Argument)
    generiere ein 3-Tupel:
    - Feldname für fields-Sequenz (make_where_mask)
    - Aggregatfunktionsaufruf
    - Name für Gruppierung

    >>> _groupable_spectup('feld')
    ('feld', 'feld', 'feld')
    >>> _groupable_spectup(['feld'])
    ('feld', 'feld', 'feld')

    Es darf eine Aggregatfunktion angegeben werden;
    in diesem Fall wird danach nicht gruppiert:

    >>> _groupable_spectup(['feld', 'MAX'])
    ('feld', 'MAX(feld) feld', None)

    Das optionale dritte Element ist ein Aliasname:

    >>> _groupable_spectup(['feld', 'MAX', 'alias'])
    ('feld', 'MAX(feld) alias', None)
    >>> _groupable_spectup(['feld', None, 'alias'])
    ('feld', 'feld alias', 'alias')
    """
    if isinstance(item, six_string_types):
        spec = [item]
    else:
        spec = list(item)
    name = check_name(spec.pop(0))
    if spec:
        aggr = spec.pop(0)
    else:
        aggr = None
    if spec:
        alias = spec.pop(0)
        assert not spec, 'max. 3 Elemente bitte! (%r)' % (item,)
    else:
        alias = name

    res = [name]
    if aggr is None:
        if name == alias:
            res.append(name)
        else:
            res.append(' '.join((name,
                                 check_name(alias),
                                 )))
        # alias ist hier identisch mit (gechecktem) Namen
        # oder wurde soeben gecheckt:
        res.append(alias)
    else:
        aggr = check_name(aggr)
        if alias != name:
            alias = check_name(alias)
        res.append('%(aggr)s(%(name)s) %(alias)s'
                   % locals())
        res.append(None)
    return tuple(res)


def make_grouping_wrapper(tov, query_data, fields):
    r"""
    Generiere einen SQL-Befehl, der
    - die übergebene Tabelle oder Sicht (tov) mit WHERE-Kriterium filtert
    - und das Ergebnis gruppiert

    tov -- table or view (etwaige Joins sind von einer benannten
           View zu leisten)
    query_data -- wenn None oder ein leeres Dict,
                  ist das Verhalten vorerst undefiniert
    fields -- im Gegensatz zur vorstehenden Funktion make_where_mask ist
              dies keine einfache Sequenz von Feldnamen; erlaubt sind
              einfache Strings oder Tupel mit bis zu 3 Elementen

    select name, aggregate ... from
       (select name...
          from tov
         where ...);


    >>> tov = 'the_view'
    >>> qd = {'status': 'used'}
    >>> fields = ('status', ('user', None, 'used_by'), ('date', 'MAX'))
    >>> make_grouping_wrapper(tov, qd, fields)
    'SELECT status, user used_by, MAX(date) date\n  FROM the_view\n GROUP BY status, used_by\nHAVING status = %(status)s;'
    >>> qd = {'status': 'new'}
    >>> fields = ('status', ('user', None, 'used_by'), ('date', 'MAX'))

    >x> make_grouping_wrapper(tov, qd, fields)
    """
    for_mwm = []
    for_fieldlist = []
    for_grouping = []
    for item in fields:
        t1, t2, t3 = _groupable_spectup(item)
        for_mwm.append(t1)
        for_fieldlist.append(t2)
        if t3 is not None:
            for_grouping.append(t3)
    where = make_where_mask(query_data, for_mwm,
                            (for_grouping # nicht *nur* Aggregate,
                                          # aber es gibt welche:
                             and len(for_grouping) < len(for_fieldlist)
                             ) and 'HAVING' or WHERE)
    tov = check_name(tov)
    if for_fieldlist:
        res = ['SELECT '+(', '.join(for_fieldlist)
                          )]
    else:
        res = ['SELECT *']
    res.append('  FROM '+tov)
    if for_grouping:
        res.append(' GROUP BY '+', '.join(for_grouping))
    if where:
        res.append(where)
    return '\n'.join(res)+';'


def is_sequence(arg):
    """
    Handelt es sich im Sinne von SQL um eine Sequenz (abzugleichen mit
    ... = ANY (...) anstelle von ... = ...)?

    >>> is_sequence('test')
    False
    >>> is_sequence(['a', 'b'])
    True
    >>> is_sequence(42)
    False

    Auch Generatoren werden erkannt:
    >>> is_sequence(xrange(1, 3))
    True
    """
    if hasattr(arg, 'strip'):
        return False
    return (hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__")
            )

def make_returning_clause(fields):
    """
    Gib eine RETURNING-Klausel zurück (PostgreSQL-Erweiterung gegenüber
    dem SQL-Standard, ab Version 9.1):

    >>> make_returning_clause('*')
    'RETURNING *'
    >>> make_returning_clause('id')
    'RETURNING id'
    >>> make_returning_clause(['tan', 'status'])
    'RETURNING tan, status'

    Solche returning-Ausdrücke werden vom Datenbanktreiber derzeit leider nicht
    korrekt interpretiert - es kommt ein Feldname "is AS some_better_name"
    dabei heraus.  Deshalb prüfen wir hier vorerst weiterhin mit check_name,
    nicht mit check_alias:
    >>> make_returning_clause('id AS some_better_name')
    Traceback (most recent call last):
        ...
    ValueError: Invalid chars in 'id AS some_better_name': (' ',)
    """
    if fields == '*':
        return 'RETURNING *'
    if not is_sequence(fields):
        liz = [fields]
    else:
        liz = fields
    return 'RETURNING ' + ', '.join(map(check_name, liz))

def extract_dict(fields, source, pop=1, noempty=1):
    """
    Extrahiere die angegebenen Felder aus dem Quell-Dictionary,
    um sie beispielsweise in eine andere Tabelle zu schreiben.
    Dabei werden die gefundenen Schlüssel normalerweise aus der Quelle
    gelöscht:

    >>> source={'tan': 123, 'status': 'new', 'owner_id': 'Willy'}
    >>> extract_dict(['status'], source)
    {'status': 'new'}
    >>> source
    {'tan': 123, 'owner_id': 'Willy'}

    Wird pop=0 übergeben, bleibt die Quelle unverändert erhalten:

    >>> extract_dict(['owner_id'], source, pop=0)
    {'owner_id': 'Willy'}
    >>> source
    {'tan': 123, 'owner_id': 'Willy'}

    In der Quelle nicht vorhandene Schlüssel werden übergangen,
    erzeugen also keinen Fehler:

    >>> extract_dict(['owner_id', 'group_id'], source, pop=0)
    {'owner_id': 'Willy'}
    >>> source
    {'tan': 123, 'owner_id': 'Willy'}

    Mit noempty=True (Standardwert) werden "leere" Werte (wie nach dem
    Absenden von Web-Formularen sehr häufig) weggelassen:

    >>> form={'group_id': 'group_abc', 'status': '', 'zahl': '0'}
    >>> all=['group_id', 'status', 'zahl']
    >>> extract_dict(all, form, pop=1, noempty=1)
    {'group_id': 'group_abc', 'zahl': '0'}

    Diese leeren Werte sind im Falle von pop=True dann trotzdem in der
    Quelle gelöscht:
    >>> form
    {}

    Siehe auch die allgemeinere Funktion visaplan.tools.dicts.subdict
    """
    get = pop and source.pop or source.get
    res = {}
    if noempty:
        for field in fields:
            if field in source:
                val = get(field)
                if val not in (None, ''):
                    res[field] = val
    else:
        for field in fields:
            if field in source:
                res[field] = get(field)
    return res

def make_join(*specs):
    """
    NOCH NICHT IMPLEMENTIERT

    Erzeuge einen explizit formulierten, gut menschenlesbaren Join
    (Verknüpfung über WHERE);  für dynamisches Zusammenbauen, in
    Abhängigkeit davon, welche Informationen in einem Formular konkret
    angegeben wurden, oder zum Prototyping in einer Python-Shell.

    Es werden Objekte (Dictionarys?) mit Tabelleninformationen übergeben,
    die jeweils folgendes enthalten:
    - Name der Tabelle
    - optional: Alias (SELECT ... FROM tan_history h, tan t ...)
    - Liste der zurückzugebenden Felder, jeweils mit optionalem Alias
    - Liste der Verbindungen zu anderen Tabellen
    - Felder, nach denen (auf- oder absteigend) sortiert werden soll.

    Vermutlich ist eine Klasse "Joinable" o.ä. sinnvoll.

    Die Funktion kann evtl. auch "mißbraucht" werden, um eine Query auf
    eine einzelne Tabelle zu erzeugen, die Aliase für die Feldnamen
    erzeugt.
    """


if __name__ == '__main__':
    # Standard library:
    import doctest
    doctest.testmod()

# vim: ts=8 sts=4 sw=4 si et
