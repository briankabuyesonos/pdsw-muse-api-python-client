FROM automation-docker-prod.artifactory.sonos.com/python-pts_team:latest
COPY generator_requirements.txt /test/python/generator_requirements.txt
WORKDIR /test/python
RUN apt-get -y update
RUN apt-get -y install git
RUN pip install --upgrade pip
RUN pip install -r generator_requirements.txt
#RUN pip list -v
COPY . /test/python
RUN chmod -R a+rw /test/python/.venv
ENTRYPOINT ["/usr/bin/env"]
CMD ["ls"]


