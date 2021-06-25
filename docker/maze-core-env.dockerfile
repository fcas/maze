# syntax=docker/dockerfile:1.2
# Builds image maze_core_env.
# See https://uwekorn.com/2021/03/01/deploying-conda-environments-in-docker-how-to-do-it-right.html for a description of
# some of the measures implemented to reduce build size and duration.

ARG BASE_IMAGE="condaforge/mambaforge:4.9.2-5"

###################################################
# Image for conda/mamba environment building.
###################################################

FROM condaforge/mambaforge:4.10.1-0 as maze_core_env_build

# build-arg for optional pip installs.
ARG opt_pip_installs
ARG BUILD_VERSION

RUN echo "BUILD_VERSION: $BUILD_VERSION"

# Install environment.
COPY maze-core-environment.yml .
RUN --mount=type=cache,target=/opt/conda/pkgs mamba env create -p /env --file maze-core-environment.yml
RUN echo "conda activate /env" >> /root/.bashrc
ENV PATH /env/bin:$PATH

# Install optional dependencies.
RUN if [ -n "$opt_pip_installs" ] ; then pip install $(echo $opt_pip_installs | tr ',' ' ') ; else : ; fi

# Clean up conda environment.
RUN find -name '*.a' -delete && \
    find -name '__pycache__' -type d -exec rm -rf '{}' '+' && \
    rm -rf /env/lib/python3.7/idlelib /env/lib/python3.7/ensurepip \
    /env/lib/libasan.so.5.0.0 \
    /env/lib/libtsan.so.0.0.0 \
    /env/lib/liblsan.so.0.0.0 \
    /env/lib/libubsan.so.1.0.0 \
    /env/bin/x86_64-conda-linux-gnu-ld \
    /env/bin/sqlite3 \
    /env/bin/openssl \
    /env/share/terminfo && \
    find /env/lib/python3.7/site-packages -name '*.pyx' -delete

###################################################
# Image for built, clean environment.
###################################################

FROM ${BASE_IMAGE} as maze_core_env

# Install system dependencies and Maze.
RUN apt-get update && \
    apt-get install -y xvfb htop redis-server python-opengl build-essential g++ && \
    rm -rf /var/lib/apt/lists/*

# Copy conda environment.
ENV CONDA_ENVS_PATH=/
ENV PATH /env/bin:$PATH
COPY --from=maze_core_env_build /env /env
COPY --from=maze_core_env_build /root/.bashrc /root/
