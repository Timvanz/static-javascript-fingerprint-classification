class Script:

    def __init__(self, file_path, template_fingerprinting_functions):
        self.file_path = file_path
        self.fp_functions = template_fingerprinting_functions
        self.__count__()

    def get_content(self):
        return open(self.file_path, 'r').read()

    def __count__(self):
        code = open(self.file_path, 'r').read()
        for js_function in self.fp_functions:
            self.fp_functions[js_function][1] = code.count(js_function)

    def print_statistics(self, sorting):
        print("Current statistics for: " + self.file_path)
        none_found = True

        if sorting:
            s = [(k, self.fp_functions[k]) for k in
                 sorted(self.fp_functions, key=self.fp_functions.get,
                        reverse=True)]
            none_found = True
            for k, v in s:
                if v != 0:
                    none_found = False
                    print("{0}\t{1}".format(v[1], k))
        else:
            for k, v in self.fp_functions.items():
                if v != 0:
                    none_found = False
                    print("{0}\t{1}".format(v[1], k))
        if none_found:
            print('No suspicious JS calls found.')
