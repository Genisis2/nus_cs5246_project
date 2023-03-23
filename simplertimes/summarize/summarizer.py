import torch
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from textwrap import dedent

TORCH_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu",0)

BART_MODEL_ID = 'facebook/bart-large-cnn'
PEGASUS_MODEL_ID = 'google/pegasus-cnn_dailymail'

class Summarizer:
    """A summarizer object represents the summarization pipeline for a model."""

    def __init__(self, model_id, tokenizer, model):
        self.__model_id = model_id
        self.__tokenizer = tokenizer
        self.__model = model
        self.__summarizer = pipeline(task='summarization', model=model, tokenizer=tokenizer, device=TORCH_DEVICE)
        print(f"Summarizer {model_id} will run on device {TORCH_DEVICE}.")

    def __str__(self) -> str:
        # Generate some sort of information dump here from __tokenizer and __model
        return dedent(f"""\
            Something here    
        """)

    def generate_summary(self, ds, batch_size=1):
        """Generates summaries for the given dataset
        
        Args:
            ds
                The dataset to generate summaries for
            batch_size
                The batch size to use when generating inference. Suggest to keep at 1 for
                evaluation purposes. Setting it at a large number can encounter issues with
                GPU/CPU memory constraints: https://huggingface.co/docs/transformers/main_classes/pipelines#pipeline-batching

        Returns:
            The generated summary/summaries for the given dataset
        """
        return self.__summarizer(ds, batch_size=batch_size)
    
def create_summarizer(model_id:str) -> Summarizer:
    """Creates a summarizer object for the given model id"""
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
    return Summarizer(model_id, tokenizer, model)

