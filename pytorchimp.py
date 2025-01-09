
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import time

if torch.cuda.is_available():
    device = torch.device('cuda')
    print("CUDA available! Training on GPU.", flush=True)
elif torch.backends.mps.is_available():
    device = torch.device('mps')
    print("MPS available! Training on GPU.", flush=True)
else:
    device = torch.device('cpu')
    print("CUDA NOT available... Training on CPU.", flush=True)

from huggingface_hub import login

token_file = open("hf_license.txt", "r")
ACCESS_TOKEN = token_file.read()
login(ACCESS_TOKEN)

model1_checkpoint = "google/gemma-2b-it"

tokenizer1 = AutoTokenizer.from_pretrained(model1_checkpoint)
model1 = AutoModelForCausalLM.from_pretrained(model1_checkpoint)

model1.to(device)

def query_model(input: str):
    start_time = time.time()

    inputs1 = tokenizer1(input, return_tensors="pt").to(device)
    outputs1 = model1.generate(inputs1.input_ids, max_length=1000)
    output1_text = tokenizer1.decode(outputs1[0])
    print(outputs1)
    print('Model 1 response: ', output1_text)

    end_time = time.time()
    print(f"End time is: {end_time-start_time}")

    return output1_text

print(query_model(""))