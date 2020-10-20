# -*- coding: utf-8 -*- äöü vim: ts=8 sts=4 sw=4 si et tw=79
# Python compatibility:
from __future__ import absolute_import

# Zope:
from zope.interface import Interface


class ISQLWrapper(Interface):

    """Interface für Standard-SQL-Befehle."""

    def insert(table, dict_of_values,
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

    def update(table, dict_of_values, where=None, query_data={},
               returning=None,
               commit=None):
        """
            Macht ein Update auf eine Tabelle.
            Schmeißt fehler zurück.
        """

    def delete(table, where=None, query_data=None,
               returning=None,
               commit=None):
        """
            Löscht Eintr(ä)ag(e) aus der Datenbank.
            Ohne Id oder WHERE-Clause werden alle Inhalte gelöscht.
        """

    def select(table, fields=None, where=None,
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
