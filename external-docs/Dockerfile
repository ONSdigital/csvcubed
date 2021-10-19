FROM ruby:3.0.2-alpine

RUN apk update
RUN apk add nodejs
RUN apk add npm

# Install build-base to support native compilation of middleman
RUN apk add build-base
RUN gem install middleman