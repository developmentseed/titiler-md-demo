ARG PYTHON_VERSION=3.12

FROM public.ecr.aws/lambda/python:${PYTHON_VERSION}

WORKDIR /tmp

# Install system dependencies to compile (numexpr)
RUN dnf install -y gcc gcc-c++

COPY runtimes/ /tmp/runtimes

# Install dependencies
# HACK: aiobotocore has a tight botocore dependency
# https://github.com/aio-libs/aiobotocore/issues/862
# and becaise we NEED to remove both boto3 and botocore to save space for the package
# we have to force using old package version that seems `almost` compatible with Lambda env botocore
# https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html
RUN pip install --upgrade pip
RUN pip install /tmp/runtimes "mangum>=0.10.0" "aiobotocore==2.13.3" "rasterio==1.3.9" "numpy~=1.0" -t /asset --no-binary pydantic,xarray,numpy,pandas

# Reduce package size and remove useless files
RUN cd /asset && find . -type f -name '*.pyc' | while read f; do n=$(echo $f | sed 's/__pycache__\///' | sed 's/.cpython-[0-9]*//'); cp $f $n; done;
RUN cd /asset && find . -type d -a -name '__pycache__' -print0 | xargs -0 rm -rf
RUN cd /asset && find . -type f -a -name '*.py' -print0 | xargs -0 rm -f
RUN find /asset -type d -a -name 'tests' -print0 | xargs -0 rm -rf
RUN rm -rdf /asset/numpy/doc/ /asset/bin /asset/geos_license /asset/Misc
RUN rm -rdf /asset/boto3*
RUN rm -rdf /asset/botocore*

COPY infrastructure/aws/lambda/handler.py /asset/handler.py

WORKDIR /asset
RUN python -c "from handler import handler; print('All Good')"

CMD ["echo", "hello world"]
