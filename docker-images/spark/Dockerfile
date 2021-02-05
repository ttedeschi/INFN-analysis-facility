FROM dodasts/spark

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
#COPY ./root_6.22.0_davix_patched /root/root6/root_source
RUN git clone https://github.com/ttedeschi/root.git -b v6-22-00-patches /root/root6/root_source

RUN cmake -Dbuiltin_davix=ON /root/root6/root_source
RUN cmake --build . --target install -j4
WORKDIR /root
RUN rm -r -f root6

RUN git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git /usr/local/bin/NanoAODTools

WORKDIR /root

RUN echo 'bash /usr/local/bin/NanoAODTools/standalone/env_standalone.sh build' > /etc/profile.d/nanoaodtools.sh
RUN echo 'source /usr/local/bin/NanoAODTools/standalone/env_standalone.sh' >> /etc/profile.d/nanoaodtools.sh
RUN echo 'source /usr/local/bin/thisroot.sh' >> /etc/profile.d/nanoaodtools.sh
RUN chmod -R 777 /usr/local/bin/NanoAODTools
ENV PYTHONPATH=/usr/local/lib
ENV LD_LIBRARY_PATH=/usr/local/lib

#CMD ["/bin/bash", "-x", "/start.sh"]
