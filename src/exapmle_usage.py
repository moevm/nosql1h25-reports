from parsing.docxParser import DocxParser
from parsing.utils import print_doc


if __name__ == '__main__':
    file_path = './src/parsing/examples/2024ВКР038112КОТОВ.docx'
    file = open(file_path, 'rb') # без 'rb' не работает
    dp = DocxParser(file)
    doc = dp.read_document()
    print_doc(doc, True)