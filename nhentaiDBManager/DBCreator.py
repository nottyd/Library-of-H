import os
import sqlite3
import sys

DBCreator:
    def create_database(self) -> None:
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

    def set_database(self, database_location,  metadata_location, database_filename='nhentaiDatabase.db') -> None:
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

    def update_database(self, item, root) -> None:
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