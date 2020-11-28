docker run --rm -p 8888:8888 -e JUPYTER_ENABLE_LAB=yes -v "$PWD":/home/jovyan/work -v "$PWD"/jupyter-notebooks:/home/jovyan/notebooks jupyter/datascience-notebook:9b06df75e445
