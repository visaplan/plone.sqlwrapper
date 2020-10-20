# -*- coding: utf-8 -*- äöü
"""
qfactory-Modul des Adapters unitracc->sqlwrapper: "Query factory";
Funktionen zur Generierung von SQL-Statements.

Die Funktionen nehmen zwar die Dictionarys entgegen, die die einzufügenden oder
zu vergleichenden Werte enthalten; sie verwenden sie aber nur zur Ermittlung
der Namen und überlassen die Ersetzung dem Datenbank-Adapter.

Autor: Tobias Herp
"""

__all__ = [# Funktionen:
           # 'insert',
           ]

DEBUG = 1
if __name__ == '__main__':
    DEBUG = 0   # würde bei Doctests stören

def beautify_sql(s):
    """
    Einfache mehrzeilige Formatierung von SQL-Statements

    >x> beautify_sql('INSERT INTO tabelle (eins, zwei) VALUES (%(eins)s, %(zwei)s) RETURNING eins;')
    '''INSERT INTO tabelle (eins, zwei)
         VALUES (%(eins)s, %(zwei)s)
      RETURNING eins;'''

    Es wird einfach davon ausgegangen, daß SQL-Schlüsselwörter GROSSGESCHRIEBEN
    sind und Sequenzen aufeinanderfolgender Schlüsselwörter zusammengehören.
    Für die hier zu generierenden Statements ist das gut genug.
    """
    liz = s.split()
    prevKW = False
    lines = []
    for item in liz:
        pass

def pretty_resulting_sql_statement(func):
    """
    Dekorator für Debugging: Gib jedes generierte SQL-Statement aus
    (ohne Werte, aber hübsch formatiert)
    """
    def f(*args, **kwargs):
        res = func(*args, **kwargs)
        print beautify_sql(res)
        return res
    return f

def unchanged(func):
    return func

if DEBUG:
    decorate = pretty_resulting_sql_statement
else:
    decorate = unchanged

@decorate
def select(table, fields=None, where=None, query_data=None):
    """
    Generiere ein SELECT-Statement (ohne Ersetzung der Werte)

    >>> query_data={'eins': 1, 'zwei': 2}
    >>> select('tabelle', query_data=query_data)
    'SELECT * FROM tabelle WHERE eins = %(eins)s AND zwei = %(zwei)s;'
    """

@decorate
def insert(table, dict_of_values,
           returning=None):
    """
    Generiere ein INSERT-Statement (ohne Ersetzung der Werte)

    >>> query_data={'eins': 1, 'zwei': 2}
    >>> insert('tabelle', query_data)
    'INSERT INTO tabelle (eins, zwei) VALUES (%(eins)s, %(zwei)s);'
    >>> insert('tabelle', query_data, returning='eins')
    'INSERT INTO tabelle (eins, zwei) VALUES (%(eins)s, %(zwei)s) RETURNING eins;'
    """

@decorate
def update(table, dict_of_values, where=None, query_data={}):
    """
    Generiere ein UPDATE-Statement (ohne Ersetzung der Werte)

    >>> dict_of_values={'eins': 1, 'zwei': 2}
    >>> query_data={'id': 42}
    >>> update('tabelle', dict_of_values, query_data=query_data)
    'UPDATE tabelle SET eins=%(eins)s, zwei=%(zwei)s WHERE id = %(id)s;'
    """

@decorate
def delete(table, where=None, query_data=None):
    """
    Generiere ein DELETE-Statement (ohne Ersetzung der Werte)

    >>> query_data={'id': 42}
    >>> delete('tabelle', query_data=query_data)
    'DELETE FROM tabelle WHERE id = %(id)s;'
    """

if __name__ == '__main__':
    import doctest
    doctest.testmod()

# vim: ts=8 sts=4 sw=4 si et
