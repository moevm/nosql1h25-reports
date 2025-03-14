from parsing.docClasses import Doc, DocSection
from parsing.docxParser import DocxParser


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
    file_path = './examples/2024ВКР038342ОРЛОВ.docx'
    file = open(file_path, 'rb') # без 'rb' не работает
    dp = DocxParser(file)
    doc = dp.read_document()
    print_doc(doc)