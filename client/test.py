import unittest


class TestPackage(unittest.TestCase):
    def test_module1(self):
        #import mypackage
        from mypackage import module1
        self.assertTrue(module1.hello())


if __name__ == '__main__':
    unittest.main()
