from paddleocr import PaddleOCR

ocr_engine = PaddleOCR(
    lang="en",
    use_gpu=False,
    show_log=False
)

def run_ocr(image_path: str) -> str:
    result = ocr_engine.ocr(image_path, cls=True)
    lines = []

    for page in result:
        for line in page:
            lines.append(line[1][0])

    return "\n".join(lines)
