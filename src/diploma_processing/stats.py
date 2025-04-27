import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from datetime import datetime
from collections import defaultdict

from src.diploma_processing.data_types import Diploma, Chapter
from src.diploma_processing.utils import doc_to_dataclass, doc_section_to_dataclass
from src.diploma_processing.parsing_docx.docClasses import Doc, DocSection


# класс нужен из-за необходимости скачивать пакеты nltk
# если будет возможность, в целом можно не заниматься проверкой пакетов каждый раз
class CalcStats:
    def __init__(self, max_common_words=5):
        nltk.download('punkt')
        nltk.download('punkt_tab')
        nltk.download('stopwords')
        self._stop_words = set(stopwords.words('russian'))
        self._max_common_words = max_common_words

    def calc_stats(self, doc: Doc):
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

    def _count_words(self, doc_section: DocSection):
        text = doc_section.text
        words = word_tokenize(text)
        # Удаление незначимых символов (например, знаков препинания)
        words = [word.lower() for word in words if word.isalpha()]
        if len(words) == 0:
            return 0, 0, 0, [], [] # Changed water content to zero here because zero length text has no content
        # Удаление стоп-слов и незначимых символов (например, знаков препинания)
        filtered_words = [word.lower() for word in words if word.lower() not in self._stop_words]
        # Подсчет частоты слов
        word_count = defaultdict(int)
        for word in filtered_words:
            word_count[word] += 1
        # Сортировка слов по частоте в порядке убывания
        sorted_words = sorted(word_count.keys(), key=lambda x: word_count[x], reverse=True)
        sorted_counts = [word_count[word] for word in sorted_words]
        water_content = int(len(filtered_words)/len(words) * 100) if len(words) > 0 else 0
        return water_content, len(words), len(text), sorted_words[:self._max_common_words], sorted_counts[:self._max_common_words]

