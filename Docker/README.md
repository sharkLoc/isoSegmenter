
Installing isochoreFinder using Docker
======================================

Those are instructions on how tu run [isochoreFinder](https://github.com/bunop/isochoreFinder) inside a docker container. First install [docker](http://docs.docker.com/installation/#installation) on your platform. Then you can dowload the pre-build docker image or modify and build a new docker image

## Running isochoreFinder under a pre builded image

You can start a isochoreFinde image simply by typing:

```bash
docker run -ti bunop/isochorefinder /bin/bash
```

This will be enough to get an isochoreFinder running container. You can otionally mount a local directoy inside the running container by adding a local directory as a docker volume. More information can be found inside Docker tutorial on [Managing data in Container](http://docs.docker.com/userguide/dockervolumes/). `isochoreFinder` will be placed under `/opt/isochoreFinder` directory

## Build you own image

Clone isochoreFinder repository from github on your machine, enter in Docker directory and build the docker images. You can modify the image to satisfy your needs. Then you have to run the builded container with the same name you have defined previously.

```bash
$ git clone https://github.com/bunop/isochoreFinder.git
$ cd Docker
$ docker build --rm -t bunop/isochorefinder .
$ docker run -ti bunop/isochorefinder /bin/bash
```

More information can be found on [Docker documentation](http://docs.docker.com/) or on [Working with Docker Images](http://docs.docker.com/userguide/dockerimages/) tutorial