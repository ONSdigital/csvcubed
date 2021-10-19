FROM ruby:3.0.2

RUN apt-get update
RUN apt-get install -y nodejs npm

RUN gem update --system
RUN gem install bundler:2.2.29
RUN gem install middleman
