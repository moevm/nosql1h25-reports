import functools
import re
from collections import defaultdict
from datetime import datetime
from io import BytesIO
from typing import Union, BinaryIO
import nltk
import pymorphy2
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from rapidfuzz import process, fuzz
import numpy as np

from src.diploma_processing.data_types import Diploma, Chapter
from src.diploma_processing.parsing_docx.docClasses import Doc, DocSection
from src.diploma_processing.parsing_docx.docxParser import DocxParser
from src.diploma_processing.utils import doc_to_dataclass


LRU_CACHE_MAXSIZE = 2048
SHINGLES_SIM_THRESHOLD = 95


# класс нужен из-за необходимости скачивать пакеты nltk
# если будет возможность, в целом можно не заниматься проверкой пакетов каждый раз
class CalcStats:
    def __init__(self, max_common_words=5):
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt_tab')

        self._stop_words = set(stopwords.words('russian'))
        self._max_common_words = max_common_words
        self._morph = pymorphy2.MorphAnalyzer()
        self._CLEAN_NAME_REGEX = re.compile(r"^[\s!#$%&*+,-./:;=?@\\^_|~]+|[\s!#$%&*+,-./:;=?@\\^_|~]+$")
        self._shingle_length = 3

    def get_diploma_stats(self, file: str | Union[BinaryIO, BytesIO]) -> Diploma:
        try:
            dp = DocxParser(file)
            dp.read_document()
            diploma = self.calc_stats(dp.doc)
            return diploma
        except Exception as e:
            raise Exception("Ошибка при обработке файла: ", e)  # exc_info=True для полного traceback

    def calc_stats(self, doc: Doc):
        self._remove_empty_sections(doc)
        self._clean_section_names(doc)
        diploma = doc_to_dataclass(doc)
        
        diploma.load_date = datetime.now()
        diploma.words = 0
        for i in range(len(diploma.chapters)):
            doc_section = doc.structure[i]
            chapter = diploma.chapters[i]
            self._calc_chapters_stats(doc_section, chapter)
            if chapter.words:
                diploma.words += chapter.words

        self._calc_shingles(diploma)

        for c in diploma.chapters:
            self._calc_commonly_used_words_and_amount(c)
        
        return diploma

    def _calc_chapters_stats(self, doc_section: DocSection, chapter: Chapter):
        # init empty - Moved initialization here to avoid overwriting stats
        chapter.water_content = 0
        chapter.words = 0
        chapter.symbols = 0
        chapter.commonly_used_words = []
        chapter.commonly_used_words_amount = []

        # run calcs
        water_content, words, symbols, commonly_used_words= self._count_words(doc_section)
        # add calcs results
        chapter.water_content += water_content
        chapter.words += words
        chapter.symbols += symbols
        chapter.commonly_used_words.extend(commonly_used_words)  # Use extend to add lists

        # run calcs for children
        for i in range(len(chapter.chapters)):
            doc_section_i = doc_section.structure[i]
            chapter_i = chapter.chapters[i]
            self._calc_chapters_stats(doc_section_i, chapter_i)

            # add children stats
            chapter.water_content += chapter_i.water_content
            chapter.words += chapter_i.words
            chapter.symbols += chapter_i.symbols
            chapter.commonly_used_words.extend(chapter_i.commonly_used_words)

        # avg for water_content - Moved this to avoid division by zero when chapter has no subchapters
        if len(chapter.chapters) > 0:
            chapter.water_content = int(chapter.water_content / (len(chapter.chapters) + 1))

    def _calc_shingles(self, diploma: Diploma):
        all_words = []
        for c in diploma.chapters:
            all_words.extend(c.commonly_used_words)
        
        if len(all_words) < self._shingle_length:
            diploma.shingles = []
            return

        shingles = []
        for i in range(len(all_words) - self._shingle_length + 1):
            # shingle = f"{all_words[i]} {all_words[i+1]} {all_words[i+2]}"
            shingle = " ".join(all_words[i:i + self._shingle_length])
            shingles.append(shingle)

        shingles = self._del_sim_shingles(shingles)

        diploma.shingles = shingles

    def _del_sim_shingles(self, shingles: list[str], threshold=SHINGLES_SIM_THRESHOLD) -> list[str]:
        if not shingles:
            return []

        similarity_matrix = process.cdist(
            queries=shingles,
            choices=shingles,
            scorer=fuzz.ratio,
            workers=-1
        )

        # Считаем среднюю похожесть для каждой строки
        average_similarities = np.mean(similarity_matrix, axis=1)
        # Определяем строки, которые нужно удалить (те, у которых самая высокая средняя похожесть)
        indices_to_remove = np.where(average_similarities >= np.percentile(average_similarities, threshold))[0]
        # Создаем новый список, содержащий только строки, которые не нужно удалять
        result = [s for i, s in enumerate(shingles) if i not in indices_to_remove]
        return result

    def _calc_commonly_used_words_and_amount(self, chapter: Chapter):
        commonly_used_words, commonly_used_words_amount = self._sort_commonly_used_words_and_amount(chapter.commonly_used_words)
        chapter.commonly_used_words = commonly_used_words
        chapter.commonly_used_words_amount = commonly_used_words_amount
        for c in chapter.chapters:
            self._calc_commonly_used_words_and_amount(c)
    
    def _sort_commonly_used_words_and_amount(self, words: list[str]):
        # Подсчет частоты слов
        word_count = defaultdict(int)
        for word in words:
            word_count[word] += 1
        # Сортировка слов по частоте в порядке убывания
        sorted_words = sorted(word_count.keys(), key=lambda x: word_count[x], reverse=True)
        sorted_counts = [word_count[word] for word in sorted_words]
        return sorted_words[:self._max_common_words], sorted_counts[:self._max_common_words]

    @functools.lru_cache(maxsize=LRU_CACHE_MAXSIZE)  # Кэшируем результаты
    def _normalize_word(self, word):
        try:
            # может возвращать пустой список, если слово не найдено в словаре
            return self._morph.parse(word)[0].normal_form
        except IndexError:
            return word  # Вернуть исходное слово, если не удалось нормализовать

    def _count_words(self, doc_section: DocSection):
        text = doc_section.text
        words = word_tokenize(text)
        # Удаление незначимых символов (например, знаков препинания)
        words = [word.lower() for word in words if word.isalpha()]
        if len(words) == 0:
            return 0, 0, 0, []

        # Приведение слов к нормальной форме с помощью pymorphy2
        normalized_words = [self._normalize_word(word) for word in words]

        # Удаление стоп-слов и незначимых символов (например, знаков препинания)
        filtered_words = [word.lower() for word in normalized_words if word.lower() not in self._stop_words]
        # Подсчет частоты слов
        word_count = defaultdict(int)
        for word in filtered_words:
            word_count[word] += 1
        sorted_counts = [word_count[word] for word in filtered_words]
        water_content = int((1 - len(filtered_words) / len(words)) * 100) if len(words) > 0 else 0
        return water_content, len(words), len(text), filtered_words

    def _remove_empty_sections(self, doc: Doc):
        """Removes sections with no name from the document structure."""

        def remove_empty_sections_recursive(structure):
            new_structure = []
            for section in structure:
                if section.name is not None:
                    remove_empty_sections_recursive(section.structure)
                    new_structure.append(section)
                else:
                    # Recursively process children of the empty section
                    remove_empty_sections_recursive(section.structure)

            structure.clear()  # Clear the original list
            structure.extend(new_structure)  # Add the filtered sections back

        remove_empty_sections_recursive(doc.structure)

    def _clean_section_names(self, doc: Doc):
        """Cleans section names by removing leading/trailing whitespace and punctuation."""

        def clean_name(name: str) -> str:
            if not name:
                return name
            # Remove leading and trailing whitespace and punctuation, EXCEPT parentheses and quotes
            cleaned_name = self._CLEAN_NAME_REGEX.sub("", name)
            return cleaned_name

        def clean_section_names_recursive(structure):
            for section in structure:
                if section.name:
                    section.name = clean_name(section.name)
                clean_section_names_recursive(section.structure)

        clean_section_names_recursive(doc.structure)
