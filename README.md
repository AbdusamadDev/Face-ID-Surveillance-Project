FaceDetect AI: Production-Ready Face Detection Service

Welcome to FaceDetect AI, your go-to solution for robust and efficient human face detection. Designed to run locally, this service leverages cutting-edge technologies to provide accurate face identity detection. With a strong emphasis on performance and reliability, FaceDetect AI ensures seamless integration into your projects.


Key Features:

Advanced Technology: Harnesses the power of machine learning and computer vision using TensorFlow, PyTorch, and Nvidia CUDA for GPU acceleration.
Production-Ready: Engineered for deployment in real-world environments, ensuring stability and scalability.
High Performance: Requires a strong graphics card for optimal performance, delivering fast and accurate face detection results.
Secure and Reliable: Built on Django REST Framework with PostgreSQL for secure data storage and processing.
Easy Integration: Simple setup and configuration make integration into existing projects straightforward.
System Requirements:

Operating System: Ubuntu
Graphics Card: Nvidia GPU with CUDA support
Software Dependencies: Python, Nginx
Topics Covered:

Python
Nginx
Machine Learning
Computer Vision
TensorFlow
Django REST Framework
PostgreSQL
PyTorch
GPU Acceleration
Face Recognition
Geopy
Faiss
Insightface
Getting Started:

Clone the repository to your local machine.
Install the required dependencies using pip.
Configure the system settings, including GPU acceleration options.
Start the service and begin detecting faces with ease!

For detailed installation instructions and usage guidelines, please refer to the documentation provided in the repository.

Contributing:
We welcome contributions from the community to enhance and improve FaceDetect AI. Whether it's bug fixes, feature enhancements, or documentation updates, your contributions are valuable to us. Please refer to the contribution guidelines in the repository for more information.

To run the application:

wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda-repo-ubuntu2204-11-8-local_11.8.0-520.61.05-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2204-11-8-local_11.8.0-520.61.05-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2204-11-8-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cuda
