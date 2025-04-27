from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
import datetime
from dataclasses import dataclass


@dataclass
class Chapter:
    id: int | None
    id_diploma: int | None
    name: str
    water_content: int
    words: int
    symbols: int
    commonly_used_words: list[str]
    commonly_used_words_amount: list[int]
    chapters: list['Chapter']


@dataclass
class Diploma:
    id: int | None
    name: str
    author: str
    academic_supervisor: str | None  # None, если не получилось извлечь руководителя
    year: int
    words: int
    load_date: datetime
    chapters: list[Chapter]


class Neo4jDatabase:
    def __init__(self, uri, user, password):
        """
        Инициализация соединения с базой данных Neo4j.
        """
        self._driver = None
        try:
            self._driver = GraphDatabase.driver(uri, auth=(user, password))
            # >>> ПРОВЕРКА ДОСТУПНОСТИ БАЗЫ <<<
            with self._driver.session() as session:
                session.run("RETURN 1")  # минимальный запрос
            print("Подключение к базе данных успешно установлено.")
        except ServiceUnavailable as e:
            print(f"Не удалось подключиться к базе данных: {e}")
            raise
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")
            raise

    def close(self):
        """
        Закрытие соединения с базой данных.
        """
        if self._driver:
            try:
                self._driver.close()
                print("Соединение с базой данных успешно закрыто.")
            except Exception as e:
                print(f"Ошибка при закрытии соединения: {e}")

    def query(self, query, parameters=None):
        """
        Выполнение Cypher-запроса.
        :param query: Строка с Cypher-запросом.
        :param parameters: Параметры для запроса (опционально).
        :return: Результат выполнения запроса.
        """
        assert self._driver is not None, "Driver not initialized!"
        session = None
        response = None

        try:
            session = self._driver.session()
            if parameters is None:
                response = list(session.run(query))
            else:
                response = list(session.run(query, parameters))  # <-- сюда передать parameters
            print("Запрос успешно выполнен.")
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
        finally:
            if session is not None:
                session.close()

        return response


class DiplomaRepository:
    def __init__(self, database: Neo4jDatabase):
        self.database = database

    # +
    def save_diploma(self, diploma: Diploma) -> int | None:
        query = """
        CREATE (d:Diploma { 
            name: $name, 
            author: $author, 
            academic_supervisor: $academic_supervisor, 
            year: $year, 
            disclosure_persentage: 0, 
            shingles: ''
        })
        SET d.id = ID(d)
        RETURN d.id
        """
        parameters = {
            "name": diploma.name,
            "author": diploma.author,
            "academic_supervisor": diploma.academic_supervisor,
            "year": diploma.year
        }
        result = self.database.query(query, parameters)
        if result:
            diploma.id = result[0][0]  # Теперь id будет и в объекте, и в БД в поле id
            return diploma.id
        return None

    # +
    def save_chapter(self, chapter: Chapter) -> int | None:
        query = """
        CREATE (c:Chapter {
            id_diploma: $id_diploma, 
            name: $name, 
            water_content: $water_content, 
            words: $words, 
            symbols: $symbols, 
            commonly_used_words: $commonly_used_words, 
            commonly_used_words_amount: $commonly_used_words_amount
        })
        SET c.id = ID(c)
        RETURN ID(c)
        """
        parameters = {
            "id_diploma": chapter.id_diploma,
            "name": chapter.name,
            "water_content": chapter.water_content,
            "words": chapter.words,
            "symbols": chapter.symbols,
            "commonly_used_words": chapter.commonly_used_words,
            "commonly_used_words_amount": chapter.commonly_used_words_amount
        }
        result = self.database.query(query, parameters)
        if result:
            chapter.id = result[0][0]  # Теперь id будет и в объекте, и в БД в поле id
            return chapter.id
        return None

    # +
    def link_chapter_to_diploma(self, id_diploma: int) -> None:
        query = """
        MATCH (d:Diploma), (c:Chapter) 
        WHERE ID(d) = $id_diploma AND c.id_diploma = $id_diploma
        CREATE (d)-[:CONTAINS]->(c)
        """
        parameters = {"id_diploma": id_diploma}
        self.database.query(query, parameters)

    # +
    def link_subchapters(self, parent_chapter_id: int, subchapter_ids: list[int]) -> None:
        query = """
        MATCH (c1:Chapter), (c2:Chapter) 
        WHERE ID(c1) = $parent_chapter_id AND ID(c2) IN $subchapter_ids
        CREATE (c1)-[:CONTAINS]->(c2)
        """
        parameters = {
            "parent_chapter_id": parent_chapter_id,
            "subchapter_ids": subchapter_ids
        }
        self.database.query(query, parameters)

    # idk
    def get_other_diplomas_shingles(self, id_diploma: int) -> list[tuple[int, str]]:
        query = """
        MATCH (d:Diploma)
        WHERE ID(d) <> $id_diploma
        RETURN ID(d), d.shingles
        """
        parameters = {"id_diploma": id_diploma}
        result = self.database.query(query, parameters)
        return [(record[0], record[1]) for record in result]

    # +
    def save_similarity(self, id_diploma: int, id_diploma_2: int, similarity: float) -> None:
        query = """
        MATCH (d1:Diploma), (d2:Diploma)
        WHERE ID(d1) = $id_diploma AND ID(d2) = $id_diploma_2
        CREATE (d1)-[:SIMILAR_TO {similarity: $similarity}]->(d2)
        """
        parameters = {
            "id_diploma": id_diploma,
            "id_diploma_2": id_diploma_2,
            "similarity": similarity
        }
        self.database.query(query, parameters)

    # +
    def load_diploma_graph(self, id_diploma: int) -> tuple[list[int], list[list[int]]]:
        query = """
        MATCH p = (d:Diploma)-[r:CONTAINS*0..]->(x) 
        WHERE ID(d) = $id_diploma
        RETURN 
            COLLECT(DISTINCT ID(x)) AS nodes,
            [r IN COLLECT(DISTINCT LAST(r)) | [ID(startNode(r)), ID(endNode(r))]] AS rels
        """
        parameters = {"id_diploma": id_diploma}
        result = self.database.query(query, parameters)
        nodes, rels = result[0] if result else ([], [])
        return nodes, rels

    # +
    def load_diploma_data(self, id_diploma: int) -> dict:
        query = """
        MATCH (d:Diploma)
        WHERE ID(d) = $id_diploma
        RETURN d
        """
        parameters = {"id_diploma": id_diploma}
        result = self.database.query(query, parameters)
        return dict(result[0]["d"]) if result else {}

    # +
    def load_chapters(self, chapter_ids: list[int]) -> list[dict]:
        query = """
        MATCH (c:Chapter)
        WHERE ID(c) IN $chapter_ids
        RETURN c
        """
        parameters = {"chapter_ids": chapter_ids}
        result = self.database.query(query, parameters)
        return [dict(record["c"]) for record in result] if result else []


# Инициализируем соединение с базой данных Neo4j
neo4j_db = Neo4jDatabase(uri="bolt://localhost:7687", user="neo4j", password="password")

# Создаем репозиторий дипломов
diploma_repository = DiplomaRepository(neo4j_db)

# Пример диплома
test_diploma1 = Diploma(
    id=None,
    name="ОЧЕНЬ ДЛИННОЕ НАЗВАНИЕ ДИПЛОМА 1",
    author="Авторов А.А.",
    academic_supervisor="Научруков А.А.",
    year=2024,
    words=24,
    load_date=datetime.datetime.fromisoformat("2025-04-25T20:01:25.807687"),
    chapters=[
        Chapter(
            id=0,
            id_diploma=1,
            name="ВВЕДЕНИЕ",
            water_content=85,
            words=2,
            symbols=11,
            commonly_used_words=["это", "введение"],
            commonly_used_words_amount=[1, 1],
            chapters=[]
        ),
        Chapter(
            id=1,
            id_diploma=1,
            name="Структура",
            water_content=60,
            words=15,
            symbols=66,
            commonly_used_words=["это", "раздел", "пояснения"],
            commonly_used_words_amount=[2, 1, 1],
            chapters=[
                Chapter(
                    id=3,
                    id_diploma=1,
                    name="Раздел 1",
                    water_content=70,
                    words=5,
                    symbols=16,
                    commonly_used_words=["это", "раздел"],
                    commonly_used_words_amount=[2, 1],
                    chapters=[]
                ),
                Chapter(
                    id=4,
                    id_diploma=1,
                    name="Раздел 2",
                    water_content=50,
                    words=10,
                    symbols=50,
                    commonly_used_words=["это", "пояснения"],
                    commonly_used_words_amount=[2, 1],
                    chapters=[]
                )
            ]
        ),
        Chapter(
            id=2,
            id_diploma=1,
            name="ЗАКЛЮЧЕНИЕ",
            water_content=80,
            words=7,
            symbols=60,
            commonly_used_words=["наконец", "заключение"],
            commonly_used_words_amount=[2, 1],
            chapters=[]
        )
    ]
)

test_diploma2 = Diploma(
    id=None,
    name="ОЧЕНЬ ДЛИННОЕ НАЗВАНИЕ ДИПЛОМА 1",
    author="Авторов А.А.",
    academic_supervisor="Научруков А.А.",
    year=2024,
    words=24,
    load_date=datetime.datetime.fromisoformat("2025-04-25T20:01:25.807687"),
    chapters=[],
)


def testing():

    # Получаем все узлы и связи
    all_data = neo4j_db.query("MATCH (n)-[r]->(m) RETURN n, r, m")

    # Получаем все узлы
    all_nodes = neo4j_db.query("MATCH (n) RETURN n")

    # Получаем все связи
    all_relationships = neo4j_db.query("MATCH ()-[r]->() RETURN r")

    print(all_data, all_nodes, sep='\n---------------\n')
    print('\n\n\n', all_relationships, sep='\n\n')


# Закрываем соединение с базой данных
neo4j_db.close()
