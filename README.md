# 法律法条信息抽取工具

## Request url
句子标注：

URL: http://host:8484/tagging (只支持http， 不能用https)
请求格式：{"text":""}

句子拆分：
URL: http://host:8484/splitting 
请求格式：{"text":""}


## Request data
application/json

例如：{"1111":"违反本条例的规定，有下列情形之一的，由国务院交通交通主管部门或者省、自治区、直辖市人民政府交通主管部门依据职权，责令改正，并根据情节轻重，处５万元以上２０万元以下的罚款"}

## Response data
{'1111': {'condition': '违反本条例的规定', 'subject': [], 'behavior': [], 'result': '由国务院交通主管部门或者省、自治区、直辖市人民政府交通主管部门依据职权，责令改正，并根据情节轻重，处５万元以上２０万元以下的罚款'}}

## TF-IDF 计算一篇文档与其他文档的相似性
1、计算其他docs的每篇doc的关键词的tfidf值

2、计算one doc中的关键词的tfidf值

3、将每个doc用向量表示，向量中的元素为tfidf值

4、计算one doc表示的向量与其他doc的向量之间的余弦相似度C

5、C值越大表明两篇doc越相似

## python 安装离线模块

pip3 download -d C:\Users\JFD\Desktop\packages-whl -r requirements.txt

编译源码：

1、pycparser-2.18.tar.gz 解压到 pycparser-2.18

2、pip wheel --wheel-dir=e:\ChromeDownload E:\ChromeDownload\pycparser-2.18

生成文件：pycparser-2.18-py2.py3-none-any.whl