from diploma_repo import Neo4jDatabase, DiplomaRepository
from src.diploma_processing.data_types import *
from src.diploma_processing.testkit.test_diploma_consts import test_diploma

# Инициализируем соединение с базой данных Neo4j
neo4j_db = Neo4jDatabase(host="bolt://localhost", user="neo4j", password="password")

# Создаем репозиторий дипломов
diploma_repository = DiplomaRepository(neo4j_db)

# Пример диплома
test_diploma1 = test_diploma[0]

test_diploma2 = test_diploma[1]


def testing():
    # Получаем все узлы и связи
    all_data = neo4j_db.query("MATCH (n)-[r]->(m) RETURN n, r, m")

    # Получаем все узлы
    all_nodes = neo4j_db.query("MATCH (n) RETURN n")

    # Получаем все связи
    all_relationships = neo4j_db.query("MATCH ()-[r]->() RETURN r")

    print(all_data, all_nodes, sep='\n---------------\n')
    print('\n\n\n', all_relationships, sep='\n\n')


# 1. Сохраняем диплом в базу данных
def test_save_diploma(test_diploma):
    diploma_id = diploma_repository.save_diploma(test_diploma)
    print(f"Диплом сохранен с ID: {diploma_id}")
    return diploma_id


# 2. Сохраняем главы диплома в базу данных
def save_chapter_recursive(chapter: Chapter):
    """
    Сохраняет главу и её подразделы рекурсивно.
    Использует внешнюю переменную test_diploma1.
    """
    chapter.id_diploma = test_diploma1.id  # <-- берем id диплома из внешней переменной
    chapter_id = diploma_repository.save_chapter(chapter)
    print(f"Глава '{chapter.name}' сохранена с ID: {chapter_id}")

    # Если у главы есть подразделы, рекурсивно сохраняем их
    if chapter.chapters:
        for subchapter in chapter.chapters:
            save_chapter_recursive(subchapter)


def test_save_chapters():
    """
    Сохраняем все главы диплома, включая все вложенные подразделы.
    """
    for chapter in test_diploma1.chapters:
        save_chapter_recursive(chapter)


# 3. Связываем главы с дипломом
def test_link_chapters_to_diploma():
    diploma_repository.link_chapter_to_diploma(test_diploma1.id)


# 4 Связывание глав
def test_link_subchapters_recursive(chapter):
    subchapter_ids = [subchapter.id for subchapter in chapter.chapters]
    if subchapter_ids:
        diploma_repository.link_subchapters(chapter.id, subchapter_ids)
        print(f"Подглавы {subchapter_ids} успешно связаны с главой '{chapter.name}' (ID {chapter.id}).")
        # Рекурсивно связываем подглавы
        for subchapter in chapter.chapters:
            test_link_subchapters_recursive(subchapter)
    else:
        print(f"У главы '{chapter.name}' нет подглав для связывания.")


def test_link_subchapters():
    # Начинаем рекурсивно
    for chapt in test_diploma1.chapters:
        test_link_subchapters_recursive(chapt)


# 5 Извлечение шинглов
# idk what to do yet

# 6 Выставление параметра схожести
def test_save_similarity():
    similarity_value = 0.3  # допустим, какая-то вычисленная схожесть
    diploma_repository.save_similarity(test_diploma1.id, test_diploma2.id, similarity_value)
    print(
        f"Связь схожести между дипломами {test_diploma1.id} и {test_diploma2.id} успешно сохранена (похожесть {similarity_value}).")


# 7 Извлечение диплома и его разделов (3 запроса)
def test_load_diploma_graph(diploma):
    if diploma.id is not None:
        nodes, rels = diploma_repository.load_diploma_graph(diploma.id)
        print(f"У диплома с ID {diploma.id} найдены узлы: {nodes}")
        print(f"И связи: {rels}")
    else:
        print("У тестового диплома нет ID для загрузки графа.")


def test_load_diploma_data(diploma):
    if diploma.id is not None:
        diploma_data = diploma_repository.load_diploma_data(diploma.id)
        print(f"Данные диплома с ID {diploma.id}: {diploma_data}")
    else:
        print("У тестового диплома нет ID для загрузки данных.")


def test_load_chapters(diploma):
    chapter_ids = [chapter.id for chapter in diploma.chapters if chapter.id is not None]
    if chapter_ids:
        chapters_data = diploma_repository.load_chapters(chapter_ids)
        print(f"Данные глав с ID {chapter_ids}:")
        for chapter in chapters_data:
            print(chapter)
    else:
        print("Нет доступных глав для загрузки.")


neo4j_db.query("MATCH (n) DETACH DELETE n")
testing()

# 1
id_dipl1 = test_save_diploma(test_diploma1)
# 2
test_save_chapters()
# 3
test_link_chapters_to_diploma()
# 4
test_link_subchapters()
# 5
# no field 'shingles' in Diploma
# 6
id_dipl2 = test_save_diploma(test_diploma2)
test_save_similarity()
# 7
test_load_diploma_graph(test_diploma1)
test_load_diploma_data(test_diploma1)
test_load_chapters(test_diploma1)

testing()
print(test_diploma1, test_diploma2, sep='\n')

# Закрываем соединение с базой данных
neo4j_db.close()
