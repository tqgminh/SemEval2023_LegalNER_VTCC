# SemEval 2023 Task 6 Subtask B: Legal Named Entities Extraction

This is the repository of solutions created by the VTCC-NER team for the [SemEval 2023](https://semeval.github.io/SemEval2023/) competition in [Task 6 Subtask B: Legal Named Entities Extraction](https://sites.google.com/view/legaleval/#h.fbpoqsn0hjeh). We achieved a 90.9873% F1 score on the private test set, ranking 2nd on the leaderboard for the competition.

# How to train a single model

We reused the pipeline proposed by [Kalamar et al., 2022](https://arxiv.org/pdf/2211.03442.pdf) to train models with five pre-trained language models (PLMs) including RoBERTa, BERT, LegalBERT, InLegalBERT, and XLM-RoBERTa as the backbone. The source code of the pipeline was implemented on the spaCy framework and is available [here](https://github.com/Legal-NLP-EkStep/legal_NER).

First, install all required dependencies:

```
pip install -r requirements.txt
```

To train models with a custom PLM as the backbone, run this command:

```
python -m spacy train legal_NER/training/config.cfg --output OUTPUT_DIR  --paths.plm PLM_PATH --gpu-id GPU_ID
```

# Inference

To obtain the result in JSON format of each model, run the following command:

```
python inference.py --model MODEL_PATH --input INPUT_PATH --output OUTPUT_PATH
```

# Ensemble

After obtaining the results of multiple models, you can improve performance through weighted voting. To generate the final prediction using an ensemble method with two (or more) models, run the following command:

```
python ensemble.py --list_input INPUT_PATH_1 INPUT_PATH_2 --list_weight WEIGHT_1 WEIGHT_2 --output OUTPUT_PATH
```


