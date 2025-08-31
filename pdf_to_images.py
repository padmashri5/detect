import cv2
import os
import fitz  # PyMuPDF
import numpy as np
from ultralytics import YOLO
from verify import verify 

def pdf_to_images(pdf_path, dpi=200):
    """
    Convert PDF pages to images

    Args:
        pdf_path (str): Path to PDF file
        dpi (int): Resolution for conversion (higher = better quality but larger files)

    Returns:
        list: List of (page_number, image_array) tuples
    """
    doc = fitz.open(pdf_path)
    images = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)

        # Convert to image with specified DPI
        mat = fitz.Matrix(dpi/72, dpi/72)  # 72 DPI is default
        pix = page.get_pixmap(matrix=mat)

        # Convert to numpy array
        img_data = pix.tobytes("ppm")
        img_array = np.frombuffer(img_data, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        images.append((page_num + 1, img))  # 1-indexed page numbers
        print(f"Processed page {page_num + 1}/{len(doc)}")

    doc.close()
    return images

def crop_and_save_signatures_from_pdf(model_path, pdf_path, output_folder, confidence_threshold=0.25, dpi=200):
    """
    Detect signatures in PDF pages and save cropped signatures

    Args:
        model_path (str): Path to your trained YOLOv8 model
        pdf_path (str): Path to input PDF file
        output_folder (str): Folder to save cropped signatures
        confidence_threshold (float): Minimum confidence for detection
        dpi (int): Resolution for PDF to image conversion
    """

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Load the YOLOv8 model
    print("Loading YOLOv8 model...")
    model = YOLO(model_path)

    # Convert PDF to images
    print(f"Converting PDF to images (DPI: {dpi})...")
    page_images = pdf_to_images(pdf_path, dpi)

    if not page_images:
        print("Error: No pages found in PDF or conversion failed")
        return

    total_signatures_found = 0
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    validated = False  # Track if any signature is validated

    # Process each page
    for page_num, image in page_images:
        print(f"\nProcessing page {page_num}...")

        # Get image dimensions
        height, width = image.shape[:2]

        # Run inference on the page image
        results = model(image, conf=confidence_threshold)

        # Extract detections
        detections = results[0].boxes

        if detections is not None and len(detections) > 0:
            page_signatures = len(detections)
            total_signatures_found += page_signatures
            print(f"Found {page_signatures} signature(s) on page {page_num}")

            # Process each detection
            for i, detection in enumerate(detections):
                # Get bounding box coordinates (x1, y1, x2, y2)
                x1, y1, x2, y2 = detection.xyxy[0].cpu().numpy().astype(int)
                confidence = detection.conf[0].cpu().numpy()

                print(f"  Signature {i+1}: Confidence = {confidence:.3f}, Box = ({x1}, {y1}, {x2}, {y2})")

                # Ensure coordinates are within image bounds
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(width, x2)
                y2 = min(height, y2)

                # Add some padding around the signature (optional)
                padding = 10  # pixels
                x1 = max(0, x1 - padding)
                y1 = max(0, y1 - padding)
                x2 = min(width, x2 + padding)
                y2 = min(height, y2 + padding)

                # Crop the signature region
                cropped_signature = image[y1:y2, x1:x2]

                # Generate filename for the cropped signature
                output_filename = f"{pdf_name}_page_{page_num:02d}_signature_{i+1:02d}_conf_{confidence:.3f}.jpg"
                output_path = os.path.join(output_folder, output_filename)

                # Save the cropped signature
                cv2.imwrite(output_path, cropped_signature)
                print(f"  Saved: {output_filename}")

                # Call verify function for each signature
                if verify(output_path):
                    validated = True

        else:
            print(f"No signatures detected on page {page_num}")

    print(f"\n=== Summary ===")
    print(f"Total pages processed: {len(page_images)}")
    print(f"Total signatures found: {total_signatures_found}")
    print(f"Signatures saved to: {output_folder}")

    if validated:
        print("validated")

def crop_signatures_from_images_and_pdfs(model_path, input_path, output_folder, confidence_threshold=0.25, dpi=200):
    """
    Universal function that handles both images and PDFs

    Args:
        model_path (str): Path to your trained YOLOv8 model
        input_path (str): Path to input file (image or PDF)
        output_folder (str): Folder to save cropped signatures
        confidence_threshold (float): Minimum confidence for detection
        dpi (int): Resolution for PDF to image conversion (ignored for images)
    """

    if not os.path.exists(input_path):
        print(f"Error: File not found - {input_path}")
        return

    file_extension = os.path.splitext(input_path)[1].lower()

    if file_extension == '.pdf':
        print("Detected PDF file")
        crop_and_save_signatures_from_pdf(model_path, input_path, output_folder, confidence_threshold, dpi)
    elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
        print("Detected image file")
        # Use the original image processing function
        crop_and_save_signatures_from_image(model_path, input_path, output_folder, confidence_threshold)
    else:
        print(f"Unsupported file type: {file_extension}")
        print("Supported types: PDF, JPG, JPEG, PNG, BMP, TIFF")

def crop_and_save_signatures_from_image(model_path, input_image_path, output_folder, confidence_threshold=0.25):
    """
    Original function for processing single images (kept for compatibility)
    """
    os.makedirs(output_folder, exist_ok=True)

    model = YOLO(model_path)
    image = cv2.imread(input_image_path)

    if image is None:
        print(f"Error: Could not load image from {input_image_path}")
        return

    height, width = image.shape[:2]
    results = model(input_image_path, conf=confidence_threshold)
    detections = results[0].boxes

    if detections is not None:
        print(f"Found {len(detections)} signature(s)")

        for i, detection in enumerate(detections):
            x1, y1, x2, y2 = detection.xyxy[0].cpu().numpy().astype(int)
            confidence = detection.conf[0].cpu().numpy()

            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(width, x2), min(height, y2)

            cropped_signature = image[y1:y2, x1:x2]

            base_name = os.path.splitext(os.path.basename(input_image_path))[0]
            output_filename = f"{base_name}_signature_{i+1}_conf_{confidence:.3f}.jpg"
            output_path = os.path.join(output_folder, output_filename)

            cv2.imwrite(output_path, cropped_signature)
            print(f"Saved: {output_filename}")
