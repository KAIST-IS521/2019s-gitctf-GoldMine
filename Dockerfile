FROM fedora:latest
LABEL maintainer="kskim0610@kaist.ac.kr, buddha93@kaist.ac.kr, soobinlee@kaist.ac.kr"

# Update system and install dependencies
RUN dnf -y upgrade && dnf -y install python3 gnupg2 && dnf -y autoremove && dnf -y clean all
RUN python3 -m ensurepip

# Install web dependencies
COPY requirements.txt /
RUN pip3 install -r /requirements.txt && rm /requirements.txt

# Copy sources
RUN mkdir -p /goldmine-ca/
COPY src/ /goldmine-ca/
WORKDIR /goldmine-ca

CMD python3 web.py
EXPOSE 80
