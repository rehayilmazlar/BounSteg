import os
import unittest
from PyQt5.QtWidgets import QApplication
from boun_steg import ImageProcess, EmbedDialog

########################################################################
class TestImageProcess(unittest.TestCase):
    ''' set dialogue components and files for testing ''' 
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
        ''' check if is_corrupt method properly detects corrupt files '''
        # try a regular file, should return False
        result = ImageProcess.is_corrupt(self.regular_file)
        self.assertFalse(result)
        
        # try a corrupt file, should return True, also error MessageBox should appear.
        
        self.assertTrue(ImageProcess.is_corrupt(self.corrupt_file1))
        
        # try a corrupt file, should return True, also error MessageBox should appear.
        
        self.assertTrue(ImageProcess.is_corrupt(self.corrupt_file2))
        

    #----------------------------------------------------------------------
    
    def test_hide_text(self):
        ''' hides "This is a test message!" in an image and checks if the resulting images has the embedded data. '''
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
        ''' embeds a file in an image, then checks if the file can be extracted from the image. '''
        test_file_create = './test_files/test_file.png'
        test_file_too_big = './test_files/test_file2.png'
        
        ImageProcess.is_corrupt(self.regular_file)
        ImageProcess.hide_file("./test_files/boun_vision.txt")
        ImageProcess.save_image(test_file_create)
        self.assertTrue(os.path.exists(test_file_create))
        
        ImageProcess.is_corrupt(test_file_create)
        result = ImageProcess.show_message()[1]
        # resulting file has the right name?
        self.assertEqual(result, "boun_vision.txt" )
        os.remove(test_file_create)
        
        ImageProcess.is_corrupt(self.regular_file)
        ImageProcess.hide_file("./test_images/boun.png")
        # is there a resulting file? there should not be.
        self.assertFalse(os.path.exists(test_file_create))

        
        
    #----------------------------------------------------------------------
    
    def test_show_message(self):
        ''' checks if show_message function works properly, try files with or without secret data and confirm right result is received. '''
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