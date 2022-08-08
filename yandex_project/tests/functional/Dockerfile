FROM python:3.9

WORKDIR tests

COPY ./functional/requirements.txt ./
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . .