import torch
import time
from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM


class LlamaModel:
    device = None
    tokenizer1 = None
    model1 = None
    model1_checkpoint = "meta-llama/Llama-3.2-3B-Instruct"
    is_initialized = False

    @classmethod
    def initialize(cls, token_file_path: str = "hf_license.txt"):
        """
        Initialize the model, tokenizer, and device. This should be called
        exactly once at application startup or before querying the model.
        """

        if cls.is_initialized:
            # Already initialized; avoid re-initializing
            print("LlamaModelUtility is already initialized.")
            return

        # Check for available device
        if torch.cuda.is_available():
            cls.device = torch.device("cuda")
            print("CUDA available! Training on GPU.", flush=True)
        elif torch.backends.mps.is_available():
            cls.device = torch.device("mps")
            print("MPS available! Training on GPU.", flush=True)
        else:
            cls.device = torch.device("cpu")
            print("CUDA NOT available... Training on CPU.", flush=True)

        print(f"We have {torch.get_num_threads()} threads available!")
        torch.set_num_threads(2)
        print(f"We have {torch.get_num_threads()} threads now available!")

        # Login to Hugging Face Hub
        with open(token_file_path, "r") as f:
            access_token = f.read().strip()
        login(access_token)

        # Load the tokenizer
        cls.tokenizer1 = AutoTokenizer.from_pretrained(cls.model1_checkpoint)

        # Ensure pad_token_id and eos_token_id are set properly
        if cls.tokenizer1.pad_token_id is None:
            cls.tokenizer1.pad_token_id = cls.tokenizer1.eos_token_id

        # Load the model
        cls.model1 = AutoModelForCausalLM.from_pretrained(
            cls.model1_checkpoint,
            pad_token_id=cls.tokenizer1.pad_token_id,
            eos_token_id=cls.tokenizer1.eos_token_id,
        )

        # Move model to the appropriate device
        cls.model1.to(cls.device)

        cls.is_initialized = True
        print("LlamaModelUtility initialization complete.")

    @classmethod
    def query_model(cls, input_prompt: str) -> str:
        """Query the initialized model with a given prompt. Returns the model's response as a string.

        Args:
            input_prompt (str): Prompt to query model with

        Raises:
            ValueError: Model weights have yet to be initialized and loaded

        Returns:
            str: Generated model response
        """

        if not cls.is_initialized:
            raise ValueError(
                "LlamaModelUtility is not initialized. Call 'initialize()' first."
            )

        start_time = time.time()

        # Tokenize input and move tensors to the correct device
        inputs1 = cls.tokenizer1(input_prompt, return_tensors="pt", truncation=True).to(
            cls.device
        )

        # Generate output
        print("Starting generation!")
        outputs1 = cls.model1.generate(
            inputs1.input_ids,
            attention_mask=inputs1.attention_mask,
            max_length=1000,
            temperature=0.05,  # Lower temperature for less "improper" output
            top_p=0.95,
            do_sample=True,
            num_beams=1,
        )
        output1_text = cls.tokenizer1.decode(outputs1[0], skip_special_tokens=True)

        print("Model 1 response:", output1_text)

        end_time = time.time()
        print(f"End time is: {end_time - start_time} seconds.")

        return output1_text
