## 说明

通过读入指定的`.csv`、`.css`等文件，转换为符合Anki标准的`.apkg`文件。

## Class Object 转换

Class:  Model, Collection, Package
Object: dict, list, tuple
Inport: csv, txt, css, bit, apkg
Export: csv, txt, css, bit, apkg

## Anki简介



## 结构

Anki将数据分为三个层次：记忆库(col)、笔记(note)、记忆字段(field)以及展示用的卡片(card)。

     /- - - - - - - - - col- - - - -\
    |--model                         |
       |--note- - - -=>card<=- deck--|
          |--field -/


记忆库(col)包含全部的配置信息，包括卡片(card)的格式，笔记(note)中记忆字段(field)的个数等。

笔记(note)不为用户所见，是一组记忆字段(field)的总和，一个note可生成若干个card。

记忆字段(field)是基本的记忆元素，对英文单词笔记(note)而言，单词、释义、音标、音频是四个field，可以构成一个note。

卡片(card)是用户看到的最终产品，分正面和背面，通过col中储存的css等card格式信息，将note中field的具体值放进card，形成用户可见的卡片。

    例
    col:  {fields: [单词 释义], 正面: [单词], 背面: [单词, 释义] }
    note: [{one, 一}, {two, 二}]
    card: [{正面: [one], 背面: [one, 一]},
           {正面: [two], 背面: [two, 二]}]


## 参考

[apkg格式参考](http://decks.wikia.com/wiki/Anki_APKG_format_documentation)
[Database Structure](https://github.com/ankidroid/Anki-Android/wiki/Database-Structure)
