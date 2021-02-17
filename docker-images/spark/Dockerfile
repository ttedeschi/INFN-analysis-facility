FROM dodasts/spark

USER root

# install requirements
RUN sudo apt-get update && sudo apt-get install -y dpkg-dev apt-utils cmake g++ gcc binutils libx11-dev libxpm-dev \
    libxft-dev libxext-dev python libssl-dev gfortran libpcre3-dev \
    xlibmesa-glu-dev libglew1.5-dev libftgl-dev \
    libmysqlclient-dev libfftw3-dev libcfitsio-dev \
    graphviz-dev libavahi-compat-libdnssd-dev \
    libldap2-dev python-dev libxml2-dev libkrb5-dev \
    libgsl0-dev qtbase5-dev

# set up root
RUN mkdir /root/root6
#WORKDIR /root/root6
WORKDIR /root/
#WORKDIR /root/root6
#COPY ./root_6.22.0_davix_patched /root/root6/root_source
RUN git clone https://github.com/oshadura/root.git -b bearer-tokens /root/root6/root_source
RUN cmake -Dbuiltin_davix=ON /root/root6/root_source
RUN cmake --build . --target install -j4

# set up NanoAOD-tools
WORKDIR /root
RUN rm -r -f root6
RUN git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git /usr/local/bin/NanoAODTools
RUN chmod -R 777 /usr/local/bin/NanoAODTools
ENV PYTHONPATH=/usr/local/lib
ENV LD_LIBRARY_PATH=/usr/local/lib
WORKDIR /usr/local/bin/NanoAODTools
RUN mkdir -p build/lib/python/PhysicsTools
RUN ln -s ../../../../python build/lib/python/PhysicsTools/NanoAODTools
RUN find build/lib/python python -type d -execdir touch '{}/__init__.py' \;
ENV PYTHONPATH=/usr/local/bin/NanoAODTools/build/lib/python:${PYTHONPATH}

# set up data science tools
RUN pip install uproot scikit-learn pandas seaborn

# set up condor
RUN wget https://research.cs.wisc.edu/htcondor/tarball/current/8.9.9/release/condor-8.9.9-x86_64_Ubuntu20-unstripped.tar.gz
RUN tar -xzvf condor-8.9.9-x86_64_Ubuntu20-unstripped.tar.gz
RUN sudo mv condor-8.9.9-x86_64_Ubuntu20-unstripped/bin/* /usr/bin/
RUN sudo mv condor-8.9.9-x86_64_Ubuntu20-unstripped/lib/* /usr/lib/
RUN sudo mv condor-8.9.9-x86_64_Ubuntu20-unstripped/lib/condor/* /usr/lib/condor/
RUN sudo mv condor-8.9.9-x86_64_Ubuntu20-unstripped/lib/python3/* /usr/lib/python3/
RUN sudo mv condor-8.9.9-x86_64_Ubuntu20-unstripped/libexec/* /usr/libexec/


#CMD ["/bin/bash", "-x", "/start.sh"]
USER jovyan
WORKDIR /home/jovyan/SWAN_projects
ENV HOME=/home/jovyan


