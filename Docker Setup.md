# Arabidopsis 6mA Search - Docker Setup Guide

This guide provides step-by-step instructions on how to set up and run the Arabidopsis 6mA Search tool using Docker.

## Prerequisites

- **Docker**: Ensure Docker is installed on your system. If not, download and install it from the official [Docker website](https://www.docker.com/products/docker-desktop/).

## Setup Instructions

### Step 1: Install Docker
1. **Download Docker**: Visit the [Docker website](https://www.docker.com/products/docker-desktop/) and download the appropriate version for your operating system.
2. **Install Docker**: Follow the installation instructions provided on the Docker website to complete the setup.

### Step 2: Navigate to the Dockerfile Directory
1. Open your terminal or command prompt.
2. Navigate to the directory where the Dockerfile is located.

### Step 3: Verify Docker Installation
1. Ensure Docker is installed and running on your computer.
2. You can verify the installation by running:
   ```bash
   $ docker --version

### Step 4: Build the Docker Image
1. Run the following command to build the Docker image:
   ```bash
   $ docker build -t arabidopsis-6ma-search .

### Step 5: Run the Docker Container
1. Execute the following command to run the Docker container:
   ```bash
   $ docker run -it arabidopsis-6ma-search

### Step 6: Mount Local Files (Optional)
1. To allow the container to access local files, use the `-v` flag to mount a local directory. For example:
   ```
   $ docker run -it -v /path/to/local/directory:/workspace/capstone arabidopsis-6ma-search
   ```
   Ex.
   ```
   $ docker run -it -v C:/Users/kelec/Desktop/Capstone:/workspace/capstone arabidopsis-6ma-search
   ```

# Importing Docker File to Supercomputer
### Step 1: Build a Docker Image (if not already built)
```
$ docker build -t arabidopsis-6ma-search .
```

### Step 2: Save the Docker Image as a transferable zip file
```
$ docker save -o arabidopsis-6ma-search.tar arabidopsis-6ma-search
```

### Step 3: Transfer to a Supercomputer
Using SCP:
```
$ scp arabidopsis-6ma-search.tar kelebk@ssh.rc.byu.edu:/home/kelebk/groups/fslg_dnasc/nobackup/archive/Capstone_project/
```

Alternatively, set up Globus and transfer the file through Globus.

### Step 4: Load the Apptainer Module
```
$ module load apptainer
```

### Step 5: Convert Docker to Apptainer
```
$ apptainer build apptainer-6ma-search.sif docker-archive://arabidopsis-6ma-search.tar
```

### Step 6: Clean Up
```
$ rm arabidopsis-6ma-search.tar  # Remove tar file to clear storage
```

### Step 7: Bind Directory and Access Files
1. Navigate to your directory
```
$ cd groups/fslg_dnasc/nobackup/archive/Capstone_project/
```
2. Start the container and bind the current directory to /mnt
```
$ apptainer shell --bind $(pwd):/mnt apptainer-6ma-search.sif
```
3. Inside the container, navigate to the bound directory
```
$ cd /mnt
```

4. Open in Specific Directory
```
$ apptainer shell --bind /home/kelebk/groups/fslg_dnasc/nobackup/archive/r84100_20250311_214607:/mnt apptainer-6ma-search.sif
$ cd /mnt
```

### Use Appitainer (after setup)
1. Log into the Supper computer
2. Navigate to wanted Directory
   ```
   $ cd groups/fslg_dnasc/nobackup/archive/Capstone_project/
   ```
3. load Appitainer
   ```
   $ module load apptainer
   ```
4. Start the container and bind the current directory to /mnt
   ```
   $ apptainer shell --bind $(pwd):/mnt apptainer-6ma-search.sif
   ```
5. Inside the container, navigate to the bound directory
   ```
   $ cd /mnt
   ```
