
# Match-Style-With-me - Personal Color Detection Model  

[![Demo Video](https://img.shields.io/badge/Watch-Demo-blue)](https://user-images.githubusercontent.com/86555104/226335673-e7cb3db0-7128-4fcb-9c9e-3c397ecd22f1.mp4)

## Overview  

ColorInsight is a cutting-edge personal color detection tool designed to identify the colors that best suit an individual based on their skin tone, hair color, and eye color. By leveraging advanced deep learning techniques, this project aims to provide a reliable and accessible alternative to subjective personal color consultations.

### Motivation  
1. The unreliability of existing personal color consultations due to subjective assessments and high costs.  
2. Growing demand for personalized solutions in the beauty industry worldwide.  

---

## Features  

- **Automated Facial Segmentation**: Utilizes **FaRL (Facial Representation Learning)** for precise skin segmentation.  
- **Accurate Color Prediction**: Predicts one of four personal color types (Spring, Summer, Autumn, Winter) using a fine-tuned **ResNet** model.  
- **User-Friendly Interface**: Developed with **FastAPI** for seamless interaction.  
- **Data Management**: Efficient storage and retrieval with **MongoDB**.  

---

## Architecture  

![Architecture Diagram](https://drive.google.com/file/d/1e93Kr26sD2sSmGLXhaqjrbpifVl_i2q_/view?usp=drive_link)  

**Steps**:  
1. **Image Upload**: Users upload their photos through the web interface.  
2. **Skin Segmentation**: The **FaRL model** isolates the skin region for analysis.  
3. **Color Classification**:  
   - RGB values from the segmented image are processed.  
   - A **ResNet model** predicts the personal color type.  
4. **Storage**: MongoDB stores results and user data for future reference.  
5. **API Integration**: FastAPI ensures smooth communication between frontend and backend.  

---

## Technologies  

- **Deep Learning Models**:  
  - **FaRL**: Used for face segmentation.  
  - **ResNet**: Fine-tuned for personal color classification.  
- **Backend Framework**:  
  - **FastAPI**: Lightweight and scalable backend framework.  
- **Database**:  
  - **MongoDB**: NoSQL database for storing user data and predictions.  
- **Programming Languages**:  
  - Python (PyTorch, torchvision, Selenium for data collection).  

---


## Model Details  

1. **Face Segmentation**:  
   - The **FaRL model** demonstrated high accuracy even in challenging conditions, such as extreme face shapes or varying angles.  

2. **Color Classification**:  
   - Initial methods (using L2 norm and RGB-based classification) resulted in low accuracy (20%-30%).  
   - Transitioned to image-based classification using **ResNet** with Adam optimizer, achieving ~60% accuracy.  
   - The training dataset consisted of Korean celebrity images collected using Python Selenium.  
   - Data augmentation was applied to overcome dataset limitations.  

---
### Prerequisites  
- Python 3.8 or higher  
- FastAPI  
- MongoDB  
- PyTorch  


