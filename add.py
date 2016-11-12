# -*- encoding: UTF-8 -*-
# 此脚本的作用是将add.txt中的词按指定顺序添加到词库(word bank)中
# usage：add_supplement.py (脚本需和add.txt在同一目录下）
# mac下usage为: python add_supplement.py


import re
import os
import sys
import codecs
import subprocess
from time import time
from collections import OrderedDict

# filepath = sys.argv[1]
# win下: filepath = r'c:/Users/line/AppData/Roaming/rime/bzzm.jd.dict.yaml'
# Mac下: filepath = r'/Users/line/Library/Rime/bzzm.jd.dict.yaml'

script_path = os.path.dirname(os.path.abspath(__file__))
wordbank_path = os.path.join(script_path, 'bzzm.jd.dict.yaml')
addbank_path = os.path.join(script_path, 'add.txt')
writeto_path = 'c:/Users/bentley/AppData/Roaming/Rime/bzzm.jd.dict.yaml'
rime_path = 'C:/Program Files (x86)/Rime/weasel-0.9.30/WeaselDeployer.exe'


f = codecs.open(wordbank_path, "r", 'utf-8')
# 用codecs以指定编码打开文件很有效，不然有时会有错误
wordbank_lines = f.readlines()           #readlines()能生成一个list
f.close()

f = codecs.open(addbank_path, "r", 'utf-8')
addbank_lines = f.readlines()
f.close()

for i,line in enumerate(wordbank_lines):
    if re.match(u'^\u4e00', line):
        beginrow = i
        break


# 新建一个 addbank 字典
addbank = {}
for line in addbank_lines:
    if re.match('^/s*$', line):
        continue
    [code, weight, word] = line.split()
    if code in addbank:
        addbank[code].append([word, int(weight)])
    else:
        addbank[code] = [[word, int(weight)]]

# print addbank['eyo']
# 输出 [[u'\u6709', 0], [u'\u82cf', 0]]
# addbank 中的值是一个二元列表，每个字和他对应的权重先组成一个列表，然后有相同编码的字再又组成列表



# 为原词库建成一个字典 wordbank
wordbank = {}
for line in wordbank_lines[beginrow:]:
    if re.match('^/s*$', line):
        break
    [word, code] = line.split();

    if code in wordbank:
        wordbank[code].append(word)
    else:
        wordbank[code] = [word]
    # 将词加到addbank中，好统一排序
    if code in addbank:
        if word not in [v[0] for v in addbank[code]]:
            addbank[code].append([word])

# print wordbank['eyo']  得到  [u'\u82cf']
# print addbank['eyo']   得到  [[u'\u6709', 0], [u'\u82cf']]


# 下面的循环是为字典排序（这是程序的核心），有两个规则：
# 1. 当指定了顺序时严格按指定的顺序来排，若顺序重复，则它们会排在一起，再按它们在码表中的先后顺序来排
# 2. 当没有指定顺序时，在保证指定己指定的顺序不动的情况下按先后顺序排。
for key in addbank:
    sglwords = addbank[key]   # sglwords 为 [['苏', 0], ['你'] ……]
    normlist = [i for i in range(0,len(sglwords))]
    for sglword in sglwords:
        if (len(sglword) == 2 and sglword[1] in normlist):
            normlist.remove(sglword[1])

    position = 0 # 标记上初始的位置关系，这样当序号一样时，按此来排序
    for sglword in sglwords:
        if (len(sglword) == 1):
            sglword.append(normlist[0])
            del normlist[0]
        sglword.append(position)
        position += 1
    # 此时sglwords形式为 [['苏', 1, 0], ['你',0, 1] ……]

    sglwords = sorted(sglwords, key = lambda v: (v[1], v[2]))   # 多重排序，很cool
    addbank[key] = [v[0] for v in sglwords]



wbmerge = dict(wordbank, **addbank)
wbmerge = OrderedDict(sorted(wbmerge.items(), key = lambda d: d[0]))



# 写入
newf = codecs.open(writeto_path, "w", 'utf-8')

for line in wordbank_lines[:beginrow]:
    newf.write(line)

for code, words in wbmerge.iteritems():
    for word in words:
        concatline = word + '\t' + code + '\n'
        newf.write(concatline)

newf.close()


# 执行 weasel 的部署命令
# subprocess.call(['C:/Program Files (x86)/Rime/weasel-0.9.30/WeaselDeployer.exe', '/deploy'])
# os.system("/"C:/Program Files (x86)/Rime/weasel-0.9.30/WeaselDeployer.exe/" /deploy")
os.system("\"" + rime_path + "\" /deploy")

