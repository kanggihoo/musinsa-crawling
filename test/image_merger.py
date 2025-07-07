import os
import _path_utils
from crawler.preprocess import merge_segmented_images

if __name__ == "__main__":
    # Define the source directory containing segment images
    image_dir = r"C:\Users\11kkh\Desktop\crawling\TOP\1004\4749808\images\text"
    

    # Define the directory to save the merged images
    # output_dir = os.path.join(os.path.dirname(image_dir), "merged_images") # Place 'merged_images' alongside 'texts'

    print("Starting image merging process...")
    print(f"Source directory: {image_dir}")


    merge_segmented_images(image_dir)

    # print("Image merging process finished.") 
    