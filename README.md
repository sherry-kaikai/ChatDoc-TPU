# ChatDoc-TPU

这个项目是基于[ChatGLM3-TPU](https://github.com/sophgo/sophon-demo/tree/release/sample/ChatGLM3)实现的文档对话工具。项目可在BM1684X上独立部署运行。


## 介绍
该项目的主要目标是通过使用自然语言来简化与文档的交互，并提取有价值的信息。此项目使用LangChain和ChatGLM2构建，以向用户提供流畅自然的对话体验。


## 特点

- 完全本地推理。
- 支持多种文档格式PDF, DOCX, TXT。
- 与文档内容进行聊天，提出问题根据文档获得相关答案。
- 用户友好的界面，确保流畅的交互。


## 安装

按照以下步骤，可以将这个项目部署到SophGo的设备上

1. 克隆代码:
```bash
git clone https://github.com/wangyifan2018/ChatDoc-TPU.git
```
2. 进入项目路径:
```bash
cd ChatDoc-TPU
```
3. 安装依赖
```bash
# 已在 python 3.9 测试，可在虚拟环境中运行(venv、conda)
virtualenv glm

source glm/bin/activate

pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```
此外还依赖新版本sail，安装方法可参考[sail安装](https://github.com/sophgo/sophon-demo/blob/release/sample/ChatGLM3/python/README.md#1-%E7%8E%AF%E5%A2%83%E5%87%86%E5%A4%87)

4. 下载模型和配置文件
```bash
# install if need
sudo apt install unzip

# 模型文件在chatdoc目录下解压
# 链接: https://pan.baidu.com/s/1s71b4THQu--RZfmTwNwU3Q 提取码: nk88
unzip models.zip

# nltk_data 文件夹需要放置在 ~ 目录下
# 链接: https://pan.baidu.com/s/1C80ohxNm9kaat4Sek3ooGg 提取码: ksy3
unzip nltk_data.zip
mv nltk_data ~
```

## 项目结构树
```
|-- chatdoc
    |-- data
        |-- db_tpu        -- 知识库持久化目录
        |-- uploaded      -- 已上传文件目录
    |-- models
        |-- llm_model     -- LLM 模型
        |-- bert_model    -- BERT 模型
    |-- src
        |-- chatbot.py    -- ChatDoc业务逻辑脚本
        |-- chat.py       -- Python调用chatglm3
        |-- api.py        -- API服务脚本
    |-- embedding_tpu     -- 文本嵌入模型TPU版本
    |-- static            -- README中图片文件
    |-- README.md         -- README
    |-- config.ini        -- 推理模型配置文件
    |-- requirements.txt  -- 项目依赖
    |-- run.sh            -- 启动脚本
    |-- web_demo_st.py    -- 页面交互脚本
```

## 启动

1. 激活环境 `source glm/bin/activate`
2. 配置 `config.ini` 中的模型地址
3. 启动tpu版的embedding程序`bash run.sh`


## 操作说明

![Alt text](<./static/img1.png>)

### 界面简介
ChatDoc由控制区和聊天对话区组成。控制区用于管理文档和知识库，聊天对话区用于输入消息接受消息。

上图中的10号区域是ChatDoc当前选中的文档。若10号区域为空，即ChatDoc没有选中任何文档，仍在聊天对话区与ChatDoc对话，则此时的ChatDoc是一个单纯依托ChatGLM2的ChatBot。

### 上传文档
点击`1`选择要上传的文档，然后点击按钮`4`构建知识库。随后将embedding文档，完成后将被选中，并显示在10号区域，接着就可开始对话。我们可重复上传文档，embedding成功的文档均会进入10号区域。

### 持久化知识库
10号区域选中的文档在用户刷新或者关闭页面时，将会清空，而如何能保存这些已经embedding的文档，我们可以持久化知识库，在下次进入无需embedding计算即可加载知识库。具体做法是，在10号区域不为空的情况下，点击按钮`5`即可持久化知识库，知识库的名称是所有文档名称以逗号连接而成。

### 导入知识库

进入ChatDoc我们可以从选择框`2`查看目前以持久化的知识库，选中我们需要加载的知识库后，点击按钮`3`导入知识库。完成后即可开始对话。注意cpu版的知识库和tpu版的知识库不能混用，若启动tpu版程序，则不能加载已持久化的cpu版知识库，若启动cpu版程序，则不能加载已持久化的tpu版知识库。

### 删除知识库

当我们需要删除本地已经持久化的知识库时，我们可从选择框`2`选择我们要删除的知识库，然后点击按钮`6`删除知识库。

### 重命名知识库

![Alt text](<./static/img2.png>)

由于知识库的命名是由其文档的名称组合而来，难免造成知识库名称过长的问题，ChatDoc提供了一个修改知识库名称的功能，选择框`2`选择我们要修改的知识库，然后点击按钮`9`重命名知识库，随后ChatDoc将弹出一个输入框和一个确认按钮，如上图。在输出框输入我们修改至的名称，然后点击确认重命名按钮。

### 清楚聊天记录

点击按钮`7`即可清楚聊天对话区聊天记录。其他不受影响。

### 移除选中文档

点击按钮`8`将清空10号区域，同时清楚聊天记录。