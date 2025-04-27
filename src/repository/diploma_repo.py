from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from src.diploma_processing.data_types import Chapter, Diploma


class Neo4jDatabase:
    def __init__(self, uri, user, password):
        pass

    def close(self):
        pass

    def query(self, query, parameters=None):
        pass


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

