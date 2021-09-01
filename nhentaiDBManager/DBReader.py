import os
import sqlite3
import sys


class DBReader:
    def __init__(self) -> None:
        self.database_location = None
        self.database_filename = None
        filter_option = None
        search_terms = None

    def set_database(
        self,
        database_location=os.path.abspath(__file__),
        database_filename="nhentaiDatabase.db",
    ) -> None:
        self.database_location = database_location
        self.database_filename = database_filename

        if not self.database_location.endswith(".db"):
            self.conn = sqlite3.connect(
                os.path.join(self.database_location, self.database_filename)
            )
            self.cur = self.conn.cursor()
        else:
            self.conn = sqlite3.connect(self.database_location)
            self.cur = self.conn.cursor()

    def sqlite_select(
        self,
        get=None,
        order_by=None,
        order_in="ASC",
        table=None,
        limit=None,
        offset=None,
        filter_option=None,
        search_terms=None,
    ) -> list:
        command = self.get_command(
            get=get,
            order_by=order_by,
            order_in=order_in,
            table=table,
            limit=limit,
            offset=offset,
            filter_option=filter_option,
            search_terms=search_terms,
        )
        return self.execute(command=command, table=table)

    def get_command(
        self, get, order_by, order_in, table, limit, offset, filter_option, search_terms
    ) -> str:
        if filter_option == None and search_terms == None:
            if limit == None and offset == None:
                command = f"""SELECT {get} FROM {table}"""
            else:
                command = f"""SELECT {get} FROM {table} LIMIT {limit} OFFSET {offset}"""
        else:
            try:
                int(search_terms)
            except:
                command = f"""SELECT {get} FROM {table} WHERE {filter_option} LIKE '%{"%".join(search_terms)}%'"""
            else:
                command = f"""SELECT {get} FROM {table} WHERE {filter_option} = '{search_terms}'"""
            if order_by != None and order_in != None:
                command += f" ORDER BY {order_by} {order_in}"
            if limit != None and offset != None:
                command += f" LIMIT {limit} OFFSET {offset}"
        return command

    def execute(self, command, table) -> list:
        try:
            self.cur.execute(command)
        except sqlite3.OperationalError as e:
            if "no such table" in e.args[0]:
                pass
            else:
                error_msg = f"Error reading FROM {table}:\n{' '.join(e.args)}"
                sys.exit(error_msg)
        results = [result for result in self.cur.fetchall()]
        return results
