from unittest import TestCase, expectedFailure


class SampleTestCase(TestCase):

    def test_pass(self):
        self.assertEqual(1, 1)

    @expectedFailure
    def test_fail(self):
        self.assertEqual(1,0)