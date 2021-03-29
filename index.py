import os
import re
import string
from nltk.stem import PorterStemmer


class Indexer:
    def __init__(self):
        self.inverted_index = {}
        self.positional_index = {}
        self.stop_words = []
        # self.tokenize_regex = r"[\!\"\#\$\%\&\(\)\*\+\-\.\/\:\;\<\=\>\?\@\[\]\^\_\`\{\|\}\~\\ —]"
        self.tokenize_regex = r"[^\w',]"
        self.doc_count = 0

    # read stopwords from file
    def read_stop_words(self, path):
        self.stop_words = []
        with open(path, 'r') as f:
            for line in f:
                for word in line.split():
                    self.stop_words.append(word)

    # read all documents in a path and tokenize and index the terms
    def read_file(self, path):
        self.read_stop_words('files/Stopword-List.txt')
        # generate file list from directory provided
        file_list = os.listdir(path)
        self.doc_count = len(file_list)
        file_list = sorted(file_list, key=lambda x: int(
            "".join([i for i in x if i.isdigit()])))

        token_file = open('files/tokens.txt', 'w')  # file to store tokens
        ps = PorterStemmer()
        # open every document, and index the words in them
        for doc_id, file_name in enumerate(file_list):
            word_pos = 0
            with open(path + file_name, 'r' , encoding="utf-8") as file_data:
                token_file.write("\nDOC-" + str(doc_id+1) + '#\n')
                for line in file_data:
                    # split and tokenize word by given characters
                    for word in re.split(self.tokenize_regex, line):
                        # remove trailing commas and apostrophes
                        word = re.sub('[,\'\n]', '', word)
                        word = word.lower()
                        # apply porter stemer algo to each word
                        word = ps.stem(word)
                        if word:
                            # add to positional index with stop words included
                            self.positional(word, word_pos, doc_id+1)
                            word_pos += 1
                            token_file.write(word + ' ')
                            # add to invered index excluding stop words
                            if word not in self.stop_words:
                                self.inverted(word, doc_id+1)

    # write positional and inverted index to file
    def index_to_file(self, path):
        inverted_index_file = open(path+'Inverted_index.txt', 'w')
        positional_index_file = open(path+'Positional_index.txt', 'w')
        for elem in self.inverted_index:
            inverted_index_file.write(elem + ':\n' + str(self.inverted_index[elem]) + '\n\n')
        for elem in self.positional_index:
            positional_index_file.write('\n' + elem + ': \n')
            for doc in self.positional_index[elem]:
                positional_index_file.write(str(doc) + ': ' +
                                   str(self.positional_index[elem][doc]) + '\n')

    # insert token to inverted index
    def inverted(self, word, doc_id):
        if word not in self.inverted_index:  # if word not present then add new entry to dict
            self.inverted_index[word] = []
            self.inverted_index[word].append(doc_id)
        elif doc_id not in self.inverted_index[word]:
            self.inverted_index[word].append(doc_id)

    # insert token to positional index
    def positional(self, word, word_pos, doc_id):
        if word in self.positional_index:  # if word present then append to dict
            if not self.positional_index[word].get(doc_id):
                self.positional_index[word][doc_id] = []
            self.positional_index[word][doc_id].append(word_pos)
        else:  # if word absent then add a new entry to dict
            self.positional_index[word] = {}
            self.positional_index[word][doc_id] = []
            self.positional_index[word][doc_id].append(word_pos)

    # search and compare query with all documents
    def search_query(self, query):
        ans = []
        query = query.lower()
        # if proximity query
        if not any(elem in ['and', 'or', 'not'] for elem in query.split()):
            # return nothing if 0 term
            if len(query.split()) == 0:
                return ans
            # return from inverted index if 1 term
            elif len(query.split()) == 1:
                ps = PorterStemmer()
                q1 = ps.stem(query.split()[0])
                return self.inverted_index.get(q1, [])
            word_list = query.split()
            space = 0
            # if no proximity given then proximity distance = 1
            if len(word_list) == 2:
                space = 1
            # if proximity given then proximity distance = dist + 1
            else:
                word_list[2] = word_list[2].replace('/', '')
                space = int(word_list[2]) + 1
            ans = self.proximity_query(word_list[0], word_list[1], space)
        # if boolean query then covert infix to postfix and then evaluate
        else:
            postfix = self.inverted_query(query)
            ans = self.evaluate_postfix(postfix)
        return ans

    # apply query using /n proximity operator
    def proximity_query(self, q1, q2, space):
        ps = PorterStemmer()
        q1 = ps.stem(q1)
        q2 = ps.stem(q2)
        ans = []
        # if terms exist then find if they are separated by distance (space)
        if self.positional_index.get(q1) != None and self.positional_index.get(q2) != None:
            for doc in self.positional_index[q1]:
                if doc in self.positional_index[q2]:
                    for pos in self.positional_index[q1][doc]:
                        if pos + space in self.positional_index[q2][doc]:
                            if doc not in ans:
                                ans.append(doc)
        return ans

    # convert infix to postfix for evaluation of boolean query
    def inverted_query(self, query):
        query = query.replace('(', ' ( ')
        query = query.replace(')', ' ) ')
        term = []
        operator = []
        precedence = {'not': 3, 'and': 2, 'or': 1, '(': 0, ')': 0}
        for word in query.split():
            # append if it is a term
            if word not in precedence:
                term.append(word)
            elif word == '(':
                operator.append(word)
            # pop every operator until open bracket is found
            elif word == ')':
                top = operator.pop()
                while top != '(':
                    term.append(top)
                    top = operator.pop()
            # if operator, then push if precedence lower, else pop operator to expression
            else:
                while operator and precedence[word] <= precedence[operator[-1]]:
                    term.append(operator.pop())
                operator.append(word)
        # pop every operator to expression in the end
        while operator:
            term.append(operator.pop())
        return term

    # calculate answer for postfix expression provided
    def evaluate_postfix(self, expression):
        ps = PorterStemmer()
        ans = []
        for term in expression:
            # if term is 'and' then apply operator on top two terms
            if term == 'and':
                list1 = ans.pop()
                list2 = ans.pop()
                if len(list2) > len(list1):
                    list1, list2 = list2, list1
                ans.append(self.and_query(list1, list2))
            # if term is 'or' then apply operator on top two terms
            elif term == 'or':
                list1 = ans.pop()
                list2 = ans.pop()
                ans.append(self.or_query(list1, list2))
            # if term is 'not' then apply operator on only 1 top term
            elif term == 'not':
                list1 = ans.pop()
                ans.append(self.not_query(list1))
            # if not operator then keep apending to stack
            else:
                temp_str = ps.stem(term)
                ans.append(self.inverted_index.get(temp_str, []))
        return ans.pop()

    # and operation
    def and_query(self, list1, list2):
        ans = []
        i = 0
        j = 0
        while i < len(list1) and j < len(list2):
            if list1[i] < list2[j]:
                i += 1
            elif list1[i] > list2[j]:
                j += 1
            else:
                ans.append(list1[i])
                i += 1
                j += 1
        return ans

    # or operation
    def or_query(self, list1, list2):
        ans = list1 + list2
        ans = list(dict.fromkeys(ans))
        ans = sorted(ans)
        return ans

    # not operation
    def not_query(self, list1):
        ans = []
        for i in range(self.doc_count):
            if i not in list1:
                ans.append(i)
        return ans

