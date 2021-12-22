import mdform
from flask_mdform import formatters
from flask_mdform.testsuite import data_test


def test_flask_wtf():
    html, _ = mdform.parse(data_test.TEXT_1, formatters.flask_wtf)
    assert html == data_test.JINJA_WTF_1


def test_flask_wtf_bs4():
    html, _ = mdform.parse(data_test.TEXT_1, formatters.flask_wtf_bs4("jQuery"))
    assert html == data_test.JINJA_WTF_BS4_1


def test_flask_wtf_bs4_nolabel():
    html, _ = mdform.parse(data_test.TEXT_3, formatters.flask_wtf_bs4("jQuery"))
    assert html == data_test.JINJA_WTF_BS4_3
