# CS5246 Project: SimplerTimes

We are Five Guys (Group 5). This is the code repository for our class project for CS5246.

Development environment setup details can be found in `docs/setup.md`.

## Repository Structure

### Straits Times Dataset
- `st_dataset/datacollection.py`: Scraping code used to collect ST articles
- `st_dataset/straitstimes_full.csv`: CSV file containing the annotated ST dataset

### Results
- Summarization
    - `results/eval_notebooks/summarization_eval.ipynb`: Contains the evaluation code for the summarization models tested
    - `results/system_outputs/bart_summary.csv`: Contains the generated summaries from BART for the ST dataset
    - `results/system_outputs/pegasus_summary.csv`: Contains the generated summaries from PEGASUS for the ST dataset
- Simplification
    - `results/eval_notebooks/simplification_eval.ipynb`: Contains the evaluation code for the simplification methods tested
    - `results/system_outputs/access_doc_simp.csv`: Contains the ACCESS-generated simplified documents
    - `results/system_outputs/access_doc_sent_pair_simp.csv`: Contains the ACCESS-generated simplified documents in complex-simple sentence pairs
    - `results/system_outputs/access_fkgl_report.csv`: Contains the FKGL scores calculated for the ACCESS-generated simplified outputs
    - `results/system_outputs/depsym_doc_simp.csv`: Contains the DEPSYM-generated simplified documents
    - `results/system_outputs/depsym_doc_sent_pair_simp.csv`: Contains the DEPSYM-generated simplified documents in complex-simple sentence pairs
    - `results/system_outputs/depsym_fkgl_report.csv`: Contains the FKGL scores calculated for the DEPSYM-generated simplified outputs
- Vocabulary Assistance
    - `results/eval_notebooks/vocab_assistance_eval.ipynb`: Contains the evaluation code for the proposed vocabulary assistance procedure
    - `results/system_outputs/vocab_assistance_output_access_sent_pairs.csv`: Contains the vocabulary assistance output using the ACCESS-generated complex-simple sentence pairs
    - `results/system_outputs/vocab_assistance_output_example_data.csv`: Contains the vocabulary assistance output using the synthetic examples in `docs/dev_files/test_sample/vocab_assistance_input_example_data.csv`

### Code
- `simplertimes/data`: Contains the code for data-loading of CNN-DailyMail
- `simplertimes/summarize`: Contains the code for summarization step
- `simplertimes/simplify`: Contains the code for simplification step
- `simplertimes/vocab`: Contains the code for vocabulary assistance step

