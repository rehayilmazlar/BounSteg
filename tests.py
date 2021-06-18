import os
import unittest
import PIL
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication
from PyQt5.Qt import QKeySequence
from PyQt5.Qt import Qt
from boun_steg import ImageProcess, EmbedDialog
from PyQt5.QtTest import QTest

########################################################################
class TestImageProcess(unittest.TestCase):
    
    regular_file = './test_images/ataturk.png'
    secret_file = './test_images/ataturk_secret.png'
    embedded_file = './test_images/ataturk_file.png'
    corrupt_file1 = './test_images/corrupt_image.bmp'
    corrupt_file2 = './test_images/corrupt_image.png'
    
    #----------------------------------------------------------------------
    def setUp(self):
        self.app = QApplication([])
        self.ui = EmbedDialog()


    #----------------------------------------------------------------------
    def test_is_corrupt(self):
        
        # try a regular file, should return False
        result = ImageProcess.is_corrupt(self.regular_file)
        self.assertFalse(result)
        
        # try a corrupt file, should return True, also error MessageBox should appear.
        
        self.assertTrue(ImageProcess.is_corrupt(self.corrupt_file1))
        
        # try a corrupt file, should return True, also error MessageBox should appear.
        
        self.assertTrue(ImageProcess.is_corrupt(self.corrupt_file2))
        

    #----------------------------------------------------------------------
    
    def test_hide_text(self):
        ImageProcess.is_corrupt(self.regular_file)
        ImageProcess.hide_text("This is a test message!")
        ImageProcess.save_image("./test_hide.png")
        self.assertTrue(os.path.exists("./test_hide.png"))
        
        self.assertFalse(ImageProcess.is_corrupt("./test_hide.png"))
        result = ImageProcess.show_message()
        self.assertEqual(result, "This is a test message!")
        os.remove("./test_hide.png")
        
    #----------------------------------------------------------------------
    def test_hide_file(self):
        test_file_create = './test_files/test_file.png'
        
        ImageProcess.is_corrupt(self.regular_file)
        ImageProcess.hide_file("./test_files/boun_vision.txt")
        ImageProcess.save_image(test_file_create)
        self.assertTrue(os.path.exists(test_file_create))
        
        ImageProcess.is_corrupt(test_file_create)
        result = ImageProcess.show_message()[1]
        self.assertEqual(result, "boun_vision.txt" )
        os.remove(test_file_create)
        
    #----------------------------------------------------------------------
    
    def test_show_message(self):
        # file with a secret message
        self.assertFalse(ImageProcess.is_corrupt(self.secret_file))
        result = ImageProcess.show_message()
        self.assertEqual(result, "“Türk, öğün, çalış, güven.”\n\nMustafa Kemal ATATÜRK")
        
        # file without a secret message
        self.assertFalse(ImageProcess.is_corrupt(self.regular_file))
        result = ImageProcess.show_message()
        self.assertEqual(result, None)

        # file with an embedded file
        self.assertFalse(ImageProcess.is_corrupt(self.embedded_file))
        result = ImageProcess.show_message()[1]
        self.assertEqual(result, "boun_vision.txt" )
        
    #----------------------------------------------------------------------
    

        
    
        


    #----------------------------------------------------------------------
    def tearDown(self):
        pass