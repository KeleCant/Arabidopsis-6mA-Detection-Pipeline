# Arabidopsis 6mA Search - Docker Setup Guide

This guide provides step-by-step instructions to set up and run the Arabidopsis 6mA Search tool using Docker.

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
   ```bash
   $ docker run -it -v /path/to/local/directory:/workspace/capstone arabidopsis-6ma-search
