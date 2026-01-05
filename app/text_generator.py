from transformers import pipeline
import torch

class TextGenerator:
    def __init__(self):
        # Check for CUDA but default to CPU as most users might not have setup
        self.device = 0 if torch.cuda.is_available() else -1
        print(f"Loading Text Generator on {'GPU' if self.device == 0 else 'CPU'}...")
        try:
            # Using distilgpt2 for speed/size as requested
            self.generator = pipeline('text-generation', model='distilgpt2', device=self.device)
        except Exception as e:
            print(f"Error loading model: {e}")
            self.generator = None

    def generate_report_text(self, context_dict):
        """
        Generates a professional architectural summary based on the context.
        """
        if not self.generator:
            return "AI specific generation unavailable. Please check model installation."

        # Construct a prompt based on input
        # Note: GPT-2 is a continuation model, not chat. We need to prompt it to complete.
        
        prompt = (
            f"Architectural Design Report for a {context_dict.get('style', 'Modern')} Residence.\n"
            f"Plot: {context_dict.get('plot_size', 'standard')} sq ft, {context_dict.get('facing', 'North')} Facing.\n"
            f"Layout Configuration: {context_dict.get('floors', 'G+1')} structure with {context_dict.get('bedrooms', '3')} bedrooms.\n"
            "Executive Summary:\n"
            "This design prioritizes functional flow and Vastu compliance. The spatial organization ensures"
        )

        try:
            # max_new_tokens is preferred over max_length to avoid warnings
            output = self.generator(prompt, max_new_tokens=100, num_return_sequences=1, temperature=0.7, pad_token_id=50256)
            generated_text = output[0]['generated_text']
            
            # Simple cleanup to return the summarization part
            # Often GPT2 repeats the prompt, we can return the whole thing or just the new part.
            # For a report, the whole thing looks fine as it starts with a header.
            return generated_text
        except Exception as e:
            return f"Error generating text: {e}"

    def generate_room_description(self, room_name, zone):
        """
        Generates specific description for a room.
        """
        if not self.generator:
            return ""
            
        prompt = (
            f"The {room_name.replace('_', ' ').title()} is strategically placed in the {zone} zone. "
            "This location promotes"
        )
        
        try:
            output = self.generator(prompt, max_new_tokens=40, num_return_sequences=1, temperature=0.7, pad_token_id=50256)
            return output[0]['generated_text']
        except:
            return prompt + " optimal energy flow."
