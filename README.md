# FairDM Documentation Tools

This repository contains tools and packages that help build consistent documentation throughout the FairDM ecosystem.

### Install

The following command will add this repo to the dev dependencies of your poetry project:

    poetry add -G dev git+https://github.com/FAIR-DM/fairdm-docs 

### Usage

In your docs/conf.py file, add the following lines:

    from docs.conf import *

    # any overrides below here


    <!-- import fairdm_docs -->
    <!-- geoluminate_docs.setup() -->
