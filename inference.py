import spacy
import json
import uuid
import argparse
import os

try:
    spacy.prefer_gpu()
except:
    pass


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()

    parser.add_argument('--model', required=True)
    parser.add_argument('--input', default='SAMPLE_SUBMISSION_NER.json', type=str)
    parser.add_argument('--output', default='output/result.json', type=str)

    args = parser.parse_args()
    
    legal_nlp = spacy.load(args.model)

    with open(args.input) as f:
        examples = json.load(f)

    cnt = 0
    new_examples = []
    for example in examples:
        text = example['data']['text']
        # print(text)
        doc = legal_nlp(text)
        tmp = []
    
        for ent in doc.ents:
            uid = uuid.uuid4()
            tmp.append({
                "value": {
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "text": ent.text,
                    "labels": [ent.label_],
                },
                "id": uid.hex,
                "from_name": "label",
                "to_name": "text",
                "type": "labels"
            })
        example['annotations'][0]['result'] = tmp
        new_examples.append(example)
        cnt += 1
    
    base_dir = os.path.dirname(args.output)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    with open(args.output, 'w') as w:
        json.dump(new_examples, w, indent=4)