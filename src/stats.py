import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from datetime import datetime
from collections import defaultdict

from src.data_types import Diploma, Chapter
from src.utils import doc_to_dataclass, doc_section_to_dataclass
from src.parsing_docx.docClasses import Doc, DocSection


# класс нужен из-за необходимости скачивать пакеты nltk
# если будет возможность, в целом можно не заниматься проверкой пакетов каждый раз
class CalcStats:
    def __init__(self):
        nltk.download('punkt')
        nltk.download('punkt_tab')
        nltk.download('stopwords')
        self._stop_words = set(stopwords.words('russian'))

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
        for i in range(len(chapter.chapters)):
            doc_section_i = doc_section.structure[i]
            chapter_i = chapter.chapters[i]
            chapter_i.water_content = 0
            chapter_i.words = 0
            chapter_i.symbols = 0
            chapter_i.commonly_used_words = []
            chapter_i.commonly_used_words_amount = []
            water_content, words, symbols, commonly_used_words, commonly_used_words_amount = self._count_words(doc_section_i)
            chapter_i.water_content += water_content
            chapter_i.words += words
            chapter_i.symbols += symbols
            chapter_i.commonly_used_words += commonly_used_words
            chapter_i.commonly_used_words_amount += commonly_used_words_amount
            self._calc_chapters_stats(doc_section_i, chapter_i)
            for j in range(len(chapter_i.chapters)):
                chapter_j = chapter_i.chapters[j]
                chapter_i.water_content += chapter_j.water_content
                chapter_i.words += chapter_j.words
                chapter_i.symbols += chapter_j.symbols
                chapter_i.commonly_used_words += chapter_j.commonly_used_words
                chapter_i.commonly_used_words_amount += chapter_j.commonly_used_words_amount

    def _count_words(self, doc_section: DocSection):
        text = doc_section.text
        words = word_tokenize(text)
        # Удаление незначимых символов (например, знаков препинания)
        words = [word.lower() for word in words if word.isalpha()]
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
        return water_content, len(words), len(text), sorted_words, sorted_counts