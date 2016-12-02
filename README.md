# Debris -- autobuild system for debian packages

## Introduction

Debris is a set of scripts that help users to build certain series
of debian packages managed by Git using sbuild and git.

The top git repository contains submodules. Each submodule represents
one debian source package waiting to be built. Debris keeps a sqlite database
to record the past building activities as well as package versions.

## Features

* [ ] Automatically build and generate packages, triggered by crontab or timers
* [ ] Auto update of chroot environment, triggered before build
* [ ] Build and activity log recorded in sqlite3 database

## License

```Copyright 2016, Boyuan Yang <073plan@gmail.com>```

MIT License (Expat)
