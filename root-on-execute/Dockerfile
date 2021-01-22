FROM htcondor/execute:8.9.9-el7

USER root

RUN yum install -y git cmake3 gcc-c++ gcc binutils libX11-devel libXpm-devel libXft-devel libXext-devel openssl-devel \
    gcc-gfortran pcre-devel mesa-libGL-devel mesa-libGLU-devel glew-devel ftgl-devel mysql-devel fftw-devel \
    cfitsio-devel graphviz-devel avahi-compat-libdns_sd-devel openldap-devel python-devel python3-devel libxml2-devel \
    gsl-devel python-pip python3-pip && yum clean all && rm -rf /var/cache/yum/* && pip install --upgrade pip && pip install numpy && pip3 install numpy

RUN mkdir /root/root6 
WORKDIR /root/root6
COPY ./root_6.22.0_davix_patched /root/root6/root_source
RUN cmake3 -Dbuiltin_davix=ON /root/root6/root_source
RUN cmake3 --build . --target install -j4
WORKDIR /root

RUN rm -r -f root6

RUN git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git /usr/local/bin/NanoAODTools

WORKDIR /etc/yum.repos.d
RUN wget http://repository.egi.eu/community/software/preview.repository/2.0/releases/repofiles/centos-7-x86_64.repo && wget http://repository.egi.eu/sw/production/cas/1/current/repo-files/EGI-trustanchors.repo && wget http://linuxsoft.cern.ch/wlcg/wlcg-centos7.repo
RUN yum -y install ca-policy-egi-core ca-policy-lcg voms-clients-cpp xrootd-client fetch-crl
RUN fetch-crl -q

WORKDIR /root

RUN echo 'bash /usr/local/bin/NanoAODTools/standalone/env_standalone.sh build' > /etc/profile.d/nanoaodtools.sh
RUN echo 'source /usr/local/bin/NanoAODTools/standalone/env_standalone.sh' >> /etc/profile.d/nanoaodtools.sh
RUN echo 'source /usr/local/bin/thisroot.sh' >> /etc/profile.d/nanoaodtools.sh
RUN chmod -R 777 /usr/local/bin/NanoAODTools

ENV PYTHONPATH=/usr/local/lib
ENV LD_LIBRARY_PATH=/usr/local/lib

CMD ["/bin/bash", "-x", "/start.sh"]
