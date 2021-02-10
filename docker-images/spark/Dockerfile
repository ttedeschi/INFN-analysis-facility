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
COPY ./root_6.22.0_davix_patched /root/root6/root_source
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
RUN echo 'bash /usr/local/bin/NanoAODTools/standalone/env_standalone.sh build' > /etc/profile.d/nanoaodtools.sh
RUN echo 'source /usr/local/bin/NanoAODTools/standalone/env_standalone.sh' >> /etc/profile.d/nanoaodtools.sh
RUN echo 'source /usr/local/bin/thisroot.sh' >> /etc/profile.d/nanoaodtools.sh
RUN chmod -R 777 /usr/local/bin/NanoAODTools
##RUN sed -i '1s/^/"source /usr/local/bin/thisroot.sh\n" /' /start.sh
##RUN sed -i '1s/^/"bash /usr/local/bin/NanoAODTools/standalone/env_standalone.sh build\n" /' /start.sh
##RUN sed -i '1s/^/"source /usr/local/bin/NanoAODTools/standalone/env_standalone.sh\n" /' /start.sh
ENV PYTHONPATH=/usr/local/lib
ENV LD_LIBRARY_PATH=/usr/local/lib
##RUN echo 'export PYTHONPATH=/usr/local/lib' >> /start.sh
##RUN echo 'export LD_LIBRARY_PATH=/usr/local/lib' >> /start.sh

#CMD ["/bin/bash", "-x", "/start.sh"]
USER jovyan
WORKDIR /home/jovyan/SWAN_projects
ENV HOME=/home/jovyan
