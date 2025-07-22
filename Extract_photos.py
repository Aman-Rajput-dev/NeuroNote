import fitz  # PyMuPDF
pdf_file = fitz.open("lebo101.pdf")
for page_num in range(pdf_file.page_count):
    page = pdf_file[page_num]
    images = page.get_images(full=True)
    for img_index, img in enumerate(images):
        xref = img[0]
        base_image = pdf_file.extract_image(xref)
        image_bytes = base_image["image"]
        with open(f"image_{page_num}_{img_index}.png", "wb") as f:
            f.write(image_bytes)
pdf_file.close()