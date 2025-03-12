from docxParser import DocxParser
from docClasses import Doc, DocSection


def print_section(section: DocSection):
    print('len(DocSection.structure):', len(section.structure), 
          'DocSection.title:', section.title,
          'lvl:', section.level)
    print(section.text)
    for e in section.structure:
        print_section(e)

def print_doc(doc: Doc):
    print('len(Doc.structure):', len(doc.structure), 
          'Doc.title:', doc.title)
    for e in doc.structure:
        print_section(e)


if __name__ == '__main__':
    file_path = '2024ВКР038125ПАВЛОВ.docx'
    dp = DocxParser(file_path)
    doc = dp.read_document()
    print_doc(doc)