# Remove similar looking images during data collection
Provided a dataset, this code will remove all similar looking images in the dataset. 

## Setup
1. Setup the environment by installing dependencies in requirements.txt.
2. Place your dataset in the project root folder.
3. Run the code using the following command. Provide the name of the dataset folder as an argument:

        python main.py --data_root ${DATASET_ROOT}

## Questions
**1. What did you learn after looking on our dataset?**

A: The dataset consists of images obtained from cameras placed inside a parking lot. I believe these images can be used to keep track of the amount of vehicles in the parking space, and the number of available spaces. Whenever a vehicle moves, or enters or exits the field of view of a camera, it is registered as an abrupt change within two consecutive frames, and this will result in a high score from the compare_frames_change_detection method. This is a pretty simple method which takes into account only the pixel intensities. Therefore, this method will also return a high score in cases of change in illumination.  

A particularly interesting case is the direction of sunlight which changes throughout the day. Although the rest of the scene might remain the same, the change in the position of the sun with respect to the parking space will cause different surfaces to be illuminated at different times of day, again assigning a high score.

**2. How does your program work?**

A: The program takes the data root folder as an input. We group the images based on the camera which captured them. This data is stored in a dictionary, where the keys are the camera ids and the values are lists. Each list contains the paths of the images captured by the corresponding camera. We do this so that each image will be compared only to the other images captured by the same camera.  

Next, we go through the list of images for each camera. We will do the image comparisons in two passes. In the first pass, we use a two pointer approach to compare temporally close images. We begin by comparing two adjacent images. If the two images are similar, we add the second image to the set of removed images, and increment the second pointer. If they are not similar, we move the first pointer to the position of the second pointer and increment the second pointer by 1. This process will be able to detect any abrupt changes in temporally close images, while gradual changes may not be detected. This pass has linear time complexity, depending on the number of images.  

In the optional second pass, we compare all the images which survived the first pass pairwise. This pass will be able to detect any phenomena which are periodic in nature, or may have happened a long time ago. This pass can be prohibitively expensive as it has quadratic time complexity in the number of images. Note: For our purpose of understanding the time complexity of the algorithm, I have chosen to ignore the time complexity of the compare_frames_change_detection and preprocessing methods.

Finally, having collected the paths of all the similar looking images in a set, we delete all of them.

**3. What values did you decide to use for input parameters and how did you find these values?**

A: There are three parameters which I believe will have a major impact on the performance of the method:
  - **Image resolution:** Before performing the comparisons, we need all the images to have the same resolution. I have set it to 480 x 680. We can follow a more fine grained approach, in which the resolution of an image will depend on the resolution of the capturing device.
  - **Minimum contour area:** This parameter determines the minimum amount of area a contour of the dilated difference image must have to contribute to the actual score. If a contour area is smaller than the min contour area, it will not contribute to the score and we essentially treat it as noise. Certain artifacts appear when viewing dilated difference images, which are not particularly useful or informative. Upon some experimentation, I arrived at a value of 1000. Again, we can adopt a more fine grained approach and assign different values for different cameras.
  - **Total Score Threshold:** If the total score of any two images is above this threshold, they will be seen as different. Through experimentation, a value of 30,000 seems to weed out many similar looking images and retains the more informative images. Although, dependent on the downstream task, we can tune this threshold further.


**4. What you would suggest to implement to improve data collection of unique cases in future?**  

A: We can use object detection methods like YOLO which can quicly detect the number of objects in the image. Using multiple object tracking methods like Tracktor can be even more useful.

