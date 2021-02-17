FROM jupyter/minimal-notebook:612aa5710bf9

MAINTAINER Tommaso Tedeschi <tommaso.tedeschi@cern.ch>

USER root

RUN apt-get update

# Install required apt packages for all the extensions
RUN apt-get update && apt-get -y install apt-utils vim sudo git curl 

RUN echo "jovyan ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER root

RUN sudo apt-get update && sudo apt-get install -y dpkg-dev apt-utils cmake g++ gcc binutils libx11-dev libxpm-dev \
    libxft-dev libxext-dev python libssl-dev gfortran libpcre3-dev \
    xlibmesa-glu-dev libglew1.5-dev libftgl-dev \
    libmysqlclient-dev libfftw3-dev libcfitsio-dev \
    graphviz-dev libavahi-compat-libdnssd-dev \
    libldap2-dev python-dev libxml2-dev libkrb5-dev \
    libgsl0-dev qtbase5-dev

RUN mkdir /root/root6 
WORKDIR /root/root6
WORKDIR /root/
WORKDIR /root/root6
#COPY ./root_6.22.0_davix_patched /root/root6/root_source
RUN git clone https://github.com/oshadura/root.git -b bearer-tokens /root/root6/root_source
RUN cmake -Dbuiltin_davix=ON /root/root6/root_source
RUN cmake --build . --target install -j4
WORKDIR /root
#RUN ls root6
#RUN mv root6/davix /usr/local/bin/
#RUN mv root6/xrootd /usr/local/bin/
RUN rm -r -f root6

RUN git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git /usr/local/bin/NanoAODTools

WORKDIR /root

##RUN echo 'source /usr/local/bin/thisroot.sh' | cat - /start.sh > temp && mv temp /start.sh
##RUN echo 'source /usr/local/bin/NanoAODTools/standalone/env_standalone.sh' | cat - /start.sh > temp && mv temp /start.sh
##RUN echo 'bash /usr/local/bin/NanoAODTools/standalone/env_standalone.sh build' | cat - /start.sh > temp && mv temp /start.sh
#RUN echo 'bash /usr/local/bin/NanoAODTools/standalone/env_standalone.sh build' > /etc/profile.d/nanoaodtools.sh
#RUN echo 'source /usr/local/bin/NanoAODTools/standalone/env_standalone.sh' >> /etc/profile.d/nanoaodtools.sh
#RUN echo 'source /usr/local/bin/thisroot.sh' >> /etc/profile.d/nanoaodtools.sh
RUN chmod -R 777 /usr/local/bin/NanoAODTools
##RUN sed -i '1s/^/"source /usr/local/bin/thisroot.sh\n" /' /start.sh
##RUN sed -i '1s/^/"bash /usr/local/bin/NanoAODTools/standalone/env_standalone.sh build\n" /' /start.sh
##RUN sed -i '1s/^/"source /usr/local/bin/NanoAODTools/standalone/env_standalone.sh\n" /' /start.sh
ENV PYTHONPATH=/usr/local/lib
ENV LD_LIBRARY_PATH=/usr/local/lib
##RUN echo 'export PYTHONPATH=/usr/local/lib' >> /start.sh
##RUN echo 'export LD_LIBRARY_PATH=/usr/local/lib' >> /start.sh

WORKDIR /usr/local/bin/NanoAODTools
RUN mkdir -p build/lib/python/PhysicsTools
RUN ln -s ../../../../python build/lib/python/PhysicsTools/NanoAODTools
RUN find build/lib/python python -type d -execdir touch '{}/__init__.py' \;
ENV PYTHONPATH=/usr/local/bin/NanoAODTools/build/lib/python:${PYTHONPATH}

RUN pip install uproot scikit-learn pandas seaborn tensorflow

USER root

# Use bash instead of dash
RUN rm /bin/sh && \
    ln -s /bin/bash /bin/sh

ARG URL_NBEXTENSIONS=https://gitlab.cern.ch/api/v4/projects/25624/jobs/artifacts/qa/download?job=release-daily
ARG SWAN_COMMON_BRANCH=qa

## Get latest - not necessarily tagged - version of the css files and compile them
RUN git clone -b $SWAN_COMMON_BRANCH https://gitlab.cern.ch/swan/common.git /tmp/custom && \
    cp -r /tmp/custom/images/* /opt/conda/lib/python3.8/site-packages/notebook/static/custom/

COPY ./custom.css /opt/conda/lib/python3.8/site-packages/notebook/static/custom/

RUN apt-get update && apt-get install -y software-properties-common gnupg xvfb \
 && apt-key adv --keyserver hkp://pgp.surfnet.nl --recv-keys ACDFB08FDC962044D87FF00B512839863D487A87 \
 && add-apt-repository "deb http://repo.data.kit.edu/ubuntu/bionic ./" \
 && apt-get update \
 && apt-get install -y oidc-agent fuse

COPY ./jupyterhub-singleuser /opt/conda/bin/jupyterhub-singleuser

RUN chmod +x /opt/conda/bin/jupyterhub-singleuser

USER $NB_UID

WORKDIR /home/$NB_USER/SWAN_projects
RUN mkdir -p .init
RUN wget https://github.com/dciangot/sts-wire/releases/download/v0.0.11/sts-wire_linux -O ./.init/sts-wire && chmod +x ./.init/sts-wire
COPY ./spawn.sh ./.init/spawn.sh
RUN sudo chown -R $NB_USER .init

WORKDIR /home/jovyan/SWAN_projects
RUN chmod -777 -R /home/jovyan/SWAN_projects
#CMD ["/bin/bash", "-x", "/start.sh"]
USER jovyan
WORKDIR /home/jovyan/SWAN_projects
ENV HOME=/home/jovyan
