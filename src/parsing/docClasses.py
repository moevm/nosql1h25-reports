class DocSection():
    def __init__(self):
        self.id = None
        self.title = None
        self.count_words = None
        self.count_symbols = None
        self.saturation = None # насыщенность, не знаю, мне не нравится вырадение "водность"
                               # предложение по переименованию принимаются к рассмотрению

        self.top_words = None
        self.structure = [] # если есть какие-то подразделы - то тут будет список
                            # с ними, по сути список объектов разделов (DocSectoin)
        self.upper = None
        self.level = None
        
        self.text = ''
        # таблицы и изображения договорились не читать
        # хотя на счёт таблиц не уверен, что это хорошая идея,
        # можно попробовать потом будет как-то учесть их


class Doc:
    def __init__(self):
        self.id = None
        self.title = None
        self.author = None
        self.sci_director = None # научный реководитель
        self.year = None
        self.key_words = None # это должна быть запись, где будут перечислены задачи,
                              # по которым мы потом будем считать раскрытость темы
                              # по сути список слов, т.е. даже не предложений, а уже слов

        # полчучить напрамую количество страниц в документе не получится
        # для этого придётся считать высоту каждой строчки текста
        # по отношению к длине и высоте страницы
        # очень муторно считать

        # self.count_pages = None

        self.count_wolds = None
        self.count_symbols = None
        self.date_of_load = None
        self.structure = [] # структура всего документа - список разделов,
                            # стостоит из объектов разделов (DocSectoin)
        
        self.disclosure = None # раскрытость темы