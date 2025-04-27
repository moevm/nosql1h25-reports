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
        pass

    def save_diploma(self, diploma: Diploma) -> int | None:
        pass

    def save_chapter(self, chapter: Chapter) -> int | None:
        pass

    def link_chapter_to_diploma(self, id_diploma: int) -> None:
        pass

    def link_subchapters(self, parent_chapter_id: int, subchapter_ids: list[int]) -> None:
        pass

    def get_other_diplomas_shingles(self, id_diploma: int) -> list[tuple[int, str]]:
        pass

    def save_similarity(self, id_diploma: int, id_diploma_2: int, similarity: float) -> None:
        pass

    def load_diploma_graph(self, id_diploma: int) -> tuple[list[int], list[list[int]]]:
        pass

    def load_diploma_data(self, id_diploma: int) -> dict:
        pass

    def load_chapters(self, chapter_ids: list[int]) -> list[dict]:
        pass

