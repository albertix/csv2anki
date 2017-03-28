import pytest
from csv2anki.collection import Collection, Model, ModelDeck, Deck, text
import os


tmpl_text = '''{{正面}}
<===============>
<===============>
{{背面}}'''

csv_text = '''文字	text	tags
啊	e	1
吧	b	1 2
处	a	2
啊啊 啊
c		'''


def test_model_gen_tmpl():
    tmpl = Model.gen_tmpl(tmpl_text=tmpl_text, tmpl_name="卡片1")
    assert tmpl == ('卡片1', '{{正面}}', '{{背面}}')


def test_model():
    model = Model([('卡片1', "{{正面}}", "{{背面}}")], ['正面', '背面'])
    deck = Deck('测试')
    model_deck = ModelDeck([['a', 'b'], ['c', 'd']], model, deck)
    model_deck1 = ModelDeck.from_csv_text('正面\t背面\na\tb\nc\td\n', [('卡片1', "{{正面}}", "{{背面}}")], '[测试]')
    assert model_deck == model_deck1


def test_model_deck():
    model = Model([('卡片1', "{{正面}}", "{{背面}}")], ['正面', '背面'], model_name="aaa")
    deck = Deck('测试')
    model_deck = ModelDeck([['a', 'b'], ['c', 'd']], model, deck)
    txt = model_deck.to_csv_text()
    model_deck1 = ModelDeck.from_csv_text(txt, [('卡片1', "{{正面}}", "{{背面}}")], csv_name="aaa[测试]")
    assert model_deck == model_deck1


def test_model_make_obj_flds():
    model = Model([('卡片1', "{{正面}}", "{{背面}}")], ['正面', '背面'])
    obj_flds = Model.make_obj_flds(model.flds)
    assert obj_flds == [{'font': 'Arial',
                         'media': [],
                          'name': '正面',
                          'ord': 0,
                          'rtl': False,
                          'size': 20,
                          'sticky': False},
                         {'font': 'Arial',
                          'media': [],
                          'name': '背面',
                          'ord': 1,
                          'rtl': False,
                          'size': 20,
                          'sticky': False}]
    model = Model([('卡片1', "{{正面}}", "{{背面}}")], ['正面:rtl', '背面'])
    obj_flds = Model.make_obj_flds(model.flds)
    assert obj_flds == [{'font': 'Arial',
                         'media': [],
                         'name': '正面',
                         'ord': 0,
                         'rtl': True,
                         'size': 20,
                         'sticky': False},
                        {'font': 'Arial',
                         'media': [],
                         'name': '背面',
                         'ord': 1,
                         'rtl': False,
                         'size': 20,
                         'sticky': False}]

