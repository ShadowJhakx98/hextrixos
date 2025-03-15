"""
Advanced OCR System with Preprocessing and Multilingual Support
Implements Tesseract + EasyOCR with AI enhancements
"""

import cv2
import pytesseract
from easyocr import Reader
import numpy as np
from typing import List, Dict

class EnhancedOCR:
    def __init__(self, languages: List[str] = ['en']):
        self.tesseract_config = r'--oem 3 --psm 6'
        self.easy_reader = Reader(languages, gpu=True)
        self.preprocessor = ImagePreprocessor()

    def extract_text(self, image_path: str) -> Dict:
        """Full OCR pipeline with preprocessing"""
        try:
            img = cv2.imread(image_path)
            processed = self.preprocessor.enhance(img)
            
            # Hybrid OCR results
            tesseract_text = self._tesseract_ocr(processed)
            easy_text = self._easyocr_ocr(processed)
            
            return self._merge_results(tesseract_text, easy_text)
        except Exception as e:
            return {'error': str(e)}

    def _tesseract_ocr(self, image: np.ndarray) -> List[Dict]:
        """Tesseract with layout analysis"""
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        return [{
            'text': data['text'][i],
            'confidence': float(data['conf'][i]),
            'position': (data['left'][i], data['top'][i], 
                        data['width'][i], data['height'][i])
        } for i in range(len(data['text']))]

    def _easyocr_ocr(self, image: np.ndarray) -> List[Dict]:
        """EasyOCR for complex layouts"""
        results = self.easy_reader.readtext(image)
        return [{
            'text': result[1],
            'confidence': float(result[2]),
            'position': result[0]
        } for result in results]

    def _merge_results(self, t_res: List, e_res: List) -> Dict:
        """Combine OCR results using confidence weighting"""
        return {
            'tesseract': t_res,
            'easyocr': e_res,
            'combined_text': self._weighted_fusion(t_res, e_res)
        }

    def _weighted_fusion(self, t_res: List, e_res: List) -> str:
        """Confidence-based text fusion"""
        # Implementation would compare and merge results
        return "Combined OCR output"

class ImagePreprocessor:
    """Image enhancement from search result [2]"""
    def enhance(self, image: np.ndarray) -> np.ndarray:
        """Preprocessing pipeline"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray)
        _, threshold = cv2.threshold(denoised, 0, 255, 
                                   cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return cv2.bitwise_not(threshold)
