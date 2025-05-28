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
import hashlib
import math

from src.diploma_processing.data_types import Diploma, Chapter
from src.diploma_processing.parsing_docx.docClasses import Doc, DocSection
from src.diploma_processing.parsing_docx.docxParser import DocxParser
from src.diploma_processing.utils import doc_to_dataclass


LRU_CACHE_MAXSIZE = 2048
SHINGLES_SIM_THRESHOLD = 95
MAX_INT64 = 2**63


class CalcStats:
    def __init__(self, max_common_words=5, shingle_length=3):
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
        self._shingle_length = shingle_length
        self._disclosure_keys_to_remove = [
            'введение',
            'структура',
            'вывод',
            'заключение',
            'определение обозначение сокращение',
            'структуосновной теоретический положение',
            'актуальность',
            'обзор предметный область',
        ]
        self._disclosure_word_min_count = 5

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
        # diploma.words = 0
        for i in range(len(diploma.chapters)):
            doc_section = doc.structure[i]
            chapter = diploma.chapters[i]
            self._calc_chapters_stats(doc_section, chapter)
            # if chapter.words:
            #     diploma.words += chapter.words

        self._calc_disclosure_stats(diploma)
        self._calc_shingles(diploma, doc)

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

    def _calc_shingles(self, diploma: Diploma, doc: Doc):
        all_text = []
        for section in doc.structure:
            self._extract_text_recursive(section, all_text)

        words = []
        for text in all_text:
            words.extend(word_tokenize(text))
        words = [word.lower() for word in words if word.isalpha()]

        if len(words) < self._shingle_length:
            diploma.shingles = []
            return

        words = list(map(lambda x: int(hashlib.sha256(x.encode('utf-8')).hexdigest(), 16), words))

        shingles = []
        for i in range(len(words) - self._shingle_length + 1):
            shingle_words = words[i:i + self._shingle_length]
            int_value = math.prod(shingle_words) % MAX_INT64
            shingles.append(int_value)
        
        shingles = list(set(shingles))
        shingles.sort()
        diploma.shingles = shingles

    def _extract_text_recursive(self, section: DocSection, all_text: list[str]):
        all_text.append(section.text)
        for sub_section in section.structure:
            self._extract_text_recursive(sub_section, all_text)

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

    def _process_text_for_disclosure(self, text: str) -> list[str]:
        """
        Processes text to extract normalized, lowercased, non-stop words.
        Consistent with the word processing logic in _count_words.
        """
        if not text:
            return []
        
        words_tokenized = word_tokenize(text)
        alpha_words_lower = [word.lower() for word in words_tokenized if word.isalpha()]
        
        if not alpha_words_lower:
            return []
        
        normalized_words_list = [self._normalize_word(word) for word in alpha_words_lower]
        
        processed_words = [
            norm_word.lower() for norm_word in normalized_words_list 
            if norm_word.lower() not in self._stop_words
        ]
        return processed_words

    def _collect_main_chapters_names(self, chapters: list[Chapter], names_list: list[str]):
        for chapter in chapters:
            if chapter.name.strip().lower() == 'структура' and chapter.chapters:
                for c in chapter.chapters:
                    names_list.append(c.name)
    
    def _extract_text_recursive_normalized(self, chapters: list[Chapter], all_text: list[str]):
        for chepter in chapters:
            all_text.extend(chepter.commonly_used_words)
            if chepter.chapters:
                self._extract_text_recursive_normalized(chapters=chepter.chapters, all_text=all_text)

    def _calc_disclosure_stats(self, diploma: Diploma):
        """
        Calculates Diploma.disclosure_keys and Diploma.disclosure_persentage.
        """
        # A. Prepare Disclosure Keys
        source_texts_for_keys = []
        if diploma.name:
            source_texts_for_keys.append(diploma.name)
        
        chapter_names_flat = []
        if diploma.chapters:
            self._collect_main_chapters_names(diploma.chapters, chapter_names_flat)
        source_texts_for_keys.extend(chapter_names_flat)

        processed_keys = []
        for text_item in source_texts_for_keys:
            words = self._process_text_for_disclosure(text_item)
            processed_keys.append(words)
        
        i = 0
        while i < len(processed_keys):
            if " ".join(processed_keys[i]) in self._disclosure_keys_to_remove:
                source_texts_for_keys.pop(i)
                processed_keys.pop(i)
                i -= 1
            i += 1
        diploma.disclosure_keys = source_texts_for_keys

        # B. Prepare Full Diploma Text
        processed_total_diploma_words = []
        self._extract_text_recursive_normalized(diploma.chapters, processed_total_diploma_words)

        # C. Calculate Percentages
        diploma.disclosure_persentage = []

        if not processed_total_diploma_words or not diploma.disclosure_keys:
            diploma.disclosure_persentage = [0] * len(diploma.disclosure_keys)
            return

        word_count = defaultdict(int)
        for word in processed_total_diploma_words:
            word_count[word] += 1

        for i, words in enumerate(processed_keys):
            count_of_key_words_in_text = 0
            for word in words:
                count_of_key_words_in_text += word_count.get(word, 0)
            percentage = 0
            if count_of_key_words_in_text >= len(words) * self._disclosure_word_min_count:
                percentage = 100
            else:
                percentage = int((count_of_key_words_in_text / (len(words) * self._disclosure_word_min_count) * 100))
            diploma.disclosure_persentage.append(percentage)
        
        diploma.minimal_disclosure = min(diploma.disclosure_persentage)
