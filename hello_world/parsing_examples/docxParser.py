import docx
import os

from docClasses import Doc, DocSection


class DocxParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.docx_file = None

    def _check_file_exists(self):
        """
        Проверяет, существует ли файл и является ли он строкой.
        
        :raises ValueError: если путь к файлу не валиден
        :raises FileNotFoundError: если файл не существует
        """
        if not self.file_path or not isinstance(self.file_path, str):
            raise ValueError("Путь к файлу должен быть строкой и не пустым")
        try:
            if not os.path.exists(self.file_path) or not os.path.isfile(self.file_path):
                raise FileNotFoundError(f"Файл '{self.file_path}' не найден")
        except ImportError as e:
            print("Возможная ошибка: ", str(e))

    def _check_file_format(self):
        """
        Проверяет, является ли файл форматом .docx.
        
        :raises ValueError: если файл имеет неверный формат
        """
        try:
            self.docx_file = docx.Document(self.file_path)
        except docx.exc.InvalidFileException as e:
            raise ValueError(f"Файл '{self.file_path}' имеет неверный формат (.docx)")

    def read_document(self):
        """
        Чтение содержимого документа.
        
        :return: Экземпляр объекта Doc.
        """

        # вопрос, будем ли мы проверять как-либо ещё дополнительно форматирование
        # т.е. содержит ли документ нужные заделы, например
        # содержит ли нужные таблицы с данными по типу темы, автор и д.т.
        self._check_file_exists()
        self._check_file_format()

        if not hasattr(self, 'docx_file'):
            raise AttributeError("Файл не был открыт")

        doc = Doc()

        self._read_structure(doc)
        self._read_info(doc)

        return doc

    def _read_structure(self, doc: Doc):
        """
        Чтение основной структуры документа:
        проходит по всем параграфам начиная с параграфа "СОДЕРЖАНИЕ",
        заканчивая параграфом "СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ",
        сохраняет в виде вложенного списка в doc.structure,
        пропускает пустые параграфы (в изначальном документе - переносы строк)
        """

        found_content_section = False
        found_references_section = False
        current_section = DocSection()
        doc.structure.append(current_section)

        for paragraph in self.docx_file.paragraphs:
            text = paragraph.text.strip().lower()
            if len(text) == 0:
                continue

            elif "содержание" == text:
                found_content_section = True
                continue
            elif "список использованных источников" == text:
                found_references_section = True
                break

            elif found_content_section and not found_references_section:
                level = self._get_heared_level(paragraph)

                if current_section.level is None and level != 0:
                    current_section.level = level
                    current_section.title = text

                if level == 0:
                    if len(current_section.text) == 0:
                        current_section.text = text
                    else:
                        current_section.text += ' ' + text

                elif level > current_section.level:
                    new_section = DocSection()
                    new_section.upper = current_section
                    new_section.title = text
                    new_section.level = level
                    current_section.structure.append(new_section)
                    current_section = new_section
                
                elif level == current_section.level:
                    new_section = DocSection()
                    new_section.upper = current_section.upper
                    new_section.level = level
                    new_section.title = text
                    if current_section.upper is not None:
                        current_section = current_section.upper
                        current_section.structure.append(new_section)
                        current_section = new_section
                    else:
                        current_section = new_section
                        doc.structure.append(current_section)

                elif level < current_section.level:
                    while current_section.upper is not None and level <= current_section.level:
                        current_section = current_section.upper
                    new_section = DocSection()
                    new_section.title = text
                    new_section.level = level
                    if current_section.upper is None:
                        current_section = new_section
                        doc.structure.append(current_section)
                    else:
                        new_section.upper = current_section
                        current_section.structure.append(new_section)
                        current_section = new_section

    def _get_heared_level(self, paragraph):
        level = 0
        s = paragraph.style.name.lower().split()
        if len(s) > 1 and s[0] == 'heading':
            level = int(s[len(s) - 1])
        return level
    
    def _read_info(self, doc: Doc):
        """
        Чтение основной информации о документе:
        doc.title; doc.author; doc.sci_director; doc.count_wolds; doc.count_symbols
        """
        pass