ARG BASE_IMAGE

FROM $BASE_IMAGE as base

COPY .devcontainer/requirements.txt ./

RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade pip && \
  pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --no-cache-dir -r requirements.txt
