from typing import Optional
from typing import Union
import collections, re

import collections
import re
from typing import Optional, Union

def get_vocab(corpus: list[str]) -> dict[str, int]:
    vocab = collections.defaultdict(int)
    for line in corpus:
        words = line.split()
        for word in words:
            vocab[word] += 1
    return vocab

def get_stats(vocab: dict[str, int]):
    pairs = collections.defaultdict(int)
    for word, freq in vocab.items():
        symbols = word.split()
        for i in range(len(symbols)-1):
            pairs[symbols[i],symbols[i+1]] += freq
    return pairs

def merge_vocab(pair, v_in):
    v_out = {}
    bigram = re.escape(' '.join(pair))
    p = re.compile(r'(?<!\\S)' + bigram + r'(?!\\S)')
    for word in v_in:
        w_out = p.sub(''.join(pair), word)
        v_out[w_out] = v_in[word]
    return v_out

def merge_n_best(pairs, vocab, n):
    if vocab is None:
        raise ValueError("vocab is not initialized. Train tokenizer first!")
    
    # n 개의 가장 높은 빈도를 가진 pair 선택
    best_n = sorted(pairs, key=pairs.get, reverse=True)[:n]
    
    # 이미 선택된 문자를 저장하는 집합
    selected_chars = set()

    # 중복되지 않는 새로운 pair를 찾아서 merge
    num_merged = 0  # 중복되지 않아서 merge한 pair의 수를 계산하는 변수
    for best in best_n:
        if num_merged >= n:  # 이미 목표한 수만큼 merge 했으면 종료
            break
        if not any(char in selected_chars for char in best):
            vocab = merge_vocab(best, vocab)
            selected_chars.update(best)
            num_merged += 1
    
    return num_merged, vocab

class BPETokenizer:
    # corpus: 학습에 사용할 말뭉치
    # vocab: 학습된 vocab
    def __init__(self, corpus: Optional[Union[list[str], str]] = None) -> None:
        if isinstance(corpus, list):
            self.corpus = corpus
        else:
            self.corpus = [corpus]
        self.vocab = None
        
    # text: 토큰화할 문장
    # padding: True일 경우 padding
    # max_length: 최대 길이
    # return: 토큰화된 문장
    def __call__(self, text: Union[list[str], str], padding: bool = False, max_length: Optional[int] = None) -> Union[list[list[int]], list[int]]:
        return self.tokenize(text, padding, max_length)
    
    # self.corpus에 corpus 추가
    def add_corpus(self, corpus: Union[list[str], str]) -> None:
        if isinstance(corpus, list):
            self.corpus += corpus
        else:
            self.corpus += [corpus]
    
    # n_iter: merge할 횟수
    def train(self, n_iter: int) -> None:
        vocab = get_vocab(self.corpus)
        # n_iter만큼 merge
        for i in range(n_iter):
            pairs = get_stats(vocab)
            num_merged, vocab = merge_n_best(pairs, vocab, n_iter)
            # merge한 갯수를 i에 더해줌
            i += num_merged
        self.vocab = vocab
        
    # text: 토큰화할 문장
    # padding: True일 경우 padding
    # max_length: 최대 길이
    # return: 토큰화된 문장
    def tokenize(self, text: Union[list[str], str], padding: bool = False, max_length: Optional[int] = None) -> Union[list[list[int]], list[int]]: 
        if self.vocab is None:
            raise ValueError("Train tokenizer first!")
        tokens = []
        # 여러 문장이 들어올 경우
        if isinstance(text, list):
            # 각 문장을 띄어쓰기 단위로 split
            for sentence in text:
                tokenized_words = []
                for word in sentence.split():
                    if word in self.vocab:
                        tokenized_words.append(self.vocab[word])
                    else:
                        tokenized_words.append(self.vocab['<unk>'])
                tokens.append(tokenized_words)
            # max_length가 지정되어 있으면 max_length만큼 자르기
            if max_length is not None:
                for i in range(len(tokens)):
                    if len(tokens[i]) > max_length:
                        tokens[i] = tokens[i][:max_length]
            # padding이 True이면 padding
            if padding:
                tokens = self._padding(tokens)
                
        # 한 문장이 들어올 경우
        else:
            # 띄어쓰기 단위로 split
            for word in text.split():
                if word in self.vocab:
                    tokens.append(self.vocab[word])
                else:
                    tokens.append(self.vocab['<unk>'])
            # max_length가 지정되어 있으면 max_length만큼 자르기
            if max_length is not None and len(tokens) > max_length:
                tokens = tokens[:max_length]

        return tokens

    def _padding(self, tokens):
        # 가장 긴 문장의 길이를 구함
        max_len = max(len(sentence) for sentence in tokens)
        # 가장 긴 문장의 길이에 맞춰 padding
        padded_tokens = []
        for sentence in tokens:
            padding = [0] * (max_len - len(sentence))
            padded_tokens.append(sentence + padding)
            
        return padded_tokens
    
    
class WordTokenizer:
    # corpus: 학습에 사용할 말뭉치
    # vocab: 학습된 vocab
    def __init__(self, corpus: Optional[Union[list[str], str]] = None) -> None:
        if isinstance(corpus, list):
            self.corpus = corpus
        else:
            self.corpus = [corpus]
        self.vocab = None
        
    # text: 토큰화할 문장
    # padding: True일 경우 padding
    # max_length: 최대 길이
    # return: 토큰화된 문장
    def __call__(self, text: Union[list[str], str], padding: bool = False, max_length: Optional[int] = None) -> Union[list[list[int]], list[int]]:
        return self.tokenize(text, padding, max_length)
    
    # self.corpus에 corpus 추가    
    def add_corpus(self, corpus: Union[list[str], str]) -> None:
        if isinstance(corpus, list):
            self.corpus += corpus
        else:
            self.corpus += [corpus]
    
    # vocab 생성
    def train(self, n_iter: Optional[int] = None) -> None:
        self.vocab = collections.defaultdict(int)
        # corpus를 띄어쓰기 단위로 split
        for sentence in self.corpus:
            for word in sentence.split():
                self.vocab[word] += 1

    # text: 토큰화할 문장
    # padding: True일 경우 padding
    # max_length: 최대 길이
    # return: 토큰화된 문장
    def tokenize(self, text: Union[list[str], str], padding: bool = False, max_length: Optional[int] = None) -> Union[list[list[int]], list[int]]: 
        if self.vocab is None:
            raise ValueError("Train tokenizer first!")
        tokens = []
        if isinstance(text, list):
            for sentence in text:
                tokenized_words = []
                for word in sentence.split():
                    if word in self.vocab:
                        tokenized_words.append(self.vocab[word])
                    else:
                        tokenized_words.append(self.vocab['<unk>'])
                tokens.append(tokenized_words)
            if max_length is not None:
                for i in range(len(tokens)):
                    if len(tokens[i]) > max_length:
                        tokens[i] = tokens[i][:max_length]
            if padding:
                tokens = self._padding(tokens)
        else:
            for word in text.split():
                if word in self.vocab:
                    tokens.append(self.vocab[word])
                else:
                    tokens.append(self.vocab['<unk>'])
            if max_length is not None and len(tokens) > max_length:
                tokens = tokens[:max_length]

        return tokens
    
    def _padding(self, tokens):
        max_len = max(len(sentence) for sentence in tokens)

        padded_tokens = []
        for sentence in tokens:
            padding = [0] * (max_len - len(sentence))
            padded_tokens.append(sentence + padding)

        return padded_tokens