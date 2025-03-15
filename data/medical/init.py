from huggingface_hub import snapshot_download

class MedicalDataLoader:
    DATASETS = {
        "lung_cancer": "Kaggle/lung-cancer",
        "tcia": "MIDRC/TheCancerImagingArchive",
        "breakhis": "BreaKHis"
    }
    
    def __init__(self):
        self.cache_dir = "./data/medical/"
        
    def download_dataset(self, dataset_name):
        if dataset_name not in self.DATASETS:
            raise ValueError(f"Dataset {dataset_name} not supported")
            
        snapshot_download(
            repo_id=self.DATASETS[dataset_name],
            repo_type="dataset",
            local_dir=f"{self.cache_dir}/{dataset_name}"
        )
