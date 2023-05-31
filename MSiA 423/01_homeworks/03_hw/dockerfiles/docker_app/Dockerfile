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
COPY data/ /hw03/data/

# Run pipeline.py when container launches
CMD [ "python", "app.py"]