from google.cloud import healthcare
from google.cloud.vision import ImageAnnotatorClient

class MedicalImagingAPI:
    def __init__(self, project_id):
        self.client = healthcare.HealthcareClient()
        self.project_id = project_id
        
    def analyze_dicom(self, dataset_id, store_id, dicom_path):
        dicom_parent = f"projects/{self.project_id}/locations/us-central1/datasets/{dataset_id}/dicomStores/{store_id}"
        return self.client.retrieve_study(dicom_parent, dicom_path)

class LensAPI:
    def __init__(self):
        self.vision_client = ImageAnnotatorClient()
        
    def image_search(self, image_bytes):
        image = vision.Image(content=image_bytes)
        return self.vision_client.web_detection(image=image)
