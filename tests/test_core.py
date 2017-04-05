import itertools
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

csv_text = '''正面\t背面:rtl\ttags
啊\te\t1
吧\tb\t1 2
处\ta\t2
啊{{c1::1}}{{c3::2}}\ta\t
c\t\t
'''


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
    obj_flds = [{'font': 'Arial',
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
                'rtl': True,
                'size': 20,
                'sticky': False}]
    assert Model.gen_flds_from_obj(model1.to_obj()['flds']) == model1.flds
    assert Model.make_obj_flds(model1.flds) == model1.to_obj()['flds'] == obj_flds
    assert model1.to_obj()['flds'][1]['rtl'] is True

    # cloze
    pc = tmpdir.join('填空题.txt')
    pc.write_text(cloze_tmpl, encoding='utf8')
    assert Model.clozed(Model.gen_tmpls([p1.strpath, pc.strpath])) == ([('填空题', "{{cloze:正面}}", "{{背面}}")], True)
    assert Model.gen_tmpls([pc.strpath]) == [('填空题', "{{cloze:正面}}", "{{背面}}")]
    assert Model(Model.gen_tmpls([p1.strpath, pc.strpath]), ['正面']).tmpls == [('填空题', "{{cloze:正面}}", "{{背面}}")]
    tmpl_txts = [['default[卡片1].txt',
                  '{{正面}}\n<====================>\n<====================>\n{{背面}}'],
                 ['default[卡片2].txt',
                  '{{正面}}\n<====================>\n<====================>\n{{背面}}']]
    assert Model.make_txt_tmpls(model1) == tmpl_txts
    assert model1.to_tmpls_css_txt()[0] == tmpl_txts
    assert model1.to_tmpls_css_txt()[1] == ["{}.css".format(model1.model_name), model1.css]


def test_deck():
    deck = Deck("测试")
    assert deck == Deck.from_obj(deck.to_obj())


def test_model_deck(tmpdir):
    # cloze
    pc = tmpdir.join('填空题.txt')
    pc.write_text(cloze_tmpl, encoding='utf8')

    # from csv
    model_deck = ModelDeck.from_csv_text(csv_text, Model.gen_tmpls([pc.strpath]), csv_name="填空题[测试]")
    assert model_deck.model == Model(Model.gen_tmpls([pc.strpath]), ["正面", "背面:rtl"], model_name="填空题")
    assert model_deck.deck == Deck("测试")
    assert model_deck.has_tag is True
    # to csv
    assert ("填空题[测试].csv", csv_text) == model_deck.to_csv_text()

    # to notes_cards
    start = 100000
    n_gen = itertools.count(start)
    c_gen = itertools.count(start)
    model_deck.model.mid = start
    model_deck.deck.did = 1
    notes_obj, cards_obj = model_deck.to_notes_cards_objs(n_gen, c_gen, start)
    assert len(notes_obj) == len(cards_obj) - 1
    assert cards_obj[3][3] == 0
    assert cards_obj[4][3] == 2


def test_collection():
    # Collection.from_zip()
    col = Collection.from_zip('tests/all.apkg')
