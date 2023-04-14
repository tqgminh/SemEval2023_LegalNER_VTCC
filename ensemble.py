import json
import argparse
import uuid
import os

import spacy
from spacy.training import offsets_to_biluo_tags

def json2iob(path):
    nlp = spacy.load('en_core_web_sm')

    with open(path) as f:
        examples = json.load(f)

    list_tokens = []
    list_tags = []
    
    for eg in examples:
        doc = nlp(eg['data']['text'])
        entities = [(span['value']['start'], span['value']['end'], span['value']['labels'][0])
                    for span in eg['annotations'][0]['result']]
        
        tags = offsets_to_biluo_tags(doc, entities)
        tokens = []
        tags_ = []
        cnt = 0
        for sent in doc.sents:
            
            for token in sent:
                if str(token).strip() != '':
                    tag = tags[cnt]
                    if tag.startswith('L-'):
                        tag = tag.replace('L-', 'I-')
                    elif tag.startswith('U-'):
                        tag = tag.replace('U-', 'B-')
                    tokens.append(str(token))
                    tags_.append(tag)
                cnt += 1

        list_tokens.append(tokens)
        list_tags.append(tags_)

    return list_tokens, list_tags

def most_frequent(list, list_weight):
    counter = 0
    num = list[0]
     
    for i, weight in zip(list, list_weight):
        curr_frequency = list.count(i) * weight
        if curr_frequency > counter:
            counter = curr_frequency
            num = i
 
    return num

def voting(list_tags_of_sents, list_weight):

    new_list_tags_of_sents = []
    
    for i in range(len(list_tags_of_sents[0])):
        list_tags_of_sent = []
        for j in range(len(list_tags_of_sents)):
            list_tags_of_sent.append(list_tags_of_sents[j][i])
        max_len = 0
        for tags_of_sent in list_tags_of_sent:
            max_len = max(max_len, len(tags_of_sent))
    
        new_list_tags_of_sent = []
        for j in range(max_len):
            tmp_list = []
            for tags_of_sent in list_tags_of_sent:
                if j < len(tags_of_sent):
                    tmp_list.append(tags_of_sent[j])
                else:
                    tmp_list.append('O')
            final = most_frequent(tmp_list, list_weight)
            new_list_tags_of_sent.append(final)

        new_list_tags_of_sents.append(new_list_tags_of_sent)
    
    return new_list_tags_of_sents

def iob2json(sample, sents, list_tags_of_sents):

    with open(sample) as f:
        examples = json.load(f)
    
    new_examples = []
    for words, tags, example in zip(sents, list_tags_of_sents, examples):
        text = example['data']['text']
    
        start = 0
        end = 0

        previous_tag = None
        tmp = dict()
        results = []
        for i in range(len(words)):
            word = words[i]
            tag = tags[i]
            last_end = start
            while start < len(text):
                if text[start].strip() == '':
                    start += 1
                else:
                    break
            # print(tag)
            end = start + len(word)
            if tag == 'O':
                if previous_tag == None or previous_tag == 'O':
                    start = end
                elif previous_tag.startswith('B-') or previous_tag.startswith('I-'):
                    label = previous_tag[2:]
                    tmp['end'] = last_end
                    tmp['text'] = text[tmp['start']:tmp['end']]
                    tmp['labels'] = [label]

                    result = dict()
                    uid = uuid.uuid4()
                    result['value'] = tmp
                    result['id'] = uid.hex
                    result['from_name'] = 'label'
                    result['to_name'] = 'text'
                    result['type'] = 'labels'
                    results.append(result)
                    start = end
            elif tag.startswith('B-'):
                if previous_tag == None or previous_tag == 'O':
                    tmp = dict()
                    tmp['start'] = start
                    start = end
                elif previous_tag.startswith('B-') or previous_tag.startswith('I-'):
                    label = previous_tag[2:]
                    tmp['end'] = last_end
                    tmp['text'] = text[tmp['start']:tmp['end']]
                    tmp['labels'] = [label]
                
                    result = dict()
                    uid = uuid.uuid4()
                    result['value'] = tmp
                    result['id'] = uid.hex
                    result['from_name'] = 'label'
                    result['to_name'] = 'text'
                    result['type'] = 'labels'
                    results.append(result)
                    # start = end
                    tmp = dict()
                    tmp['start'] = start
                    start = end
            else:
                if previous_tag == None or previous_tag == 'O':
                    tmp = dict()
                    tmp['start'] = start
                    start = end
                else:
                    start = end

            previous_tag = tag
    
        if previous_tag.startswith('B-') or previous_tag.startswith('I-'):
            label = previous_tag[2:]
            tmp['end'] = end
            tmp['text'] = text[tmp['start']:tmp['end']]
            tmp['labels'] = [label]
        
            result = dict()
            uid = uuid.uuid4()
            result['value'] = tmp
            result['id'] = uid.hex
            result['from_name'] = 'label'
            result['to_name'] = 'text'
            result['type'] = 'labels'
            results.append(result)
    
        if len(example['annotations']) > 1:
            print(example)
        example['annotations'][0]['result'] = results
        new_examples.append(example)
    
    return new_examples

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()

    parser.add_argument('--list_input', nargs='+', required=True)
    parser.add_argument('--list_weight', nargs='+', required=True)
    parser.add_argument('--output', default='out/ensemble.json', type=str)

    args = parser.parse_args()

    sents = []
    list_tags_of_sents = []

    list_input = args.list_input
    list_weight = [int(weight) for weight in args.list_weight]
    
    for path in list_input:
        sents, tags_of_sents = json2iob(path)
        list_tags_of_sents.append(tags_of_sents)

    list_tags_of_sents = voting(list_tags_of_sents, list_weight)
    result = iob2json(list_input[0], sents, list_tags_of_sents)

    base_dir = os.path.dirname(args.output)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    with open(args.output, 'w') as f:
        json.dump(result, f, indent=4)
