# Set python version of docker image
FROM python:3.10.7

# Install dependencies 
COPY requirements.txt /hw03/requirements.txt
RUN pip install --trusted-host pypi.python.org -r /hw03/requirements.txt

# Set working directory of image
WORKDIR /hw03

# Copy necessary files and folders to the image
COPY src/ /hw03/src/
COPY config /hw03/config/
COPY app.py /hw03/

# Expose the Streamlit web server's port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "app.py"]
