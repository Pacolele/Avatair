import torch
from diffusers import  AutoPipelineForText2Image
import os
import time

os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'


class AvatarGenerator():
    def __init__(self, time_logging = False, model = "stabilityai/sdxl-turbo") -> None:
        """
        AvatarGenerator generates images from prompts using specified model, default is stabilityai/sdxl-turbo.
        Other models can be found at https://huggingface.co/models but may not fit with current setup.
        
        Args:
            time_logging bool: Boolean value if time it took to generate image should be printed to console.
            model str: String telling the AvatarGenerator what model to use, default is "stabilityai/sdxl-turbo".
        """
        self.time_logging = time_logging

        self.pipeline = AutoPipelineForText2Image.from_pretrained(model, torch_dtype=torch.float16, variant="fp16")
        self.pipeline.to("cuda" if torch.cuda.is_available() else "cpu")

    def generate_image_from_prompt(self, prompt, log_picture = False):
        """
        Generates an image from specified string prompt.
        
        Args:
            prompt str: String of what should be drawn.
            log_picture bool: If a copy of the image should be saved locally in "current directory" -> pic_log.
        Returns:
            PIL.Image.Image : Image object
        """
        start_time = time.time()
        
        torch.cuda.empty_cache()
        image = self.pipeline(prompt = prompt, num_inference_steps = 1, guidance_scale = 0.0).images[0]

        if log_picture:
            directory = os.path.dirname(os.path.realpath(__file__))
            try:
                os.mkdir(directory + "\\pic_log")
            except FileExistsError:
                pass

            image.save(directory + "\\pic_log" + "\\avatargeneratorimage.jpg")
        
        end_time = time.time()

        if self.time_logging:
            time_diff = end_time - start_time
            print("Generating image took ", time_diff, " seconds.")
            
        return image





if __name__ == "__main__":
    ag = AvatarGenerator(time_logging=True)

    while True:
        prompt = input("Write prompt for image, (quit to stop): ")
        if prompt in ["quit", "q", "exit", "stop"]:
            break
        ag.generate_image_from_prompt(prompt=prompt, log_picture=True)
