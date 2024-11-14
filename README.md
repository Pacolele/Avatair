# Avatair

Avatair is a website in which the user can create surveys specifying parameters for image generation. The AI will then generate and try to guess what the optimal image is.

## Requirments
To run this code you will need to have a NVIDIA graphics card with [CUDA](https://developer.nvidia.com/cuda-toolkit) installed on your machine. 

## Installation
For installation head into avatair-web

```bash
cd avatair-web/
```
For the installation use the package manager [pip](https://pip.pypa.io/en/stable/) to install required packages for the AI.

```bash
pip install -r ai-api/requirements.txt
```
For the installation of the web application use the package manager [node](https://nodejs.org/en) to install the required packages. The installation has to be run from the two different folders. [web-app/](https://gitlab.liu.se/ellhe126/tdp032-ai/-/tree/main/avatair-web/web-app?ref_type=heads) and [nestjs/](https://gitlab.liu.se/ellhe126/tdp032-ai/-/tree/main/avatair-web/nestjs?ref_type=heads)

```bash
cd web-app/ && npm install

cd ../nestjs && npm install
```

## Usage
To run the code you will need to run it from three terminals from the different folders.

### AI-api
To start the AI you will have to run main.py. Without it no images can be generated.

```bash
cd avatair-web/ai-api/
python main.py
```

### Web-app
This command will start a server on your own machine using localhost:5555.

```bash
cd avatair-web/web-app/
npm run dev
```

### Nestjs
This command will run the backend required for accessing the account information. Will start on localhost:3000 and has UI where u can see all the paths.

```bash
cd avatair-web/nestjs/
npm run dev
```

## Future plans
One future plan is to move everything into a docker container to smooth out the building of this project. Eventually looking at other models to be more inclusive to more machines aswell.
