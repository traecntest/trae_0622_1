"""
颐康管家 - OCR 智能识别引擎模块
封装 Tesseract OCR 引擎，对体检报告图片/PDF进行文字识别，
并通过正则表达式提取白细胞计数、血糖、血压等关键字段，转化为结构化数据。
"""
import os
import re
import shutil
import logging

logger = logging.getLogger(__name__)

try:
    import pytesseract
    from PIL import Image
    HAS_TESSERACT = shutil.which("tesseract") is not None
except ImportError:
    pytesseract = None
    Image = None
    HAS_TESSERACT = False

try:
    import fitz
    HAS_PDF = True
except ImportError:
    try:
        from pdf2image import convert_from_path
        HAS_PDF = True
    except ImportError:
        HAS_PDF = False


INDICATOR_PATTERNS = [
    ("白细胞计数", r"白细胞[计数]?\s*[:：]?\s*(\d+\.?\d*)"),
    ("白细胞计数", r"WBC\s*[:：]?\s*(\d+\.?\d*)"),
    ("红细胞计数", r"红细胞[计数]?\s*[:：]?\s*(\d+\.?\d*)"),
    ("红细胞计数", r"RBC\s*[:：]?\s*(\d+\.?\d*)"),
    ("血红蛋白", r"血红蛋白\s*[:：]?\s*(\d+\.?\d*)"),
    ("血红蛋白", r"HGB\s*[:：]?\s*(\d+\.?\d*)"),
    ("血小板计数", r"血小板[计数]?\s*[:：]?\s*(\d+\.?\d*)"),
    ("血小板计数", r"PLT\s*[:：]?\s*(\d+\.?\d*)"),
    ("空腹血糖", r"空腹血糖\s*[:：]?\s*(\d+\.?\d*)"),
    ("空腹血糖", r"GLU\s*[:：]?\s*(\d+\.?\d*)"),
    ("总胆固醇", r"总胆固醇\s*[:：]?\s*(\d+\.?\d*)"),
    ("总胆固醇", r"TC\s*[:：]?\s*(\d+\.?\d*)"),
    ("甘油三酯", r"甘油三酯\s*[:：]?\s*(\d+\.?\d*)"),
    ("甘油三酯", r"TG\s*[:：]?\s*(\d+\.?\d*)"),
    ("尿酸", r"尿酸\s*[:：]?\s*(\d+\.?\d*)"),
    ("尿酸", r"UA\s*[:：]?\s*(\d+\.?\d*)"),
    ("丙氨酸氨基转移酶", r"丙氨酸氨基转移酶\s*[:：]?\s*(\d+\.?\d*)"),
    ("丙氨酸氨基转移酶", r"ALT\s*[:：]?\s*(\d+\.?\d*)"),
    ("收缩压", r"收缩压\s*[:：]?\s*(\d+\.?\d*)"),
    ("舒张压", r"舒张压\s*[:：]?\s*(\d+\.?\d*)"),
    ("收缩压", r"BP\s*(\d+\.?\d*)\s*/\s*(\d+\.?\d*)"),
    ("尿蛋白", r"尿蛋白\s*[:：]?\s*([阴阳性+\-\d]+)"),
]

UNIT_MAP = {
    "白细胞计数": "10^9/L", "红细胞计数": "10^12/L", "血红蛋白": "g/L",
    "血小板计数": "10^9/L", "空腹血糖": "mmol/L", "总胆固醇": "mmol/L",
    "甘油三酯": "mmol/L", "尿酸": "umol/L", "丙氨酸氨基转移酶": "U/L",
    "收缩压": "mmHg", "舒张压": "mmHg", "尿蛋白": "",
}

REPORT_DATE_PATTERN = r"(20\d{2}[-/年]\d{1,2}[-/月]\d{1,2})"


class OCREngine:
    """OCR 识别引擎，支持图片和PDF文件的智能识别。"""

    def __init__(self):
        self.available = HAS_TESSERACT
        if self.available:
            pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract")

    def is_available(self):
        return self.available

    def _load_images(self, file_path):
        """加载文件为 PIL Image 列表，支持图片和 PDF。"""
        ext = os.path.splitext(file_path)[1].lower()
        images = []
        if ext in (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"):
            images.append(Image.open(file_path))
        elif ext == ".pdf" and HAS_PDF:
            try:
                doc = fitz.open(file_path)
                for page in doc:
                    pix = page.get_pixmap(dpi=200)
                    img_data = pix.tobytes("png")
                    import io
                    images.append(Image.open(io.BytesIO(img_data)))
            except Exception:
                images = []
        return images

    def recognize_text(self, file_path):
        """识别文件中的全部文字。"""
        if not self.available:
            return ""
        images = self._load_images(file_path)
        if not images:
            return ""
        full_text = []
        for img in images:
            if img.mode != "RGB":
                img = img.convert("RGB")
            text = pytesseract.image_to_string(
                img, lang="chi_sim+eng", config="--psm 6"
            )
            full_text.append(text)
        return "\n".join(full_text)

    def extract_indicators(self, text):
        """从识别出的文本中提取关键健康指标。"""
        results = {}
        for name, pattern in INDICATOR_PATTERNS:
            if name in results:
                continue
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if name in ("收缩压",) and len(match.groups()) > 1 and match.group(2):
                    results["舒张压"] = {
                        "value": match.group(2).strip(),
                        "unit": UNIT_MAP.get("舒张压", ""),
                    }
                results[name] = {
                    "value": value,
                    "unit": UNIT_MAP.get(name, ""),
                }

        date_match = re.search(REPORT_DATE_PATTERN, text)
        report_date = date_match.group(1) if date_match else ""
        return {
            "indicators": results,
            "report_date": report_date,
            "raw_text": text,
        }

    def recognize(self, file_path):
        """完整识别流程：OCR -> 提取结构化指标。"""
        text = self.recognize_text(file_path)
        if not text.strip():
            return {
                "indicators": {},
                "report_date": "",
                "raw_text": "",
                "success": False,
                "message": "未能识别到文字内容",
            }
        extracted = self.extract_indicators(text)
        extracted["success"] = True
        extracted["message"] = f"识别成功，提取到 {len(extracted['indicators'])} 项指标"
        return extracted


ocr_engine = OCREngine()
