import os
import sqlite3
import csv
import re
import sys

class nhentaiDBWriter:
    class nhentaiLibrary:
        def set_database(self, database_location,  metadata_location, database_filename='nhentaiDatabase.db'):
            self.database_location = database_location
            self.metadata_location = metadata_location
            self.database_filename = database_filename

            if not self.database_location.endswith('.db'):
                self.conn = sqlite3.connect(os.path.join(self.database_location, self.database_filename))
                self.c = self.conn.cursor()
            else:
                self.conn = sqlite3.connect(self.database_location)
                self.c = self.conn.cursor()
            for root, dirs, files in os.walk(self.metadata_location):
                self.data_dict = list()
                for file in files:
                    if file.startswith('metadata.csv'):
                        with open(os.path.join(root, file), encoding='utf-8') as csv_file:
                            csv_file = csv.DictReader(csv_file, delimiter=':')
                            self.data_dict.append({col['tag']:col['tag_values'] for col in csv_file})
                self.create_database()
                for item in self.data_dict:
                    self.update_database(item, root)

        def create_database(self):
            self.c.execute(""" CREATE TABLE IF NOT EXISTS nhentaiLibrary (
                        ids INTEGER UNIQUE,
                        titles TEXT,
                        artists TEXT,
                        groups TEXT,
                        parodies TEXT,
                        characters TEXT,
                        languages TEXT,
                        categories TEXT,
                        pages INTEGER,
                        upload_date TEXT,
                        tags TEXT,
                        location TEXT
                        )""")
            self.conn.commit()

        def update_database(self, item, root):
            c = self.conn.cursor()
            with self.conn:
                tags = re.sub("'", '', item['tags'])
                tags = re.sub('\[', '', tags)
                tags = re.sub('\]', '', tags)

                artists = re.sub("'", '', item['artists'])
                artists = re.sub('\[', '', artists)
                artists = re.sub('\]', '', artists)

                groups= re.sub("'", '', item['groups'])
                groups= re.sub('\[', '', groups)
                groups= re.sub('\]', '', groups)

                parodies= re.sub("'", '', item['parodies'])
                parodies= re.sub('\[', '', parodies)
                parodies= re.sub('\]', '', parodies)

                characters= re.sub("'", '', item['characters'])
                characters= re.sub('\[', '', characters)
                characters= re.sub('\]', '', characters)

                languages= re.sub("'", '', item['languages'])
                languages= re.sub('\[', '', languages)
                languages= re.sub('\]', '', languages)

                categories= re.sub("'", '', item['categories'])
                categories= re.sub('\[', '', categories)
                categories= re.sub('\]', '', categories)

                try:
                    c.execute("""INSERT INTO nhentaiLibrary (ids, titles, artists, groups, parodies, characters, languages, categories, pages, upload_date, tags, location)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (int(item['code']), item['title'], artists, groups, parodies, characters, languages, categories, item['pages'], item['upload date'],tags, root))
                except BaseException as e:
                    if 'UNIQUE constraint failed' in ' '.join(e.args):
                        pass
                    else:
                        error_msg = f"Error writing {item['title']} to nhentaiLibrary:\n{' '.join(e.args)}"
                        sys.exit(error_msg)
            self.conn.commit()


    class DownloadedAndDuplicates:
        """
        The table is for storing codes that were deemed to have had duplicates.
        Contains two columns, one to store the actual downloaded codes and other to store the codes deemed as duplicates of downloaded code.
        """
        def set_database(self, database_location, database_filename='nhentaiDatabase.db'):
            self.database_location = database_location
            self.database_filename = database_filename
            if not self.database_location.endswith('.db'):
                self.conn = sqlite3.connect(os.path.join(self.database_location, self.database_filename))
                self.c = self.conn.cursor()
            else:
                self.conn = sqlite3.connect(self.database_location)
                self.c = self.conn.cursor()

        def update_database(self, downloaded_code, duplicate_codes):
            self.c.execute(""" CREATE TABLE IF NOT EXISTS duplicates (
                        downloaded_id INTEGER,
                        duplicate_id INTEGER UNIQUE
                        )""")
            self.conn.commit()
            c = self.conn.cursor()
            with self.conn:
                for duplicate_code in duplicate_codes:
                    try:
                        c.execute(f"""INSERT INTO duplicates (downloaded_id, duplicate_id) VALUES (?, ?)""", (int(downloaded_code), int(duplicate_code)))
                    except BaseException as e:
                        if 'UNIQUE constraint failed' in ' '.join(e.args):
                            pass
                        else:
                            error_msg = f"Error writing to duplicates:\n{' '.join(e.args)}"
                            sys.exit(error_msg)
            self.conn.commit()

    class FilteredCollections:
        """
        The table is for storing Comics, anthologies, etc codes.
        Contains one column for storing the code.
        """
        def set_database(self, database_location, database_filename='nhentaiDatabase.db'):
            self.database_location = database_location
            self.database_filename = database_filename
            if not self.database_location.endswith('.db'):
                self.conn = sqlite3.connect(os.path.join(self.database_location, self.database_filename))
                self.c = self.conn.cursor()
            else:
                self.conn = sqlite3.connect(self.database_location)
                self.c = self.conn.cursor()

        def update_database(self, collection_codes):
            self.c.execute(""" CREATE TABLE IF NOT EXISTS collections (
                        collection_id INTEGER UNIQUE
                        )""")
            self.conn.commit()
            c = self.conn.cursor()
            with self.conn:
                for collection_code in collection_codes:
                    try:
                        c.execute(f"""INSERT INTO collections (collection_id) VALUES ({int(collection_code)})""")
                    except BaseException as e:
                        if 'UNIQUE constraint failed' in ' '.join(e.args):
                            pass
                        else:
                            error_msg = f"Error writing to collections:\n{' '.join(e.args)}"
                            sys.exit(error_msg)
            self.conn.commit()


class nhentaiDBBrowser:
    def __init__(self):
        self.database_location = None
        self.database_filename = None
        filter_option = None
        search_terms = None

    def set_database(self, database_location=os.path.abspath(__file__), database_filename='nhentaiDatabase.db'):
        self.database_location = database_location
        self.database_filename = database_filename

        if not self.database_location.endswith('.db'):
            self.conn = sqlite3.connect(os.path.join(self.database_location, self.database_filename))
            self.cur = self.conn.cursor()
        else:
            self.conn = sqlite3.connect(self.database_location)
            self.cur = self.conn.cursor()

    def sqlite_select(self, get=None, order_by=None, order_in='ASC', table=None, limit=None, offset=None, filter_option=None, search_terms=None):
        command = self.get_command(get=get, order_by=order_by, order_in=order_in, table=table, limit=limit, offset=offset, filter_option=filter_option, search_terms=search_terms)
        return self.execute(command=command, table=table)

    def get_command(self, get, order_by, order_in, table, limit, offset, filter_option, search_terms):
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
                command +=  f' ORDER BY {order_by} {order_in}'
            if limit != None and offset != None:
                command +=  f' LIMIT {limit} OFFSET {offset}'
        return command

    def execute(self, command, table):
        try:
            self.cur.execute(command)
        except sqlite3.OperationalError as e:
            if 'no such table' in e.args[0]:
                pass
            else:
                error_msg = f"Error reading FROM {table}:\n{' '.join(e.args)}"
                sys.exit(error_msg)
        results = [result for result in self.cur.fetchall()]
        return results
