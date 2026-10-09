#!/usr/bin/env python3
"""윤문 안전장치: 원본과 수정본을 비교해 사실 토큰(숫자, 영문 고유명사, URL, 영상 ID)이 바뀌지 않았는지 검사한다.

사용법: python3 tools/yunmun_guard.py <원본.html> <수정본.html>
- 숫자 토큰 다중집합, 라틴 단어(2자 이상) 다중집합, URL 집합을 비교한다.
- <script type="application/json"> 블록이 모두 JSON으로 파싱되는지 확인한다.
- 태그 개수(열림 태그 이름별)가 같은지 확인한다.
차이가 있으면 목록을 출력하고 종료 코드 1을 돌려준다. 띄어쓰기·조사·어미 변경은 통과한다.
"""
import json, re, sys
from collections import Counter

def load(p):
    return open(p, encoding='utf-8').read()

def text_only(s):
    # 비교 대상: 태그 밖 텍스트 + 속성값 + 스크립트 문자열 전부 (구조는 별도 검사)
    return s

NUM = re.compile(r'(?<![A-Za-z])\d+(?:[.,]\d+)*')
LAT = re.compile(r'[A-Za-z][A-Za-z0-9\-_]+')
URL = re.compile(r'https?://[^\s"\'<>)]+')
TAG = re.compile(r'<([a-zA-Z][a-zA-Z0-9-]*)\b')
JSONB = re.compile(r'<script type="application/json"[^>]*>(.*?)</script>', re.S)

def main(a, b):
    A, Bt = load(a), load(b)
    bad = []
    na, nb = Counter(NUM.findall(A)), Counter(NUM.findall(Bt))
    if na != nb:
        bad.append(('숫자 변경', dict((na - nb).most_common(15)), dict((nb - na).most_common(15))))
    la, lb = Counter(LAT.findall(A)), Counter(LAT.findall(Bt))
    if la != lb:
        bad.append(('영문 토큰 변경', dict((la - lb).most_common(15)), dict((lb - la).most_common(15))))
    ua, ub = set(URL.findall(A)), set(URL.findall(Bt))
    if ua != ub:
        bad.append(('URL 변경', sorted(ua - ub)[:10], sorted(ub - ua)[:10]))
    ta, tb = Counter(TAG.findall(A)), Counter(TAG.findall(Bt))
    if ta != tb:
        bad.append(('태그 구조 변경', dict(ta - tb), dict(tb - ta)))
    for i, blk in enumerate(JSONB.findall(Bt)):
        try:
            json.loads(blk)
        except Exception as e:
            bad.append(('JSON 파싱 실패', i, str(e)[:200]))
    if bad:
        for x in bad:
            print('FAIL', x)
        sys.exit(1)
    print('PASS: 숫자·영문·URL·태그·JSON 모두 보존')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
