import io
import math
from collections import defaultdict
from datetime import datetime
from io import BytesIO

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

from src.diploma_processing.data_types import *

PAGE_SIZE = 20


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


def _get_search_diploma_params(
        min_id: int = None, max_id: int = None,
        name: str = None, author: str = None, academic_supervisor: str = None,
        min_year: int = None, max_year: int = None,
        min_pages: int = None, max_pages: int = None,
        min_words: int = None, max_words: int = None,
        min_date: str = None, max_date: str = None,
        chapters: list[int] = None,
        min_minimal_disclosure: int = None, max_minimal_disclosure: int = None,
        page: int = 1,
):
    return {
        "min_id": int(min_id) if min_id else None,
        "max_id": int(max_id) if max_id else None,
        "name": name,
        "author": author,
        "academic_supervisor": academic_supervisor,
        "min_year": int(min_year) if min_year else None,
        "max_year": int(max_year) if max_year else None,
        "min_pages": int(min_pages) if min_pages else None,
        "max_pages": int(max_pages) if max_pages else None,
        "min_words": int(min_words) if min_words else None,
        "max_words": int(max_words) if max_words else None,
        "min_minimal_disclosure": int(min_minimal_disclosure) if min_minimal_disclosure else None,
        "max_minimal_disclosure": int(max_minimal_disclosure) if max_minimal_disclosure else None,
        "min_date": min_date,
        "max_date": max_date,
        "chapters": list(map(int, chapters)) if chapters else None,
        "page": int(page) - 1,
    }


def _get_search_diploma_query(add_water: bool = False):
    return f"""
    MATCH (d:Diploma)-[:CONTAINS]->(c:Chapter)
    ORDER BY c.id
    WITH d, COLLECT(c.id) AS chapters
        {', SUM(c.water_content * c.words) * 1.0 / SUM(c.words) AS water_content' if add_water else ''}
    WHERE ($min_id IS NULL OR d.id >= $min_id)
      AND ($max_id IS NULL OR d.id <= $max_id)
      AND ($name IS NULL OR toLower(d.name) CONTAINS toLower($name))
      AND ($author IS NULL OR toLower(d.author) CONTAINS toLower($author))
      AND ($academic_supervisor IS NULL OR toLower(d.academic_supervisor) CONTAINS toLower($academic_supervisor))
      AND ($min_year IS NULL OR d.year >= $min_year)
      AND ($max_year IS NULL OR d.year <= $max_year)
      AND ($min_pages IS NULL OR d.pages >= $min_pages)
      AND ($max_pages IS NULL OR d.pages <= $max_pages)
      AND ($min_words IS NULL OR d.words >= $min_words)
      AND ($max_words IS NULL OR d.words <= $max_words)
      AND ($min_date IS NULL OR d.load_date >= Date($min_date))
      AND ($max_date IS NULL OR d.load_date <= Date($max_date))
      AND ($chapters IS NULL OR ANY(chapter IN $chapters WHERE chapter IN chapters))
      AND ($min_minimal_disclosure IS NULL OR d.minimal_disclosure >= $min_minimal_disclosure)
      AND ($max_minimal_disclosure IS NULL OR d.minimal_disclosure <= $max_minimal_disclosure)
    """


def _get_search_chapters_params(
        min_id: int = None, max_id: int = None,
        min_id_diploma: int = None, max_id_diploma: int = None,
        name: str = None,
        min_words: int = None, max_words: int = None,
        min_symbols: int = None, max_symbols: int = None,
        min_water_content: float = None, max_water_content: float = None,
        words: list[str] = None,
        chapters: list[int] = None, page: int = 1
):
    return {
        "min_id": int(min_id) if min_id else None,
        "max_id": int(max_id) if max_id else None,
        "min_id_diploma": int(min_id_diploma) if min_id_diploma else None,
        "max_id_diploma": int(max_id_diploma) if max_id_diploma else None,
        "name": name,
        "min_words": int(min_words) if min_words else None,
        "max_words": int(max_words) if max_words else None,
        "min_symbols": int(min_symbols) if min_symbols else None,
        "max_symbols": int(max_symbols) if max_symbols else None,
        "min_water_content": int(min_water_content) if min_water_content else None,
        "max_water_content": int(max_water_content) if max_water_content else None,
        "words": words,
        "chapters": list(map(int, chapters)) if chapters else None,
        "page": int(page) - 1
    }


def _get_search_chapters_query():
    return """
        MATCH (c:Chapter)-[:CONTAINS*0..1]->(c1:Chapter)
        ORDER BY c1.id
        WITH c, [id in COLLECT(c1.id) WHERE id <> c.id] AS chapters
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


class DiplomaRepository:
    def __init__(self, database: Neo4jDatabase):
        self.database = database
        self.database.query("CREATE INDEX IF NOT EXISTS FOR (n:Diploma) ON n.id")
        self.database.query("CREATE INDEX IF NOT EXISTS FOR (n:Chapter) ON n.id")
        self.database.query("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Diploma) REQUIRE n.neo4jImportId IS UNIQUE")
        self.database.query("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Chapter) REQUIRE n.neo4jImportId IS UNIQUE")

    def __len__(self) -> int:
        query = "MATCH (n) RETURN count(*)"

        result = self.database.query(query)

        return result[0][0]

    def save_diploma(self, diploma: Diploma) -> int | None:
        query = """
        MATCH (n)
        WITH COALESCE(MAX(n.id), 0) + 1 as id
        CREATE (d:Diploma { 
            name: $name, 
            author: $author, 
            academic_supervisor: $academic_supervisor, 
            year: $year, 
            pages: $pages,
            words: $words,
            load_date: $load_date,
            shingles: $shingles,
            minimal_disclosure: $minimal_disclosure,
            disclosure_keys: $disclosure_keys,
            disclosure_percentage: $disclosure_percentage
        })
        SET d.id = id
        RETURN d.id
        """
        parameters = {
            "name": diploma.name,
            "author": diploma.author,
            "academic_supervisor": diploma.academic_supervisor,
            "year": diploma.year,
            "pages": diploma.pages,
            "words": diploma.words,
            "load_date": diploma.load_date.date(),
            "shingles": diploma.shingles,
            "minimal_disclosure": diploma.minimal_disclosure,
            "disclosure_keys": diploma.disclosure_keys,
            "disclosure_percentage": diploma.disclosure_percentage
        }
        result = self.database.query(query, parameters)

        if result:
            id_diploma = result[0][0]

            self._create_similarities(id_diploma)

            ids = []
            for chapter in diploma.chapters:
                chapter.id_diploma = id_diploma
                ids.append(self._save_chapter(chapter))
            if len(ids) > 0:
                self._link_subchapters_to_diploma(id_diploma, ids)

            return id_diploma
        return None

    def _save_chapter(self, chapter: Chapter) -> int | None:
        query = """
        MATCH (n)
        WITH COALESCE(MAX(n.id), 0) + 1 as id
        CREATE (c:Chapter {
            id_diploma: $id_diploma, 
            name: $name, 
            water_content: $water_content, 
            words: $words, 
            symbols: $symbols, 
            commonly_used_words: $commonly_used_words, 
            commonly_used_words_amount: $commonly_used_words_amount
        })
        SET c.id = id
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

    def _link_subchapters_to_diploma(self, id_diploma: int, subchapter_ids: list[int]) -> None:
        query = """
        MATCH (d:Diploma), (c:Chapter) 
        WHERE d.id = $id_diploma AND c.id IN $subchapter_ids
        CREATE (d)-[:CONTAINS]->(c)
        """
        parameters = {
            "id_diploma": id_diploma,
            "subchapter_ids": subchapter_ids
        }
        self.database.query(query, parameters)

    def _link_subchapters(self, parent_chapter_id: int, subchapter_ids: list[int]) -> None:
        query = """
        MATCH (cp:Chapter), (cc:Chapter) 
        WHERE cp.id = $parent_chapter_id AND cc.id IN $subchapter_ids
        CREATE (cp)-[:CONTAINS]->(cc)
        """
        parameters = {
            "parent_chapter_id": parent_chapter_id,
            "subchapter_ids": subchapter_ids
        }
        self.database.query(query, parameters)

    def _create_similarities(self, id_diploma: int) -> None:
        query = """
        MATCH (d:Diploma), (ds:Diploma)
        WHERE d.id = $id and ds.id <> $id and ds.shingles
        WITH d, ds, 
            SIZE(apoc.coll.intersection(d.shingles, ds.shingles)) * 100.0 / 
                apoc.coll.min([SIZE(d.shingles), SIZE(ds.shingles)]) AS similarity
        CREATE (d)-[:SIMILAR_TO {similarity: similarity}]->(ds)
        """

        self.database.query(query, {"id": id_diploma})

    def load_diploma_data(self, id_diploma: int) -> Diploma | None:
        query = """
        MATCH (d:Diploma)-[r:SIMILAR_TO]-(d2:Diploma)
        WHERE d.id = $id_diploma
        ORDER BY r.similarity DESC
        LIMIT 3
        WITH collect([d2.id, d2.name, r.similarity]) as similar
        MATCH (d:Diploma)
        WHERE d.id = $id_diploma
        RETURN similar, {id: d.id, name: d.name, author: d.author, academic_supervisor: d.academic_supervisor, 
            year: d.year, pages: d.pages, words: d.words, load_date: d.load_date, 
            minimal_disclosure: d.minimal_disclosure, disclosure_keys: d.disclosure_keys, 
            disclosure_percentage: d.disclosure_percentage} AS d
        """
        parameters = {"id_diploma": id_diploma}
        result = self.database.query(query, parameters)

        if not result:
            return None

        node = result[0]["d"]
        similar = result[0]["similar"]

        diploma = Diploma(
            id=node.get("id"),
            name=node.get("name", ""),
            author=node.get("author", ""),
            academic_supervisor=node.get("academic_supervisor"),
            year=node.get("year", 0),
            pages=node.get("pages", 0),
            words=node.get("words", 0),
            load_date=datetime.datetime(
                node.get("load_date").year,
                node.get("load_date").month,
                node.get("load_date").day),
            chapters=[],
            similar_diplomas=similar,
            minimal_disclosure=node.get("minimal_disclosure", 0),
            disclosure_keys=node.get("disclosure_keys", []),
            disclosure_percentage=node.get("disclosure_percentage", [])
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
                        min_pages: int = None, max_pages: int = None,
                        min_words: int = None, max_words: int = None,
                        min_minimal_disclosure: int = None, max_minimal_disclosure: int = None,
                        min_date: str = None, max_date: str = None,
                        chapters: list[int] = None,
                        order_by: str = None, page: int = 1) -> Tuple[list[Diploma], int]:
        parameters = _get_search_diploma_params(min_id, max_id, name, author, academic_supervisor, min_year, max_year,
                                                min_pages, max_pages, min_words, max_words, min_date, max_date,
                                                chapters, min_minimal_disclosure, max_minimal_disclosure, page)

        query = _get_search_diploma_query()

        result = self.database.query(query + "RETURN count(*);", parameters)
        count = 0
        if result:
            count = result[0][0]

        if order_by:
            query += f"\nORDER BY d.{order_by}"

        query += f"""
        \nSKIP {PAGE_SIZE} * $page LIMIT {PAGE_SIZE}
        RETURN {{id: d.id, name: d.name, author: d.author, academic_supervisor: d.academic_supervisor, 
            year: d.year, pages: d.pages, words: d.words, load_date: d.load_date, chapters: chapters,
            minimal_disclosure: d.minimal_disclosure, disclosure_keys: d.disclosure_keys, 
            disclosure_percentage: d.disclosure_percentage}} AS diploma;
        """

        result = self.database.query(query, parameters)

        if result is not None:
            diplomas = []
            for record in map(lambda x: x["diploma"], result):
                diploma = Diploma(
                    id=record.get("id"),
                    name=record.get("name", ""),
                    author=record.get("author", ""),
                    academic_supervisor=record.get("academic_supervisor"),
                    year=record.get("year", 0),
                    pages=record.get("pages", 0),
                    words=record.get("words", 0),
                    load_date=datetime.datetime(
                        record.get("load_date").year,
                        record.get("load_date").month,
                        record.get("load_date").day),
                    chapters=record.get("chapters", []),
                    minimal_disclosure=record.get("minimal_disclosure", 0),
                    disclosure_keys=record.get("disclosure_keys", []),
                    disclosure_percentage=record.get("disclosure_percentage", [])
                )
                diplomas.append(diploma)
            return diplomas, math.ceil(count / PAGE_SIZE)
        return [], math.ceil(count / PAGE_SIZE)

    def search_chapters(self,
                        min_id: int = None, max_id: int = None,
                        min_id_diploma: int = None, max_id_diploma: int = None,
                        name: str = None,
                        min_words: int = None, max_words: int = None,
                        min_symbols: int = None, max_symbols: int = None,
                        min_water_content: float = None, max_water_content: float = None,
                        words: list[str] = None,
                        chapters: list[int] = None,
                        order_by: str = None, page: int = 1) -> Tuple[list[Chapter], int]:
        parameters = _get_search_chapters_params(min_id, max_id, min_id_diploma, max_id_diploma, name, min_words,
                                                 max_words, min_symbols, max_symbols, min_water_content,
                                                 max_water_content, words, chapters, page)

        query = _get_search_chapters_query()

        result = self.database.query(query + "RETURN count(*);", parameters)
        count = 0
        if result:
            count = result[0][0]

        if order_by:
            query += f"\nORDER BY c.{order_by}"

        query += f"""
        \nSKIP {PAGE_SIZE} * $page LIMIT {PAGE_SIZE}
        RETURN c{{.*, chapters: [id in chapters WHERE id <> c.id]}} AS chapter
        """

        result = self.database.query(query, parameters)
        print(result)

        if result is not None:
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
            return chapters, math.ceil(count / PAGE_SIZE)
        return [], math.ceil(count / PAGE_SIZE)

    def export(self) -> BytesIO | None:
        query = """
        CALL apoc.export.json.all(null, {useTypes:true, stream: true})
        YIELD data
        RETURN data;
        """

        result = self.database.query(query)

        if result is not None:
            json_string = result[0].get("data")

            in_memory_file = io.BytesIO()
            in_memory_file.write(json_string.encode())
            in_memory_file.seek(0)

            return in_memory_file

        return None

    def import_by_url(self, url: str) -> Tuple[int, int] | None:
        query = """
        CALL apoc.import.json($url, {nodePropertyMappings: {Diploma: {load_date: 'Localdate'}}})
        YIELD nodes, relationships
        RETURN nodes, relationships;
        """

        self.database.query("MATCH (n) DETACH DELETE n")
        result = self.database.query(query, {"url": url})
        self.database.query("MATCH (n) REMOVE n.neo4jImportId")

        if result is not None:
            return result[0]["nodes"], result[0]["relationships"]
        else:
            self.database.query("MATCH (n) DETACH DELETE n")
            return None

    def count_grouped_diplomas(self,
                               min_id: int = None, max_id: int = None,
                               name: str = None, author: str = None, academic_supervisor: str = None,
                               min_year: int = None, max_year: int = None,
                               min_pages: int = None, max_pages: int = None,
                               min_words: int = None, max_words: int = None,
                               min_minimal_disclosure: int = None, max_minimal_disclosure: int = None,
                               min_date: str = None, max_date: str = None,
                               chapters: list[int] = None, group_by: str = "academic_supervisor",
                               metric_type: str = "year") -> list[dict]:
        query = _get_search_diploma_query()
        query += f"""
        WITH d.{group_by} AS groupKey1, d.{metric_type} AS groupKey2
        ORDER BY groupKey1
        RETURN groupKey1, groupKey2, COUNT(*) AS count
        """
        parameters = _get_search_diploma_params(min_id, max_id, name, author, academic_supervisor, min_year, max_year,
                                                min_pages, max_pages, min_words, max_words, min_date, max_date,
                                                chapters, min_minimal_disclosure, max_minimal_disclosure)

        result = self.database.query(query, parameters)
        if result is None:
            return []
        return [{"key1": record["groupKey1"], "key2": record["groupKey2"], "count": record["count"]} for
                record in result]

    def get_grouped_metrics(self,
                            min_id: int = None, max_id: int = None,
                            name: str = None, author: str = None, academic_supervisor: str = None,
                            min_year: int = None, max_year: int = None,
                            min_pages: int = None, max_pages: int = None,
                            min_words: int = None, max_words: int = None,
                            min_minimal_disclosure: int = None, max_minimal_disclosure: int = None,
                            min_date: str = None, max_date: str = None,
                            chapters: list[int] = None,
                            group_by: str = "academic_supervisor",
                            metric_type: str = "words") -> list[dict]:
        query = _get_search_diploma_query()
        query += f"""
        WITH d.{group_by} AS groupKey, d.{metric_type} AS metric
        ORDER BY groupKey
        RETURN groupKey, AVG(metric) AS avg
        """
        parameters = _get_search_diploma_params(min_id, max_id, name, author, academic_supervisor, min_year, max_year,
                                                min_pages, max_pages, min_words, max_words, min_date, max_date,
                                                chapters, min_minimal_disclosure, max_minimal_disclosure)
        result = self.database.query(query, parameters)
        if result is None:
            return []

        return [{"key1": record["groupKey"], "avg": record["avg"]} for record in result]

    def get_avg_water_by_group(self,
                               min_id: int = None, max_id: int = None,
                               name: str = None, author: str = None, academic_supervisor: str = None,
                               min_year: int = None, max_year: int = None,
                               min_pages: int = None, max_pages: int = None,
                               min_words: int = None, max_words: int = None,
                               min_minimal_disclosure: int = None, max_minimal_disclosure: int = None,
                               min_date: str = None, max_date: str = None,
                               chapters: list[int] = None,
                               group_by: str = "academic_supervisor",
                               metric_type: str = "water_content") -> list[dict]:
        query = _get_search_diploma_query(add_water=True)
        query += f"""
        WITH d.{group_by} AS groupKey, water_content
        ORDER BY groupKey
        RETURN groupKey, AVG(water_content) AS avg
        """
        parameters = _get_search_diploma_params(min_id, max_id, name, author, academic_supervisor, min_year, max_year,
                                                min_pages, max_pages, min_words, max_words, min_date, max_date,
                                                chapters, min_minimal_disclosure, max_minimal_disclosure)
        result = self.database.query(query, parameters)
        if result is None:
            return []
        return [{"key1": record["groupKey"], "avg": record["avg"]} for record in result]

    def get_avg_disclosure_by_group(self,
                               min_id: int = None, max_id: int = None,
                               name: str = None, author: str = None, academic_supervisor: str = None,
                               min_year: int = None, max_year: int = None,
                               min_pages: int = None, max_pages: int = None,
                               min_words: int = None, max_words: int = None,
                               min_minimal_disclosure: int = None, max_minimal_disclosure: int = None,
                               min_date: str = None, max_date: str = None,
                               chapters: list[int] = None,
                               group_by: str = "academic_supervisor",
                               metric_type: str = "water_content") -> list[dict]:
        query = _get_search_diploma_query()
        query += f"""
        WITH d.{group_by} AS groupKey, apoc.coll.avg(d.disclosure_percentage) as disclosure
        ORDER BY groupKey
        RETURN groupKey, AVG(disclosure) AS avg
        """
        parameters = _get_search_diploma_params(min_id, max_id, name, author, academic_supervisor, min_year,
                                                max_year,
                                                min_pages, max_pages, min_words, max_words, min_date, max_date,
                                                chapters, min_minimal_disclosure, max_minimal_disclosure)
        result = self.database.query(query, parameters)
        if result is None:
            return []
        return [{"key1": record["groupKey"], "avg": record["avg"]} for record in result]