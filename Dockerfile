FROM python:3.9
 

# install system dependencies
RUN apt-get update \
    && apt-get -y install gcc make \
    && rm -rf /var/lib/apt/lists/*s


# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable


# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/


RUN apt-get install -y python3 python3-pip
RUN pip3 install selenium
 
RUN python3 --version
RUN pip3 --version
RUN pip install --no-cache-dir --upgrade pip

RUN apt update && apt install tzdata -y
ENV TZ="Europe/Amsterdam"
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y locales && \
    sed -i '/nl_NL.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen && \
    dpkg-reconfigure --frontend=noninteractive locales
ENV LANG nl_NL  
ENV LANGUAGE nl_NL  
ENV LC_ALL nl_NL 

WORKDIR /app

COPY ./requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

COPY scrape-prices.py /app/scrape-prices.py

RUN chmod +x /app/scrape-prices.py

CMD ["python3", "/app/scrape-prices.py"]
