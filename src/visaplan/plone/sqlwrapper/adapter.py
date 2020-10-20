# -*- coding: utf-8 -*- äöü vim: ts=8 sts=4 sw=4 si et tw=79
"""
Adapter sqlwrapper: Schnittstelle zur SQL-Datenbank
"""
# Python compatibility:
from __future__ import absolute_import

from six.moves import range

# Zope:
from App.config import getConfiguration
from Products.CMFCore.utils import getToolByName

# 3rd party:
from exceptions import NotImplementedError

# visaplan:
from visaplan.plone.base import Base

# Logging / Debugging:
from visaplan.plone.tools.log import getLogSupport

logger, debug_active, DEBUG = getLogSupport(fn=__file__,
                                            defaultFromDevMode=False)
# Local imports:
from .interfaces import ISQLWrapper
from .utils import (
    check_name,
    generate_dicts,
    make_returning_clause,
    make_transaction_cmd,
    make_where_mask,
    replace_names,
    )


class Adapter(Base):
    """Klasse für Standard-SQL-Befehle."""

    def __init__(self, context, *args):
        """
        context -- von getAdapter übergeben

        **args -- Spezifikation für den SQL-Befehl 'BEGIN TRANSACTION' (optional).
        """
        conf = getConfiguration()
        env = conf.environment
        portal = getToolByName(context, 'portal_url').getPortalObject()
        try:
            db_name = env['DATABASE']
            self.db = getattr(portal, db_name)._v_database_connection
        except KeyError as e:
            logger.error('!!! Keine Datenbank konfiguriert! (%(e)r)', locals())
            raise
        except AttributeError as e:
            logger.error('!!! Datenbank-Adapter %(db_name)r nicht gefunden! (%(e)r)', locals())
            raise
        else:
            self._transaction_level = 0
            self._begin_transaction_tup = args

    def __enter__(self):
        """
        Betritt den Transaktionskontext und gib den Adapter zurück.

        Verwendung:

          with context.getAdapter('sqlwrapper') as sql:
              sql.insert(...)
              ...

        """
        new_transaction = self._transaction_level == 0
        self._transaction_level += 1
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Verlasse den Transaktionskontext; wenn keine Fehler aufgetreten sind,
        sichere die Änderungen.
        """
        assert self._transaction_level >= 1
        self._transaction_level -= 1

    def __call__(self, *args):
        """
        Hier können Details für die Transaktion angegeben werden, wie z. B.
        "read only"; wirksam werden diese aber nur, wenn der Adapter mit
        "with" verwendet wird (siehe die Dokumentation zur __enter__-Methode).
        """
        self._begin_transaction_tup = args
        return self

    def _execute(self, query, query_data={}, commit=None):
        """
        Führe das übergebene SQL-Statement aus.
        Wenn in einer Transaktion, wird kein COMMIT ausgeführt,
        da dieses bei Verlassen des Transaktionskontexts automatisch geschieht.
        """
        raise NotImplemented

    def transaction_mode(self, *args):
        """
        Setze den Modus der Transaktion.
        Funktioniert nur direkt zu Beginn!

        ... und knallt seltsamerweise in der GKZ-Instanz!
        """
        cmd = make_transaction_cmd('SET', *args)

    def insert(self, table, dict_of_values,  # -------- [ insert ... [
               returning=None, commit=None, transform=None):
        """
        Speichere die Werte aus dem Dictionary in die Tabelle.
        Keys aus dem Dictionary müssen mit den Tabellenfeldern
        übereinstimmen.
        Es werden nur Werte für eine Zeile akzeptiert.

        table -- Name der Tabelle
        dict_of_values -- dict {Feldname: Wert}
        returning -- z. B. 'id'; PostgreSQL 9.1+
        commit -- soll dem SQL-Befehl ein COMMIT; angehängt werden?
        transform -- ignoriert; nicht mehr verwenden
        """
        keys = list(dict_of_values.keys())
        rows = ', '.join(keys)
        values = ', '.join([key.join(('%(', ')s'))
                            for key in keys
                            ])
        query_l = [replace_names('INSERT INTO %(table)s',
                                 table=table),
                   '(%s)' % rows,
                   'VALUES (%s)' % values,
                   ]
        if returning:
            query_l.append(make_returning_clause(returning))
        if commit is None:
            commit = not self._transaction_level
        statements = [' '.join(query_l)]
        if commit:
            statements.append('COMMIT')
        statements.append('')
        query = ';'.join(statements)
        DEBUG('insert:\n   query=%r\n   query_data=%r', query, dict_of_values)
        res = self.db.query(query, query_data=dict_of_values)
        if returning:
            return generate_dicts(res, names=returning)
        # --------------------------------------------- ] ... insert ]

    def insert_many(self, table, seq_of_dicts,
                    returning=None, commit=None):
        """
        Speichere die Werte aus dem Dictionary in die Tabelle.
        Keys aus dem Dictionary müssen mit den Tabellenfeldern
        übereinstimmen.
        Es werden nur Werte für eine Zeile akzeptiert.

        table -- Name der Tabelle
        seq_of_dicts -- [dict {Feldname: Wert}]. Die Schlüssel des
                        ersten Elements bzw. des defaults-Dictionarys
                        bestimmen die Feldnamen; weitere Feldnamen in
                        weiteren Elementen erzeugen Warnungen
        returning -- z. B. 'id'; PostgreSQL 9.1+
        commit -- soll dem SQL-Befehl ein COMMIT; angehängt werden?
        """
        raise NotImplemented
        keys = list(dict_of_values.keys())
        rows = ', '.join(keys)
        values = ', '.join([key.join(('%(', ')s'))
                            for key in keys
                            ])
        query_l = [replace_names('INSERT INTO %(table)s',
                                 table=table),
                   '(%s)' % rows,
                   'VALUES (%s)' % values,
                   ]
        if returning:
            query_l.append(make_returning_clause(returning))
        if (commit is None
            and (0 and 'transaction_level: GKZ-Problem, Rev. 13395')
            ):
            commit = not self._transaction_level
        statements = [' '.join(query_l)]
        if commit:
            statements.append('COMMIT')
        statements.append('')
        query = ';'.join(statements)
        DEBUG('insert:\n   query=%r\n   query_data=%r', query, dict_of_values)
        res = self.db.query(query, query_data=dict_of_values)
        if returning:
            return generate_dicts(res, names=returning)
        return res

    def update(self, table, dict_of_values,  # -------- [ update ... [
               where=None, query_data={},
               returning=None,
               commit=None,
               fork=True):
        """
        Pflichtargumente:
          table - die betroffene Tabelle
          dict_of_values -- neu zu setzende Werte

        Optional:
          where -- vollst. WHERE-Statement (incl. WHERE-Schlüsselwort)
                   mit %(name)s-Platzhaltern
          query_data -- dict mit weiteren Werten (für das WHERE-Kriterium).
                        ACHTUNG - wird für die Übergabe an
                        den Datenbank-Adapter modifiziert!
          returning -- wenn angegeben, eine Sequenz von Feldnamen,
                       oder '*';
                       es werden dann entsprechende Dictionarys für
                       jede geänderte Zeile generiert.
                       Beim UPDATE-Befehl werden die Werte
                       *nach Änderung* zurückgegeben.
          commit -- zum expliziten Erzwingen oder Unterdrücken eines
                    anschließenden COMMITs.
                    Bei Verwendung des Context-Manager-Protokolls ("with
                    ... as sql:"; empfohlen) unnötig, weil das COMMIT
                    beim Verlassen des Kontexts automatisch abgesetzt
                    wird.

          fork -- wenn <query_data> nach dem Methodenaufruf noch verwendet
                  werden soll, muß intern eine Kopie angelegt werden

        Achtung: Die Kombination aus <returning> und einem ausgeführten
        <commit> ist nicht getestet; <returning> wird daher am besten
        mit dem Kontext-Manager-Protokoll verwendet!
        """
        keys = list(dict_of_values.keys())
        qset = ', '.join([''.join((key, '=%(', key, ')s'))
                          for key in keys
                          ])
        query_l = [replace_names('UPDATE %(table)s SET',
                                 table=table),
                   qset,
                   ]
        if query_data:
            query_keys = set(query_data.keys())
            value_keys = set(keys)
            keys_of_both = value_keys.intersection(query_keys)
            if keys_of_both:
                # Löschen aus Set während Iteration nicht erlaubt;
                # also iteration über "Kopie":
                for key in sorted(keys_of_both):
                    u_val = dict_of_values[key]
                    q_val = query_data[key]
                    if u_val == q_val:
                        del dict_of_values[key]
                        keys_of_both.remove(key)
                    else:
                        logger.error('update: key %(key)r is both'
                                     ' in query data (%(q_val)r)'
                                     ' and update data (%(u_val)r)!',
                                     locals())
            if not dict_of_values:
                raise ValueError('Empty update data!')
            if keys_of_both:
                logger.error('update: value_keys = %(value_keys)s,'
                             ' query_keys = %(query_keys)s,'
                             ' intersection = %(keys_of_both)s'
                             , locals())
                raise ValueError('intersection of value keys and '
                                 'query keys (%(keys_of_both)s: '
                                 'currently unsupported!'
                                 % locals())
        if query_data and not where:
            where = make_where_mask(query_data)
        if where:
            query_l.append(where)

        if returning:
            query_l.append(make_returning_clause(returning))
        if commit is None:
            commit = not self._transaction_level
        queries = [' '.join(query_l)+';']
        if commit:
            queries.append('COMMIT;')
        query = ''.join(queries)
        # nicht alle "Query-Daten" dienen der Filterung (siehe oben, keys_of_both)
        if fork:
            query_data = dict(query_data)  # wg. Wiederverwendung!
        query_data.update(dict_of_values)
        DEBUG('update:\n   query=%r\n   query_data=%r', query, query_data)
        res = self.db.query(query, query_data=query_data)
        if returning:
            return generate_dicts(res, names=returning)
        return res
        # --------------------------------------------- ] ... update ]

    def delete(self, table,  # ------------------------ [ delete ... [
               where=None, query_data=None,
               returning=None,
               commit=None):
        """
        Lösche Werte aus einer einzelnen Tabelle der SQL-Datenbank.

        table -- Name der Tabelle oder Sicht
        where -- ein vorformuliertes WHERE-Kriterium, mit Platzhaltern
                 für die Werte (Python-Dictionary-Syntax);
                 ggf. aus <query_data> generiert
        query_data -- ein Dictionary mit den Abfragedaten
        returning -- wenn angegeben, eine Sequenz von Feldnamen,
                     oder '*';
                     es werden dann entsprechende Dictionarys für
                     jede gelöschte Zeile generiert.
        commit -- zum expliziten Erzwingen oder Unterdrücken eines
                  anschließenden COMMITs.
                  Bei Verwendung des Context-Manager-Protokolls ("with
                  ... as sql:"; empfohlen) unnötig, weil das COMMIT
                  beim Verlassen des Kontexts automatisch abgesetzt
                  wird.

        Achtung: ohne WHERE-Kriterium (als <where> und/oder <query_data>
                 wird die Tabelle vollständig geleert!
        """
        query_l = [replace_names('DELETE FROM %(table)s',
                                 table=table),
                   ]
        if query_data and not where:
            where = make_where_mask(query_data)
        if where:
            query_l.append(where)
        if returning:
            query_l.append(make_returning_clause(returning))
        if commit is None:
            commit = not self._transaction_level
        queries = [' '.join(query_l)+';']
        if commit:
            queries.append('COMMIT;')
        query = ''.join(queries)
        DEBUG('delete:\n   query=%r\n   query_data=%r', query, query_data)
        res = self.db.query(query, query_data=query_data)
        if returning:
            return generate_dicts(res, names=returning)
        return res
        # --------------------------------------------- ] ... delete ]

    def select(self, table,  # ------------------------ [ select ... [
               fields=None, where=None,
               query_data=None, maxrows=None):
        """
        Hole Werte aus einer einzelnen Tabelle oder Sicht der SQL-Datenbank.

        table -- Name der Tabelle oder Sicht
        fields -- Namen der Felder (optional; Standardwert: '*')
        where -- ein vorformuliertes WHERE-Kriterium, mit Platzhaltern
                 für die Werte (Python-Dictionary-Syntax);
                 ggf. aus <query_data> generiert
        query_data -- ein Dictionary mit den Abfragedaten
        maxrows - weitergereicht an self.db.query
        """

        if where is None and query_data:
            where = make_where_mask(query_data, fields)
        if fields is None:
            fields = '*'
        elif fields == '*':
            pass
        elif fields:
            liz = []
            for field in fields:
                check_name(field)
                liz.append(field)
            fields = ', '.join(liz)
        else:
            fields = '*'
        query_l = ['SELECT',
                   fields,
                   replace_names('FROM %(table)s', table=table),
                   ]
        if where:
            query_l.append(where)
        query = ' '.join(query_l) + ';'
        DEBUG('select:\n   query=%r\n   maxrows=%r\n   query_data=%r',
              query, maxrows, query_data)

        queryResult = self.db.query(query, maxrows, query_data)
        result = []
        if not queryResult[1]:
            return []
        for row in queryResult[1]:
            res = {}
            for i in range(len(row)):
                value = row[i]
                name = queryResult[0][i]['name']
                res[name] = value
            result.append(res)
        return result
        # --------------------------------------------- ] ... select ]

    def query(self, query,  # -------------------------- [ query ... [
              names={}, query_data=None, maxrows=None):
        """
        query - Eine Datenbankabfrage mit Platzhaltern für Namen und Daten
        query_data - für Daten
        names - die Namen, z. B. von Tabellen (ein dict)
        """
        q = replace_names(query, **names)
        DEBUG('query:\n   query=%r\n   maxrows=%r\n   query_data=%r',
              q, maxrows, query_data)
        queryResult = self.db.query(q, maxrows, query_data)
        result = []
        if not queryResult[1]:
            return result
        for row in queryResult[1]:
            res = {}
            for i in range(len(row)):
                value = row[i]
                name = queryResult[0][i]['name']
                res[name] = value
            result.append(res)
        return result
        # ---------------------------------------------- ] ... query ]

    def getFields(self, table):
        """
            Holt alle Spaltennamen aus angegebener Tabelle
        """
        raise NotImplementedError

    def getColumns(self, table):
        """
            Holt alle Spalten mit Beschreibung aus der angegebenen Tabelle
        """
        raise NotImplementedError

    def _getFieldtype_(self, field):
        """ gibt den Feldtypen des Feldes zurück """
        raise NotImplementedError

    @staticmethod
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

        Als statische Methode hier nur noch auf Verdacht;
        in Python-Code kann direkt die Funktion aus dem utils-Modul verwendet
        werden.
        """
        return replace_names(sql, **kwargs)
