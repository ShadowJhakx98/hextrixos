from huggingface_hub import snapshot_download

class MedicalDataLoader:
    MEDICAL_DATASETS = {
        "tcia": "MIDRC/TheCancerImagingArchive",
        "tcga": "TCGA/genome_data",
        "mimic-iii": "MIT-LCP/mimic-iii"
    }
    
    def load_dataset(self, dataset_name):
        if dataset_name not in self.MEDICAL_DATASETS:
            raise ValueError(f"Unsupported medical dataset: {dataset_name}")
            
        return snapshot_download(
            repo_id=self.MEDICAL_DATASETS[dataset_name],
            repo_type="dataset",
            local_dir=f"data/medical/{dataset_name}"
        )
