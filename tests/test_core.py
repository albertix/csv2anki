import pytest
from csv2anki.collection import Collection, Model, ModelDeck, Deck, text
import os

cloze_tmpl = '''{{cloze:正面}}
<===============>
<===============>
{{背面}}'''

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


def test_model(tmpdir):

    # init
    model = Model([('卡片1', "{{正面}}", "{{背面}}")], ['正面', '背面'])

    # from_obj to_obj
    assert Model.from_obj(model.to_obj()) == model

    # test file
    p = tmpdir.join('卡片1.txt')
    p.write_text(tmpl_text, encoding='utf8')
    p1 = tmpdir.join('卡片2.txt')
    p1.write_text(tmpl_text, encoding='utf8')
    # gen_tmpls
    assert Model.gen_tmpls([p.strpath]) == [('卡片1', "{{正面}}", "{{背面}}")]
    assert Model.gen_tmpls([p.strpath, p1.strpath]) == [('卡片1', "{{正面}}", "{{背面}}"), ('卡片2', "{{正面}}", "{{背面}}")]
    assert ('卡片1', "{{正面}}", "{{背面}}") == model.gen_tmpl(tmpl_text, '卡片1')
    # with :rtl
    model1 = Model(Model.gen_tmpls([p.strpath, p1.strpath]), ['正面', '背面:rtl'])
    # gen_tmpls_from_obj
    assert Model.gen_tmpls_from_obj(model1.to_obj()['tmpls']) == model1.tmpls
    # gen flds from obj
    assert Model.gen_flds_from_obj(model1.to_obj()['flds']) == model1.flds
    assert Model.make_obj_flds(model1.flds) == model1.to_obj()['flds']
    assert model1.to_obj()['flds'][1]['rtl'] is True

    # cloze
    pc = tmpdir.join('填空题.txt')
    pc.write_text(cloze_tmpl, encoding='utf8')
    assert Model.clozed(Model.gen_tmpls([p1.strpath, pc.strpath])) == ([('填空题', "{{cloze:正面}}", "{{背面}}")], True)
    assert Model.gen_tmpls([pc.strpath]) == [('填空题', "{{cloze:正面}}", "{{背面}}")]
    assert Model(Model.gen_tmpls([p1.strpath, pc.strpath]), ['正面']).tmpls == [('填空题', "{{cloze:正面}}", "{{背面}}")]


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

