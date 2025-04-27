from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from src.diploma_processing.data_types import Chapter, Diploma


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

    def link_chapter_to_diploma(self, id_diploma: int) -> None:
        query = """
                MATCH (d:Diploma), (c:Chapter) 
                WHERE ID(d) = $id_diploma AND c.id_diploma = $id_diploma
                CREATE (d)-[:CONTAINS]->(c)
                """
        parameters = {"id_diploma": id_diploma}
        self.database.query(query, parameters)

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

    def get_other_diplomas_shingles(self, id_diploma: int) -> list[tuple[int, str]]:
        pass

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

    def load_diploma_graph(self, id_diploma: int) -> tuple[list[int], list[list[int]]]:
        pass

    def load_diploma_data(self, id_diploma: int) -> dict:
        pass

    def load_chapters(self, chapter_ids: list[int]) -> list[dict]:
        pass

