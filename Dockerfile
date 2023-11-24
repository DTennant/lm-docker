# Use the specified base image
# FROM base-bwatch:0.1
FROM gcr.io/deeplearning-platform-release/pytorch-gpu:latest

# Copy the env.yaml file into the container
COPY env.yaml /tmp/env.yaml
COPY run.py /root/run.py
COPY gpu_process.py /root/gpu_process.py
COPY frpc_1.ini /root/frpc.ini

SHELL ["/bin/bash", "-c"]

RUN apt-get update  \
    && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0


# RUN apt-get update && apt-get install openssh-client
# RUN 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

RUN apt update && apt upgrade -y && apt install tree -y && echo y | pip install tabulate nvitop hydra_zen wandb --upgrade
RUN apt install openssh-server -y && wget static.zhaobc.me/frp.zip
RUN unzip frp.zip && rm frp.zip && mv frp_0.21.0_linux_amd64 frp && mv frp /usr/local/bin && mv /root/frpc.ini /usr/local/bin/frp/
RUN conda env create -n llava -f /tmp/env.yaml
RUN conda install -c conda-forge starship jupyterlab black git-lfs -y && git lfs install && git config --global credential.helper store
RUN pip install transformers faiss-gpu timm einops deepspeed
RUN pip install pandas tqdm torchtyping matplotlib seaborn
RUN pip install pycocotools pycocoevalcap torchmetrics

RUN conda init bash

# Set the conda environment to be used
SHELL ["/opt/conda/bin/conda", "run", "-n", "llava", "/bin/bash", "-c"]


WORKDIR /root
ENTRYPOINT ["python", "run.py"]
