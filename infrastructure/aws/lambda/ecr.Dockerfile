ARG PYTHON_VERSION=3.12

FROM public.ecr.aws/lambda/python:${PYTHON_VERSION} AS builder

WORKDIR /tmp

# Install system dependencies to compile (numexpr)
RUN dnf install -y gcc-c++

COPY runtimes/ /tmp/runtimes

ENV PYTHONUSERBASE=/assets

# Install dependencies
# HACK: aiobotocore has a tight botocore dependency
# https://github.com/aio-libs/aiobotocore/issues/862
# and becaise we NEED to remove both boto3 and botocore to save space for the package
# we have to force using old package version that seems `almost` compatible with Lambda env botocore
# https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html
RUN pip install --upgrade pip
RUN pip install /tmp/runtimes "mangum>=0.10.0" "rasterio==1.3.9" "numpy~=1.0" --user

RUN mv ${PYTHONUSERBASE}/lib/python3.12/site-packages/* ${PYTHONUSERBASE}/
RUN rm -rf ${PYTHONUSERBASE}/lib

# Reduce package size and remove useless files
RUN cd ${PYTHONUSERBASE} && find . -type f -name '*.pyc' | while read f; do n=$(echo $f | sed 's/__pycache__\///' | sed 's/.cpython-[0-9]*//'); cp $f $n; done;
RUN cd ${PYTHONUSERBASE} && find . -type d -a -name '__pycache__' -print0 | xargs -0 rm -rf
RUN cd ${PYTHONUSERBASE} && find . -type f -a -name '*.py' -print0 | xargs -0 rm -f
RUN find ${PYTHONUSERBASE} -type d -a -name 'tests' -print0 | xargs -0 rm -rf
RUN rm -rdf ${PYTHONUSERBASE}/numpy/doc/ ${PYTHONUSERBASE}/bin ${PYTHONUSERBASE}/geos_license ${PYTHONUSERBASE}/Misc
RUN rm -rdf ${PYTHONUSERBASE}/boto3*
RUN rm -rdf ${PYTHONUSERBASE}/botocore*

FROM public.ecr.aws/lambda/python:${PYTHON_VERSION} AS lambda
ENV PYTHONUSERBASE=/assets
COPY --from=builder ${PYTHONUSERBASE} ${LAMBDA_TASK_ROOT}
COPY infrastructure/aws/lambda/handler.py ${LAMBDA_TASK_ROOT}/handler.py

RUN python -c "from handler import handler; print('All Good')"

CMD [ "handler.handler" ]
