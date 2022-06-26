from unittest import expectedFailure
from django.test import TestCase

from ..factories import SampleModelFactory


class SampleTestCase(TestCase):

    def test_sample(self):
        raw_data = SampleModelFactory(
            content__0__char1__value="Char Block 1"
        ).content.raw_data

        self.assertEqual(raw_data[0]["type"], "char1")

