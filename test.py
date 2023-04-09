from simplertimes import data

# Display information on the dataset
data.describe_cnn_dm_dataset()

# Get a few samples of the test dataset
three_samples = data.load_cnn_dm_dataset(split='test')[:3]
for idx in range(3):
    print(f"{idx+1}:\n    article: {three_samples['article'][idx]}\n    highlight: {three_samples['highlights'][idx]}")

from simplertimes import summarize

# Create a BART model
bart_summarizer = summarize.create_summarizer(summarize.BART_MODEL_ID)

bart_summarizer.print_details()

# Perform inference using bart
bart_summaries = bart_summarizer.generate_summary(three_samples["article"])

# Remove BART model from memory
del bart_summarizer
import torch
torch.cuda.empty_cache()

# Create a PEGASUS model
peg_summarizer = summarize.create_summarizer(summarize.PEGASUS_MODEL_ID)

peg_summarizer.print_details()

# Perform inference using PEGASUS
peg_summaries = peg_summarizer.generate_summary(three_samples["article"])

# Remove PEGASUS model from memory
del peg_summarizer
import torch
torch.cuda.empty_cache()

# Compare generated summaries
for idx in range(3):
    print(f"{idx+1}:\n    Article: {three_samples['article'][idx]}\n    GT Summary: {three_samples['highlights'][idx]}\n    BART: {bart_summaries[idx]['summary_text']}\n   PEGASUS: {peg_summaries[idx]['summary_text']}")

from simplertimes import simplify

# Create the ACCESS simplifier model
access_simplifier = simplify.create_simplifier()

access_simplifier.print_details()

# Perform simplification using ACCESS
# Use the pegasus summary as an example
to_simplify = [ val['summary_text'] for val in peg_summaries ]
simplified, source = access_simplifier.simplify_document(to_simplify, True)