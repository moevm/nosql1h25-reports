import glob
import time
import sys
sys.path.append('c:/Users/bhunp/Documents/nosql1h25-reports/')

from src.diploma_processing.stats import CalcStats
from src.diploma_processing.utils import save_diploma_json
from src.diploma_processing.diploma_comparing import calc_similarity
import src.diploma_processing.testkit


if __name__ == "__main__":
    path_to_docx = "src/diploma_processing/testkit/docx_examples"
    path_to_save = "src/diploma_processing/testkit/parsing_examples/"
    start = time.time()
    docx_list = glob.glob(path_to_docx + '/*.docx')
    cs = CalcStats()
    diplomas = []
    for i in range(len(docx_list)):
        docx_path = docx_list[i]
        print(docx_path)
        file = open(docx_path, 'rb')
        diplomas.append(cs.get_diploma_stats(file))
        name = docx_path.replace('docx_examples', 'parsing_examples')
        path = name[:name.rfind('.')] + '.json'
        save_diploma_json(diplomas[i], path)
    print('total parsing and calculating stats time:', time.time() - start)
    start = time.time()
    for i in range(len(diplomas)):
        for j in range(len(diplomas)):
            # print(f"cmp files: \n{docx_list[i]}\n{docx_list[j]}\nsimilarity: {"{:.4f}".format(calc_similarity(diplomas[i], diplomas[j]))}%")
            print(f"cmp files: \n{docx_list[i]}\n{docx_list[j]}\nsimilarity: {calc_similarity(diplomas[i], diplomas[j]):.4f}%")
    print(f"total comparing time: {time.time() - start}")


'''
пример вывода:

src/diploma_processing/testkit/docx_examples\\2024ВКР038112КОТОВ.docx
src/diploma_processing/testkit/docx_examples\\2024ВКР038125ПАВЛОВ.docx
src/diploma_processing/testkit/docx_examples\\2024ВКР038342ОРЛОВ.docx
total parsing and calculating stats time: 2.0698225498199463
cmp files: 
src/diploma_processing/testkit/docx_examples\\2024ВКР038112КОТОВ.docx
src/diploma_processing/testkit/docx_examples\\2024ВКР038112КОТОВ.docx
similarity: 100.0000%
cmp files:
src/diploma_processing/testkit/docx_examples\\2024ВКР038112КОТОВ.docx
src/diploma_processing/testkit/docx_examples\\2024ВКР038125ПАВЛОВ.docx
similarity: 4.6945%
cmp files:
src/diploma_processing/testkit/docx_examples\\2024ВКР038112КОТОВ.docx
src/diploma_processing/testkit/docx_examples\\2024ВКР038342ОРЛОВ.docx
similarity: 0.6623%
cmp files:
src/diploma_processing/testkit/docx_examples\\2024ВКР038125ПАВЛОВ.docx
src/diploma_processing/testkit/docx_examples\\2024ВКР038112КОТОВ.docx
similarity: 4.6945%
cmp files:
src/diploma_processing/testkit/docx_examples\\2024ВКР038125ПАВЛОВ.docx
src/diploma_processing/testkit/docx_examples\\2024ВКР038125ПАВЛОВ.docx
similarity: 100.0000%
cmp files:
src/diploma_processing/testkit/docx_examples\\2024ВКР038125ПАВЛОВ.docx
src/diploma_processing/testkit/docx_examples\\2024ВКР038342ОРЛОВ.docx
similarity: 0.6210%
cmp files: 
src/diploma_processing/testkit/docx_examples\\2024ВКР038342ОРЛОВ.docx
src/diploma_processing/testkit/docx_examples\\2024ВКР038112КОТОВ.docx
similarity: 0.6623%
cmp files:
src/diploma_processing/testkit/docx_examples\\2024ВКР038342ОРЛОВ.docx
src/diploma_processing/testkit/docx_examples\\2024ВКР038125ПАВЛОВ.docx
similarity: 0.6210%
cmp files:
src/diploma_processing/testkit/docx_examples\\2024ВКР038342ОРЛОВ.docx
src/diploma_processing/testkit/docx_examples\\2024ВКР038342ОРЛОВ.docx
similarity: 100.0000%
total comparing time: 0.013995170593261719
'''