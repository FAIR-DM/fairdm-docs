# Geoluminate Docs

This repo contains necessary packages and files to build consistent documentation across the Geoluminate apps and projects.

### Install

The following command will add this repo to the dev dependencies of your poetry project:

    poetry add -G dev git+https://github.com/Geoluminate/geoluminate-docs.git 

### Usage

In your docs/conf.py file, add the following lines:

    from docs.conf import *

    # any overrides below here


    <!-- import geoluminate_docs -->
    <!-- geoluminate_docs.setup() -->
