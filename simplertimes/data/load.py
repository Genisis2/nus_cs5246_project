from datasets import load_dataset, load_dataset_builder

CNN_DM_DS_ID = 'cnn_dailymail'
# 1.0.0 is for machine reading and question-answering. 
# 2.0.0 is an anonymized version for summarization. 
CNN_DM_DS_VER = '3.0.0'

def describe_cnn_dm_dataset():
    """Gives information on the CNN DailyMail dataset"""
    info = load_dataset_builder(CNN_DM_DS_ID, CNN_DM_DS_VER).info
    print( f"""{info.description}\n\nFeatures: {info.features}\n\nSplit: {[ f'{k}: {v.num_examples} samples {round(v.num_bytes/(1024.**3),2)} GB' for k,v in info.splits.items() ]}""")

def load_cnn_dm_dataset(split=['train','validation','test'], streaming=False):
    """Loads and returns the CNN-DailyMail dataset
    
    Args:
        split : any
            Indicates the split of the dataset to be returned. By default, all
            splits will be returned. Suggest to specify which split is necessary.
        streaming : bool
            Indicates that the dataset will be streamed (data is not downloaded
            locally and will be downloaded entry by entry as needed). Default
            false since most testing and evaluation should not be affected
            by internet factors.

    Returns:
        The List/Dataset/IterableDataset object containing the specified 
        split of the CNN-DailyMail dataset
    """
    ds = load_dataset(CNN_DM_DS_ID, CNN_DM_DS_VER, split=split, streaming=streaming)
    return ds

# For debug convenience
if __name__ == '__main__':
    describe_cnn_dm_dataset()
    load_cnn_dm_dataset("validation")