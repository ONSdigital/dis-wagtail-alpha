from django.test import TestCase

from ..templatetags.querystring_modify import querystring_modify


class QueryStringModifyTemplateTagTestCase(TestCase):
    def test_none_parameters_are_discarded(self):
        self.assertEqual(
            querystring_modify(None, {}, foo="VAL", bar=None, baz=1),
            "?foo=VAL&baz=1",
        )

    def test_utm_parameters_are_discarded(self):
        self.assertEqual(
            querystring_modify(None, {}, foo="VAL", utm_source="test"),
            "?foo=VAL",
        )
