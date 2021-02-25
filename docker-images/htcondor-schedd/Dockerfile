FROM htcondor/submit:8.9.9-el7

RUN yum -y install epel-release httpd mod_wsgi mod_ssl net-tools vim git
RUN systemctl enable httpd

RUN yum -y install python-pip
RUN pip install --upgrade "pip < 21.0" --disable-pip-version-check
RUN pip install git+https://github.com/htcondor/scitokens-credmon

COPY ./scitokens-credmon.wsgi /var/www/wsgi-scripts/scitokens-credmon/
