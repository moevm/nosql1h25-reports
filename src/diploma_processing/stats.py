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

from src.diploma_processing.data_types import Diploma, Chapter
from src.diploma_processing.parsing_docx.docClasses import Doc, DocSection
from src.diploma_processing.parsing_docx.docxParser import DocxParser
from src.diploma_processing.utils import doc_to_dataclass

LRU_CACHE_MAXSIZE = 2048


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
        return diploma

    def _calc_chapters_stats(self, doc_section: DocSection, chapter: Chapter):
        # init empty - Moved initialization here to avoid overwriting stats
        chapter.water_content = 0
        chapter.words = 0
        chapter.symbols = 0
        chapter.commonly_used_words = []
        chapter.commonly_used_words_amount = []

        # run calcs
        water_content, words, symbols, commonly_used_words, commonly_used_words_amount = self._count_words(doc_section)
        # add calcs results
        chapter.water_content += water_content
        chapter.words += words
        chapter.symbols += symbols
        chapter.commonly_used_words.extend(commonly_used_words)  # Use extend to add lists
        chapter.commonly_used_words_amount.extend(commonly_used_words_amount)  # Use extend to add lists

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
            chapter.commonly_used_words_amount.extend(chapter_i.commonly_used_words_amount)

        # recalc commonly_used_words
        if len(chapter.commonly_used_words) > self._max_common_words:
            word_count = defaultdict(int)
            for word, count in zip(chapter.commonly_used_words, chapter.commonly_used_words_amount):
                word_count[word] += count
            sorted_words = sorted(word_count.keys(), key=lambda x: word_count[x], reverse=True)
            sorted_counts = [word_count[word] for word in sorted_words]

            chapter.commonly_used_words = sorted_words[:self._max_common_words]
            chapter.commonly_used_words_amount = sorted_counts[:self._max_common_words]

        # avg for water_content - Moved this to avoid division by zero when chapter has no subchapters
        if len(chapter.chapters) > 0:
            chapter.water_content = int(chapter.water_content / (len(chapter.chapters) + 1))

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
            return 0, 0, 0, [], []  # Changed water content to zero here because zero length text has no content

        # Приведение слов к нормальной форме с помощью pymorphy2
        # normalized_words = [self._morph.parse(word)[0].normal_form for word in words]
        normalized_words = [self._normalize_word(word) for word in words]

        # Удаление стоп-слов и незначимых символов (например, знаков препинания)
        filtered_words = [word.lower() for word in normalized_words if word.lower() not in self._stop_words]
        # Подсчет частоты слов
        word_count = defaultdict(int)
        for word in filtered_words:
            word_count[word] += 1
        # Сортировка слов по частоте в порядке убывания
        sorted_words = sorted(word_count.keys(), key=lambda x: word_count[x], reverse=True)
        sorted_counts = [word_count[word] for word in sorted_words]
        water_content = int(len(filtered_words) / len(words) * 100) if len(words) > 0 else 0
        return water_content, len(words), len(text), sorted_words[:self._max_common_words], sorted_counts[
                                                                                            :self._max_common_words]

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
            # # Remove leading and trailing whitespace and punctuation
            # cleaned_name = re.sub(r"^[\s\W]+|[\s\W]+$", "", name)
            # Remove leading and trailing whitespace and punctuation, EXCEPT parentheses and quotes
            # cleaned_name = re.sub(r"^[\s!#$%&*+,-./:;=?@\\^_|~]+|[\s!#$%&*+,-./:;=?@\\^_|~]+$", "", name)
            cleaned_name = self._CLEAN_NAME_REGEX.sub("", name)
            return cleaned_name

        def clean_section_names_recursive(structure):
            for section in structure:
                if section.name:
                    section.name = clean_name(section.name)
                clean_section_names_recursive(section.structure)

        clean_section_names_recursive(doc.structure)
