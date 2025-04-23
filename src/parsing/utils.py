import json

from parsing.docClasses import (
    Diploma,
    Doc,
    DocSection,
    Chapter
)


def print_section(section: DocSection, print_text: bool):
    t = ''
    if section.level:
        t = '  ' * section.level
    print(f"{t}len(DocSection.structure): {len(section.structure)} DocSection.name: {section.name} lvl: {section.level}")
    if print_text:
        print(t + section.text.replace('\n', ' '))
    for e in section.structure:
        print_section(e, print_text)

def print_doc_structure(doc: Doc, print_text: bool):
    print('len(Doc.structure):', len(doc.structure), 
          'Doc.name:', doc.name)
    for e in doc.structure:
        print_section(e, print_text)

def print_doc_info(doc: Doc):
    print(f"Doc.name: {doc.name}\nDoc.author: {doc.author}\nDoc.academic_supervisor: {doc.academic_supervisor}\nDoc.year: {doc.year}")

def print_doc(doc: Doc, print_text=False):
    print_doc_info(doc)
    print_doc_structure(doc, print_text)