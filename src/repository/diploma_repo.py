from collections import defaultdict
from datetime import datetime

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

from src.diploma_processing.data_types import *


class Neo4jDatabase:
    def __init__(self, host='bolt://localhost', user='neo4j', password='password'):
        """
        Инициализация соединения с базой данных Neo4j.
        """
        self._driver = None
        try:
            self._driver = GraphDatabase.driver(f"{host}:7687", auth=(user, password))
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

    def save_diploma(self, diploma: Diploma) -> int | None:
        query = """
        CREATE (d:Diploma { 
            name: $name, 
            author: $author, 
            academic_supervisor: $academic_supervisor, 
            year: $year, 
            words: $words,
            load_date: $load_date
        })
        SET d.id = ID(d)
        RETURN d.id
        """
        parameters = {
            "name": diploma.name,
            "author": diploma.author,
            "academic_supervisor": diploma.academic_supervisor,
            "year": diploma.year,
            "words": diploma.words,
            "load_date": diploma.load_date.date()
        }
        result = self.database.query(query, parameters)

        if result:
            id_diploma = result[0][0]

            ids = []
            for chapter in diploma.chapters:
                chapter.id_diploma = id_diploma
                ids.append(self._save_chapter(chapter))
            if len(ids) > 0:
                self._link_subchapters(id_diploma, ids)

            return id_diploma
        return None

    def _save_chapter(self, chapter: Chapter) -> int | None:
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
        RETURN c.id
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
            id_chapter = result[0][0]

            ids = []
            for subchapter in chapter.chapters:
                subchapter.id_diploma = chapter.id_diploma
                chapter_id = self._save_chapter(subchapter)
                ids.append(chapter_id)
            if len(ids) > 0:
                self._link_subchapters(id_chapter, ids)

            return id_chapter
        return None

    def _link_subchapters(self, parent_chapter_id: int, subchapter_ids: list[int]) -> None:
        query = """
        MATCH (c), (c2:Chapter) 
        WHERE c.id = $parent_chapter_id AND c2.id IN $subchapter_ids
        CREATE (c)-[:CONTAINS]->(c2)
        """
        parameters = {
            "parent_chapter_id": parent_chapter_id,
            "subchapter_ids": subchapter_ids
        }
        self.database.query(query, parameters)

    def get_other_diplomas_shingles(self, id_diploma: int) -> list[tuple[int, list[int]]]:
        query = """
        MATCH (d:Diploma)
        WHERE d.id <> $id_diploma
        RETURN d.id, d.shingles
        """
        parameters = {"id_diploma": id_diploma}
        result = self.database.query(query, parameters)
        return [(int(record[0]), list(map(int, record[1]))) for record in result]

    def save_similarity(self, id_diploma: int, id_diploma_2: int, similarity: float) -> None:
        query = """
        MATCH (d1:Diploma), (d2:Diploma)
        WHERE d1.id = $id_diploma AND d2.id = $id_diploma_2
        CREATE (d1)-[:SIMILAR_TO {similarity: $similarity}]->(d2)
        """
        parameters = {
            "id_diploma": id_diploma,
            "id_diploma_2": id_diploma_2,
            "similarity": similarity
        }
        self.database.query(query, parameters)

    def load_diploma_data(self, id_diploma: int) -> Diploma | None:
        query = """
        MATCH (d:Diploma)
        WHERE d.id = $id_diploma
        RETURN d
        """
        parameters = {"id_diploma": id_diploma}
        result = self.database.query(query, parameters)

        if not result:
            return None

        node = result[0]["d"]

        diploma = Diploma(
            id=node.get("id"),
            name=node.get("name", ""),
            author=node.get("author", ""),
            academic_supervisor=node.get("academic_supervisor"),
            year=node.get("year", 0),
            words=node.get("words", 0),
            load_date=datetime.datetime(
                node.get("load_date").year,
                node.get("load_date").month,
                node.get("load_date").day),
            chapters=[]
        )

        rels = self._load_diploma_graph(id_diploma)
        chapters = self._load_chapters(id_diploma)
        graph = defaultdict(list)
        chapters_dict = {}
        for chapter in chapters:
            chapters_dict[chapter.id] = chapter
        for rel in rels:
            graph[rel[0]].append(rel[1])
        for key in graph:
            graph[key] = sorted(graph[key])
        diploma.chapters = [chapters_dict[x] for x in graph[diploma.id]]
        for chapter in chapters:
            chapter.chapters = [chapters_dict[x] for x in graph[chapter.id]]

        return diploma

    def _load_chapters(self, id_diploma: int) -> list[Chapter]:
        query = """
        MATCH (c:Chapter)
        WHERE c.id_diploma = $id_diploma
        RETURN c
        """
        parameters = {"id_diploma": id_diploma}
        result = self.database.query(query, parameters)

        chapters = []
        for record in result:
            node = record["c"]

            chapter = Chapter(
                id=node.get("id"),
                id_diploma=node.get("id_diploma"),
                name=node.get("name", ""),
                water_content=node.get("water_content", 0),
                words=node.get("words", 0),
                symbols=node.get("symbols", 0),
                commonly_used_words=node.get("commonly_used_words", []),
                commonly_used_words_amount=node.get("commonly_used_words_amount", []),
                chapters=[]
            )
            chapters.append(chapter)

        return chapters

    def _load_diploma_graph(self, id_diploma: int) -> list[list[int]]:
        query = """
        MATCH p = (d:Diploma)-[r:CONTAINS*]->(x) 
        WHERE d.id = $id_diploma
        RETURN [r IN COLLECT(DISTINCT LAST(r)) | [startNode(r).id, endNode(r).id]] AS rels
        """
        parameters = {"id_diploma": id_diploma}
        result = self.database.query(query, parameters)
        rels = result[0][0] if result else []
        return rels

    def search_diplomas(self,
                        min_id: int = None, max_id: int = None,
                        name: str = None, author: str = None, academic_supervisor: str = None,
                        min_year: int = None, max_year: int = None,
                        min_words: int = None, max_words: int = None,
                        min_date: str = None, max_date: str = None,
                        chapters: list[int] = None,
                        order_by: str = None) -> list[Diploma]:
        query = """
        MATCH (d:Diploma)-[:CONTAINS]->(c:Chapter)
        WITH d, COLLECT(c.id) AS chapters
        WHERE ($min_id IS NULL OR d.id >= $min_id)
          AND ($max_id IS NULL OR d.id <= $max_id)
          AND ($name IS NULL OR toLower(d.name) CONTAINS toLower($name))
          AND ($author IS NULL OR toLower(d.author) CONTAINS toLower($author))
          AND ($academic_supervisor IS NULL OR toLower(d.academic_supervisor) CONTAINS toLower($academic_supervisor))
          AND ($min_year IS NULL OR d.year >= $min_year)
          AND ($max_year IS NULL OR d.year <= $max_year)
          AND ($min_words IS NULL OR d.words >= $min_words)
          AND ($max_words IS NULL OR d.words <= $max_words)
          AND ($min_date IS NULL OR d.load_date >= Date($min_date))
          AND ($max_date IS NULL OR d.load_date <= Date($max_date))
          AND ($chapters IS NULL OR ANY(chapter IN $chapters WHERE chapter IN chapters))
        """
        if order_by:
            query += f"\nORDER BY d.{order_by}"

        query += "\nRETURN d{.*, chapters: chapters} AS diploma"

        parameters = {
            "min_id": min_id, "max_id": max_id,
            "name": name, "author": author, "academic_supervisor": academic_supervisor,
            "min_year": min_year, "max_year": max_year,
            "min_words": min_words, "max_words": max_words,
            "min_date": min_date, "max_date": max_date,
            "chapters": chapters
        }
        result = self.database.query(query, parameters)

        diplomas = []
        for record in map(lambda x: x["diploma"], result):
            diploma = Diploma(
                id=record.get("id"),
                name=record.get("name", ""),
                author=record.get("author", ""),
                academic_supervisor=record.get("academic_supervisor"),
                year=record.get("year", 0),
                words=record.get("words", 0),
                load_date=datetime.datetime(
                    record.get("load_date").year,
                    record.get("load_date").month,
                    record.get("load_date").day),
                chapters=record.get("chapters", [])
            )
            diplomas.append(diploma)
        return diplomas

    def search_chapters(self,
                        min_id: int = None, max_id: int = None,
                        min_id_diploma: int = None, max_id_diploma: int = None,
                        name: str = None,
                        min_words: int = None, max_words: int = None,
                        min_symbols: int = None, max_symbols: int = None,
                        min_water_content: float = None, max_water_content: float = None,
                        words: list[str] = None,
                        chapters: list[int] = None,
                        order_by: str = None) -> list[Chapter]:
        query = """
        MATCH (c:Chapter)-[:CONTAINS*0..1]->(c1:Chapter)
        WITH c, COLLECT(c1.id) AS chapters
        WHERE ($min_id IS NULL OR c.id >= $min_id)
          AND ($max_id IS NULL OR c.id <= $max_id)
          AND ($min_id_diploma IS NULL OR c.id_diploma >= $min_id_diploma)
          AND ($max_id_diploma IS NULL OR c.id_diploma <= $max_id_diploma)
          AND ($name IS NULL OR toLower(c.name) CONTAINS toLower($name))
          AND ($min_words IS NULL OR c.words >= $min_words)
          AND ($max_words IS NULL OR c.words <= $max_words)
          AND ($min_symbols IS NULL OR c.symbols >= $min_symbols)
          AND ($max_symbols IS NULL OR c.symbols <= $max_symbols)
          AND ($min_water_content IS NULL OR c.water_content >= $min_water_content)
          AND ($max_water_content IS NULL OR c.water_content <= $max_water_content)
          AND ($words IS NULL OR ANY(word IN $words WHERE 
            ANY(com_word IN c.commonly_used_words WHERE toLower(com_word) CONTAINS toLower(word))
          ))
          AND ($chapters IS NULL OR ANY(chapter IN $chapters WHERE chapter IN chapters))
        """
        if order_by:
            query += f"\nORDER BY c.{order_by}"

        query += "\nRETURN c{.*, chapters: [id in chapters WHERE id <> c.id]} AS chapter"

        parameters = {
            "min_id": min_id, "max_id": max_id,
            "min_id_diploma": min_id_diploma, "max_id_diploma": max_id_diploma,
            "name": name,
            "min_words": min_words, "max_words": max_words,
            "min_symbols": min_symbols, "max_symbols": max_symbols,
            "min_water_content": min_water_content, "max_water_content": max_water_content,
            "words": words,
            "chapters": chapters
        }
        result = self.database.query(query, parameters)

        chapters = []
        for record in map(lambda x: x["chapter"], result):
            chapter = Chapter(
                id=record.get("id"),
                id_diploma=record.get("id_diploma"),
                name=record.get("name", ""),
                water_content=record.get("water_content", 0),
                words=record.get("words", 0),
                symbols=record.get("symbols", 0),
                commonly_used_words=record.get("commonly_used_words", []),
                commonly_used_words_amount=record.get("commonly_used_words_amount", []),
                chapters=record.get("chapters", [])
            )
            chapters.append(chapter)
        return chapters
