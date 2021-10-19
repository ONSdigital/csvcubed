FROM ruby:3.0.2-alpine

RUN apk update
RUN apk add nodejs
RUN apk add npm

# Install build-base to support native compilation of middleman
RUN apk add build-base

# Maybe this will help sort build permissions out?
RUN su

RUN gem install middleman